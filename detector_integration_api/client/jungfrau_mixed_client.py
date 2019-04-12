import subprocess

from logging import getLogger
from numbers import Number

from sls_detector import Eiger, Jungfrau

_logger = getLogger(__name__)


class DetectorClient(object):

    TASK_SET = ["taskset", "-c", "0"]

    def __init__(self, id=0, use_taskset=True):
        self.detector = Jungfrau(id)

        self.detector_id = "" if id == 0 else str(id)+"-"
        self.use_taskset = use_taskset

    def start(self):
 
        self.detector.start_detector() 

        status = self.detector.status
        self.verify_response_data2(self.detector_id+'start-status', ["idle", "running", "waiting"], status)

        #cli_command = ["sls_detector_put", self.detector_id + "status", "start"]

        #if self.use_taskset:
        #    cli_command = self.TASK_SET + cli_command

        #_logger.debug("Executing start command: '%s'.", " ".join(cli_command))

        #cli_result = subprocess.check_output(cli_command)
        #response, received_parameter_name, received_value = self.interpret_response(cli_result, "status")
        # The status can also be 'idle', for single image short exptime acquisitions.
        #self.verify_response_data(response, self.detector_id+"status", received_parameter_name, ["idle", "running", "waiting"],
        #                          received_value)

    def stop(self):

        self.detector.stop_detector()

        status = self.detector.status
        self.verify_response_data2(self.detector_id+'stop-status', ["idle", "running", "waiting"], status)

        #cli_command = ["sls_detector_put", self.detector_id + "status", "stop"]

        #if self.use_taskset:
        #    cli_command = self.TASK_SET + cli_command

        #_logger.debug("Executing start command: '%s'.", " ".join(cli_command))

        #cli_result = subprocess.check_output(cli_command)
        #response, received_parameter_name, received_value = self.interpret_response(cli_result, "status")
        #self.verify_response_data(response, self.detector_id+"status", received_parameter_name, "idle", received_value)

    def get_status(self):
 
        raw_status = self.detector.status
        return raw_status
        #try:
        #    raw_status = self.get_value("status")
        #except:
            #WIP: will be different anyway with python client to communicate with detector, currently sometime (~1/x0000) _get 2-status returns "Undefined function"
        #    _logger.debug("Got error while asking for the status, there may be because of known rare bug in cli, so we try once more")
        #    raw_status = self.get_value("status")
        #return raw_status

    def get_value(self, parameter_name):
#TODO: replace by enumarate
        if parameter_name == "exptime":
            return self.detector.exposure_time
        elif parameter_name == "frames":
            return self.detector.n_frames
        elif parameter_name == "cycles":
            return self.detector.n_cycles
        elif parameter_name == "timing":
            return self.detector.timing_mode
        elif parameter_name == "period":
            return self.detector.period
        elif parameter_name == "status":
            return self.detector.status
        elif parameter_name == "dr":
            return self.detector.dynamic_range
        elif parameter_name == "vhighvoltage":
            return self.detector.high_voltage
        else:
            _logger.debug("get_value called with deprecated name : %s " % parameter_name)
            return self.get_value_cli(parameter_name)

    def get_value_cli(self, parameter_name):

        _logger.debug("CLIVERSION get called. Paramters :%s" % parameter_name)

        cli_command = ["sls_detector_get", self.detector_id + parameter_name]

        if self.use_taskset:
            cli_command = self.TASK_SET + cli_command

        _logger.debug("Executing get command: '%s'.", " ".join(cli_command))

        cli_result = subprocess.check_output(cli_command)
        return self.validate_response(cli_result, self.detector_id+parameter_name)

    def set_value(self, parameter_name, value, no_verification=False):

        _logger.debug("Will set parameter %s to %s for detector %s." % (parameter_name, value, self.detector_id))
#TODO: replace by enumarate
        if parameter_name == "exptime":
            self.detector.exposure_time = value
            return self.detector.exposure_time
        elif parameter_name == "frames":
            self.detector.n_frames = value
            return self.detector.n_frames
        elif parameter_name == "cycles":
            self.detector.n_cycles = value
            return self.detector.n_cycles
        elif parameter_name == "timing":
            self.detector.timing_mode = value
            return self.detector.timing_mode
        elif parameter_name == "period":
            self.detector.period = value
            return self.detector.period
        elif parameter_name == "dr":
            self.detector.dynamic_range = value # fobid to change dr?
            return self.detector.dynamic_range
        elif parameter_name == "settings":
            _logger.debug("Switching detector %s to %s." % (self.detector_id, value))
            self.detector.settings = value # 
            return self.detector.settings
        elif parameter_name == "clearbit":
#TODO remove completely possibility to manipulate with bits, instead Detector.settings=
            if len(value.split()) == 2:
                self.detector._api.clearBitInRegister(int(value.split()[0],16), int(value.split()[1]))
            else:
                raise RuntimeError("Wrong parameters for clearbit (%s) : %s." % (parameter_name, value))
        elif parameter_name == "setbit":
#TODO remove completely possibility to manipulate with bits, instead Detector.settings=
            if len(value.split()) == 2:
                self.detector._api.setBitInRegister(int(value.split()[0],16), int(value.split()[1]))
            else:
                raise RuntimeError("Wrong parameters for setbit (%s) : %s." % (parameter_name, value))
        else:
            _logger.debug("set_value called with deprecated name : %s (value: %s)." % (parameter_name, value))
            return self.set_value_cli(parameter_name, value, no_verification)

    def set_value_cli(self, parameter_name, value, no_verification=False):

        _logger.debug("CLIVERSION set called. Paramters :%s, value : %s" % (parameter_name, value)) 

        if isinstance(value, str):
            cli_command = ["sls_detector_put", self.detector_id + parameter_name, ] + list(map(str, value.split()))
        else:
            cli_command = ["sls_detector_put", self.detector_id + parameter_name, str(value)]

        if self.use_taskset:
            cli_command = self.TASK_SET + cli_command

        _logger.debug("Executing put command: '%s'.", " ".join(cli_command))

        try:
            cli_result = subprocess.check_output(cli_command)

            # This is to be used only when user interact manually with the detector.
            if no_verification:
                return cli_result.decode("utf-8")
            else:
                return self.validate_response(cli_result, self.detector_id + parameter_name)

        except:
            raise RuntimeError("Cannot execute detector command %s, please check the detector" % cli_command)

    def set_config(self, configuration):
        for name, value in configuration.items():
            self.set_value(name, value)

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

            if not isinstance(expected_value, list):
                expected_value = [expected_value]

            if isinstance(expected_value[0], Number):
                received_value = float(received_value)

            if received_value not in expected_value:
                raise ValueError("Invalid parameter '%s' value, expected '%s' but received '%s': %s"
                                 % (expected_parameter_name, expected_value, received_value, response))

        return received_value

    @staticmethod
    def verify_response_data2(name, expected_value, received_value):
        if expected_value is not None:

            if not isinstance(expected_value, list):
                expected_value = [expected_value]

            if isinstance(expected_value[0], Number):
                received_value = float(received_value)

            if received_value not in expected_value:
                raise ValueError("Invalid parameter '%s' value, expected '%s' but received '%s'"
                                 % (name, expected_value, received_value))

        return received_value

    @staticmethod
    def validate_response(output_bytes, parameter_name, value=None):

        response, received_parameter_name, received_value = DetectorClient.interpret_response(output_bytes,
                                                                                              parameter_name)

        return DetectorClient.verify_response_data(response, parameter_name, received_parameter_name,
                                                   value, received_value)
