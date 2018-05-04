import os.path
import requests
import json

from subprocess import Popen
from datetime import datetime
from logging import getLogger
from time import sleep

from detector_integration_api import config

_logger = getLogger(__name__)


class ExternalProcessClient(object):
    PROCESS_STARTUP_PARAMETERS = ()
    PROCESS_NAME = "unknown"

    def __init__(self, stream_url, writer_executable, writer_port, log_folder=None):

        self.stream_url = stream_url
        self.process_executable = writer_executable
        self.process_port = writer_port

        self.log_folder = None
        if log_folder is not None:

            if not os.path.exists(log_folder):
                raise ValueError("Provided %s log folder for process '%s' does not exist."
                                 % (self.PROCESS_NAME, log_folder))

            self.log_folder = log_folder

        self.process_url = config.EXTERNAL_PROCESS_URL_FORMAT % writer_port
        self.process_parameters = None

        self.process = None
        self.process_log_file = None

    def _sanitize_parameters(self, parameters):
        return {key: parameters[key] for key in parameters if key not in self.PROCESS_STARTUP_PARAMETERS}

    def _send_request_to_process(self, requests_method, url, request_json=None, return_response=False):
        for _ in range(config.EXTERNAL_PROCESS_RETRY_N):

            try:
                response = requests_method(url=url, json=request_json,
                                           timeout=config.EXTERNAL_PROCESS_COMMUNICATION_TIMEOUT)

                if response.status_code != 200:
                    _logger.debug("Error while trying to communicate with the %s process. Retrying." %
                                  self.PROCESS_NAME, response)

                    sleep(config.EXTERNAL_PROCESS_RETRY_DELAY)
                    continue

                if return_response:
                    return response
                else:
                    return True

            except:
                sleep(config.EXTERNAL_PROCESS_RETRY_DELAY)

        return False

    def get_execution_command(self):
        return self.process_executable

    def start(self):

        if self.is_running():
            raise RuntimeError("Process %s already running. Cannot start new one until old one is still alive."
                               % self.PROCESS_NAME)

        if not self.process_parameters:
            raise ValueError("Process %s parameters not set." % self.PROCESS_NAME)

        timestamp = datetime.now().strftime(config.EXTERNAL_PROCESS_LOG_FILENAME_TIME_FORMAT)

        # If the log folder is not specified, redirect the logs to /dev/null.
        if self.log_folder is not None:
            log_filename = os.path.join(self.log_folder,
                                        config.EXTERNAL_PROCESS_LOG_FILENAME_FORMAT % timestamp)
        else:
            log_filename = os.devnull

        _logger.debug("Creating log file '%s'.", log_filename)
        self.process_log_file = open(log_filename, 'w')
        self.process_log_file.write("Parameters:\n%s\n" % json.dumps(self.process_parameters, indent=4))
        self.process_log_file.flush()

        process_command = self.get_execution_command()

        _logger.debug("Starting process %s with command '%s'.", self.PROCESS_NAME, process_command)
        self.process = Popen(process_command, shell=True, stdout=self.process_log_file, stderr=self.process_log_file)

        sleep(config.EXTERNAL_PROCESS_STARTUP_WAIT_TIME)

        process_parameters = self._sanitize_parameters(self.process_parameters)
        _logger.debug("Setting process %s parameters: %s", self.PROCESS_NAME, process_parameters)

        if not self._send_request_to_process(requests.post, self.process_url + "/parameters",
                                             request_json=process_parameters):
            _logger.warning("Terminating %s process because it did not respond in the specified time." %
                            self.PROCESS_NAME)
            self._kill()

            raise RuntimeError("Could not start %s process in time. Check writer logs." % self.PROCESS_NAME)

    def _kill(self):
        _logger.warning("Terminating process %s. Data files might be corrupted." % self.PROCESS_NAME)

        self._send_request_to_process(requests.get, self.process_url + "/kill")

        try:
            self.process.wait(timeout=config.EXTERNAL_PROCESS_TERMINATE_TIMEOUT)
        except:
            self.process.terminate()

        if self.process_log_file:
            self.process_log_file.flush()
            self.process_log_file.close()

    def stop(self):

        _logger.debug("Stopping process %s." % self.PROCESS_NAME)

        if self.is_running():
            _logger.debug("Sending stop command to the process %s." % self.PROCESS_NAME)

            if not self._send_request_to_process(requests.get, self.process_url + "/stop"):
                if self.is_running():
                    raise ValueError("Process %s is running but cannot send stop command." % self.PROCESS_NAME)

            try:
                self.process.wait(timeout=config.EXTERNAL_PROCESS_TERMINATE_TIMEOUT)
            except:
                error_message = "Process %s termination timeout exceeded. Killing." % self.PROCESS_NAME
                _logger.warning(error_message)

                self._kill()

                raise RuntimeError(error_message)
        else:
            _logger.debug("Process %s is not running.", self.PROCESS_NAME)

        if self.process_log_file:
            self.process_log_file.flush()
            self.process_log_file.close()

        self.process = None
        self.process_log_file = None

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def get_status(self):

        if self.is_running():
            status = self._send_request_to_process(requests.get,
                                                   self.process_url + "/status",
                                                   return_response=True).json()

        if status is False:
            if self.is_running():
                raise ValueError("Process %s is running but cannot get status." % self.PROCESS_NAME)
            else:
                return "stopped"

        return status["status"]

    def set_parameters(self, writer_parameters):
        self.process_parameters = writer_parameters

    def reset(self):
        _logger.debug("Resetting process %s.", self.PROCESS_NAME)

        self.stop()

        self.process_parameters = None

    def get_statistics(self):

        if not self.is_running():
            return {}

        statistics = self._send_request_to_process(requests.get,
                                                   self.process_url + "/statistics",
                                                   return_response=True).json()

        if statistics is False:
            if self.is_running():
                raise ValueError("Process %s is running but cannot get statistics." % self.PROCESS_NAME)
            else:
                return {}

        return statistics
