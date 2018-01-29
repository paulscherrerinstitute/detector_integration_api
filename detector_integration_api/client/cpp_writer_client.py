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

    def __init__(self, stream_url, writer_port):

        self.writer_port = writer_port
        self.url = config.WRITER_PROCESS_URL_FORMAT % writer_port
        self.stream_url = stream_url

        self.writer_parameters = None

        self.process = None
        self.process_log_file = None

    @staticmethod
    def _sanitize_parameters(parameters):

        return {key: parameters[key] for key in parameters if key not in CppWriterClient.PROCESS_STARTUP_PARAMETERS}

    def start(self):

        if self.is_running():
            raise RuntimeError("Writer process already running. Cannot start new one until old one is still alive.")

        if not self.writer_parameters:
            raise ValueError("Writer parameters not set.")

        timestamp = datetime.now().strftime(config.WRITER_PROCESS_LOG_FILENAME_TIME_FORMAT)
        log_filename = os.path.join(config.WRITER_PROCESS_LOG_DIR, config.WRITER_PROCESS_LOG_FILENAME_FORMAT % timestamp)

        writer_command_format = "sh /home/dia/start_writer.sh %s %s %s %s %s"
        writer_command = writer_command_format % (self.stream_url,
                                                  self.writer_parameters["output_file"],
                                                  self.writer_parameters.get("n_frames", 0),
                                                  self.writer_port,
                                                  self.writer_parameters.get("user_id", -1))
        _logger.debug("Starting writer with command '%s'.", writer_command)

        _logger.debug("Creating log file '%s'.", log_filename)
        self.process_log_file = open(log_filename, 'w')
        self.process_log_file.write("Parameters:\n%s\n" % json.dumps(self.writer_parameters, indent=4))
        self.process_log_file.flush()

        self.process = Popen(writer_command, shell=True, stdout=self.process_log_file, stderr=self.process_log_file)

        sleep(config.WRITER_PROCESS_STARTUP_WAIT_TIME)

        process_parameters = self._sanitize_parameters(self.writer_parameters)

        _logger.debug("Setting process parameters: %s", process_parameters)

        response = requests.post(self.url + "/parameters", json=process_parameters)

    def stop(self):

        _logger.debug("Stopping writer.")

        if self.is_running():
            requests.get(self.url + "/stop")
            self.process.wait()

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

        # Writer is running. Get status from the process.
        if self.is_running():
            status = requests.get(self.url + "/status").json()

            return status["status"]

        return "stopped"

    def set_parameters(self, writer_parameters):

        self.writer_parameters = writer_parameters

    def reset(self):

        _logger.debug("Resetting writer.")

        self.stop()

        self.writer_parameters = None

    def get_statistics(self):

        if not self.is_running():
            raise RuntimeError("Process is not running. Cannot get statistics.")

        return requests.get(self.url + "/statistics").json()
