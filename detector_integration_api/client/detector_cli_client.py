import subprocess

from logging import getLogger

_logger = getLogger(__name__)


class DetectorClient(object):
    def start(self):
        cli_result = self._set("status", "start")

        return cli_result

    def stop(self):
        cli_result = self._set("status", "stop")

        return cli_result

    def get_status(self):
        raw_status = self._get("status")
        return raw_status

    def _get(self, parameter_name):
        cli_command = ["sls_detector_get", parameter_name]
        _logger.debug("Executing get command: '%s'.", " ".join(cli_command))

        cli_result = subprocess.check_output(cli_command)
        # TODO: Validate cli_result
        return cli_result.decode("utf-8").rstrip()

    def _put(self, parameter_name, value):
        cli_command = ["sls_detector_put", parameter_name, value]
        _logger.debug("Executing put command: '%s'.", " ".join(cli_command))

        cli_result = subprocess.check_output(cli_command)
        # TODO: Validate cli_result
        return cli_result.decode("utf-8").rstrip()

    def set_config(self, configuration):
        for name, value in configuration.items():
            self._put(name, value)