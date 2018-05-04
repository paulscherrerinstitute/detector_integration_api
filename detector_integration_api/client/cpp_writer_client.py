import os.path
import requests
import json

from subprocess import Popen
from datetime import datetime
from logging import getLogger
from time import sleep

from detector_integration_api import config

_logger = getLogger(__name__)


class CppWriterClient(object):
    PROCESS_STARTUP_PARAMETERS = ("output_file", "n_frames", "user_id")

    def __init__(self, stream_url, writer_executable, writer_port, log_folder=None):

        self.stream_url = stream_url
        self.writer_executable = writer_executable
        self.writer_port = writer_port

        self.log_folder = None
        if log_folder is not None:

            if not os.path.exists(log_folder):
                raise ValueError("Provided writer log folder '%s' does not exist." % log_folder)

            self.log_folder = log_folder

        self.writer_url = config.WRITER_PROCESS_URL_FORMAT % writer_port
        self.writer_parameters = None

        self.process = None
        self.process_log_file = None

    def _sanitize_parameters(self, parameters):
        return {key: parameters[key] for key in parameters if key not in self.PROCESS_STARTUP_PARAMETERS}

    def _send_request_to_process(self, requests_method, url, request_json=None, return_response=False):
        for _ in range(config.WRITER_PROCESS_RETRY_N):

            try:
                response = requests_method(url=url, json=request_json,
                                           timeout=config.WRITER_PROCESS_COMMUNICATION_TIMEOUT)

                if response.status_code != 200:
                    _logger.debug("Error while trying to communicate with the writer. Retrying.", response)

                    sleep(config.WRITER_PROCESS_RETRY_DELAY)
                    continue

                if return_response:
                    return response
                else:
                    return True

            except:
                sleep(config.WRITER_PROCESS_RETRY_DELAY)

        return False

    def start(self):

        if self.is_running():
            raise RuntimeError("Writer process already running. Cannot start new one until old one is still alive.")

        if not self.writer_parameters:
            raise ValueError("Writer parameters not set.")

        timestamp = datetime.now().strftime(config.WRITER_PROCESS_LOG_FILENAME_TIME_FORMAT)

        # If the log folder is not specified, redirect the logs to /dev/null.
        if self.log_folder is not None:
            log_filename = os.path.join(self.log_folder,
                                        config.WRITER_PROCESS_LOG_FILENAME_FORMAT % timestamp)
        else:
            log_filename = os.devnull

        _logger.debug("Creating log file '%s'.", log_filename)
        self.process_log_file = open(log_filename, 'w')
        self.process_log_file.write("Parameters:\n%s\n" % json.dumps(self.writer_parameters, indent=4))
        self.process_log_file.flush()

        writer_command_format = "sh " + self.writer_executable + " %s %s %s %s %s"
        writer_command = writer_command_format % (self.stream_url,
                                                  self.writer_parameters["output_file"],
                                                  self.writer_parameters.get("n_frames", 0),
                                                  self.writer_port,
                                                  self.writer_parameters.get("user_id", -1))

        _logger.debug("Starting writer with command '%s'.", writer_command)
        self.process = Popen(writer_command, shell=True, stdout=self.process_log_file, stderr=self.process_log_file)

        sleep(config.WRITER_PROCESS_STARTUP_WAIT_TIME)

        process_parameters = self._sanitize_parameters(self.writer_parameters)
        _logger.debug("Setting process parameters: %s", process_parameters)

        if not self._send_request_to_process(requests.post, self.writer_url + "/parameters",
                                             request_json=process_parameters):
            _logger.warning("Terminating writer process because it did not respond in the specified time.")
            self._kill()

            raise RuntimeError("Count not start writer process in time. Check writer logs.")

    def _kill(self):
        _logger.warning("Terminating writer. Data files might be corrupted.")

        self._send_request_to_process(requests.get, self.writer_url + "/kill")

        try:
            self.process.wait(timeout=config.WRITER_PROCESS_TERMINATE_TIMEOUT)
        except:
            self.process.terminate()

        if self.process_log_file:
            self.process_log_file.flush()
            self.process_log_file.close()

    def stop(self):

        _logger.debug("Stopping writer.")

        if self.is_running():
            _logger.debug("Sending stop command to the writer.")

            if not self._send_request_to_process(requests.get, self.writer_url + "/stop"):
                if self.is_running():
                    raise ValueError("Writer is running but cannot send stop command.")

            try:
                self.process.wait(timeout=config.WRITER_PROCESS_TERMINATE_TIMEOUT)
            except:
                error_message = "Process termination timeout exceeded for writer. Killing."
                _logger.warning(error_message)

                self._kill()

                raise RuntimeError(error_message)
        else:
            _logger.debug("Writer process is not running.")

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
                                                   self.writer_url + "/status",
                                                   return_response=True).json()

        if status is False:
            if self.is_running():
                raise ValueError("Writer is running but cannot get status.")
            else:
                return "stopped"

        return status["status"]

    def set_parameters(self, writer_parameters):
        self.writer_parameters = writer_parameters

    def reset(self):
        _logger.debug("Resetting writer.")

        self.stop()

        self.writer_parameters = None

    def get_statistics(self):

        if not self.is_running():
            return {}

        statistics = self._send_request_to_process(requests.get,
                                                   self.writer_url + "/statistics",
                                                   return_response=True).json()

        if statistics is False:
            if self.is_running():
                raise ValueError("Writer is running but cannot get statistics.")
            else:
                return {}

        return statistics
