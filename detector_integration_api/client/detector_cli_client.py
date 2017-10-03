import subprocess

from logging import getLogger
from numbers import Number

_logger = getLogger(__name__)


class DetectorClient(object):
    def start(self):
        cli_command = ["sls_detector_put", "status", "start"]
        _logger.debug("Executing start command: '%s'.", " ".join(cli_command))

        cli_result = subprocess.check_output(cli_command)
        response, received_parameter_name, received_value = self.interpret_response(cli_result, "status")
        self.verify_response_data(response, "status", received_parameter_name, "running", received_value)

    def stop(self):
        cli_command = ["sls_detector_put", "status", "stop"]
        _logger.debug("Executing start command: '%s'.", " ".join(cli_command))

        cli_result = subprocess.check_output(cli_command)
        response, received_parameter_name, received_value = self.interpret_response(cli_result, "status")
        self.verify_response_data(response, "status", received_parameter_name, "running", received_value)

    def get_status(self):
        raw_status = self._get("status")
        return raw_status

    def _get(self, parameter_name):
        cli_command = ["sls_detector_get", parameter_name]
        _logger.debug("Executing get command: '%s'.", " ".join(cli_command))

        cli_result = subprocess.check_output(cli_command)
        return self.validate_response(cli_result, parameter_name)

    def _put(self, parameter_name, value):
        cli_command = ["sls_detector_put", parameter_name, value]
        _logger.debug("Executing put command: '%s'.", " ".join(cli_command))

        cli_result = subprocess.check_output(cli_command)
        return self.validate_response(cli_result, parameter_name)

    def set_config(self, configuration):
        for name, value in configuration.items():
            self._put(name, value)

    @staticmethod
    def interpret_response(output_bytes, parameter_name):
        response = output_bytes.decode("utf-8")

        if not response:
            raise ValueError("Response is empty.")

        # Only the last line is the real output. The rest are usually warning etc.
        last_output_line = response.splitlines()[-1]
        output_parameters = last_output_line.split(" ")

        # The output is usually in format: parameter_name parameter_value
        if len(output_parameters) != 2:
            raise ValueError("Response for parameter '%s' not in expected format: %s" % (parameter_name, response))

        return response, output_parameters[0], output_parameters[1]

    @staticmethod
    def verify_response_data(response,
                             expected_parameter_name, received_parameter_name,
                             expected_value, received_value):

        # The returned parameter name must be the same as the requested.
        if received_parameter_name != expected_parameter_name:
            raise ValueError("Invalid parameter_name '%s' when requested parameter was '%s': %s" %
                             (received_parameter_name, expected_parameter_name, response))

        # The returned expected_value must be the same as the set expected_value.
        if expected_value is not None:
            if isinstance(expected_value, Number):
                received_value = float(received_value)

            if received_value != expected_value:
                raise ValueError("Invalid parameter '%s' value, set '%s' but received '%s': %s"
                                 % (expected_parameter_name, expected_value, received_value, response))

        return received_value

    @staticmethod
    def validate_response(output_bytes, parameter_name, value=None):

        response, received_parameter_name, received_value = DetectorClient.interpret_response(output_bytes,
                                                                                              parameter_name)

        return DetectorClient.verify_response_data(response, parameter_name, received_parameter_name,
                                                   value, received_value)
