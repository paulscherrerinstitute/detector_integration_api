from enum import Enum
from logging import getLogger

from detector_integration_api.utils import ClientDisableWrapper

_logger = getLogger(__name__)


class IntegrationStatus(Enum):
    INITIALIZED = "initialized",
    CONFIGURED = "configured",
    RUNNING = "running",
    DETECTOR_STOPPED = "detector_stopped",
    FINISHED = "finished"
    ERROR = "error"


MANDATORY_WRITER_CONFIG_PARAMETERS = ["n_frames", "user_id", "output_file"]
MANDATORY_BACKEND_CONFIG_PARAMETERS = ["bit_depth", "n_frames"]
MANDATORY_DETECTOR_CONFIG_PARAMETERS = ["period", "frames", "dr"]

CSAXS_FORMAT_INPUT_PARAMETERS = {
    "sl2wv": float,
    "sl0ch": float,
    "sl2wh": float,
    "temp_mono_cryst_1": float,
    "harmonic": int,
    "mokev": float,
    "sl2cv": float,
    "bpm4_gain_setting": float,
    "mirror_coating": str,
    "samx": float,
    "sample_name": str,
    "bpm5y": float,
    "sl2ch": float,
    "curr": float,
    "bs2_status": str,
    "bs2y": float,
    "diode": float,
    "samy": float,
    "sl4ch": float,
    "sl4wh": float,
    "temp_mono_cryst_2": float,
    "sl3wh": float,
    "mith": float,
    "bs1_status": str,
    "bpm4s": float,
    "sl0wh": float,
    "bpm6z": float,
    "bs1y": float,
    "scan": str,
    "bpm5_gain_setting": float,
    "bpm4z": float,
    "bpm4x": float,
    "date": str,
    "mibd": float,
    "temp": float,
    "idgap": float,
    "sl4cv": float,
    "sl1wv": float,
    "sl3wv": float,
    "sl1ch": float,
    "bs2x": float,
    "bpm6_gain_setting": float,
    "bpm4y": float,
    "bpm6s": float,
    "sample_description": str,
    "bpm5z": float,
    "moth1": float,
    "sec": float,
    "sl3cv": float,
    "bs1x": float,
    "bpm6_saturation_value": float,
    "bpm5s": float,
    "mobd": float,
    "sl1wh": float,
    "sl4wv": float,
    "bs2_det_dist": float,
    "bpm5_saturation_value": float,
    "fil_comb_description": str,
    "bpm5x": float,
    "bpm4_saturation_value": float,
    "bs1_det_dist": float,
    "sl3ch": float,
    "bpm6y": float,
    "sl1cv": float,
    "bpm6x": float,
    "ftrans": float,
    "samz": float
}


def validate_writer_config(configuration):
    if not configuration:
        raise ValueError("Writer configuration cannot be empty.")

    writer_cfg_params = MANDATORY_WRITER_CONFIG_PARAMETERS + list(CSAXS_FORMAT_INPUT_PARAMETERS.keys())

    # Check if all mandatory parameters are present.
    if not all(x in configuration for x in writer_cfg_params):
        missing_parameters = [x for x in writer_cfg_params if x not in configuration]
        raise ValueError("Writer configuration missing mandatory parameters: %s" % missing_parameters)

    unexpected_parameters = [x for x in configuration.keys() if x not in writer_cfg_params]
    if unexpected_parameters:
        raise ValueError("Received unexpected parameters for writer: %s" % unexpected_parameters)

    # Check if all format parameters are of correct type.
    wrong_parameter_types = ""
    for parameter_name, parameter_type in CSAXS_FORMAT_INPUT_PARAMETERS.items():
        if not isinstance(configuration[parameter_name], parameter_type):
            wrong_parameter_types += "\tWriter parameter '%s' expected of type '%s', but received of type '%s'.\n" % \
                                     (parameter_name, parameter_type, type(configuration[parameter_name]))

    if wrong_parameter_types:
        raise ValueError("Received parameters of invalid type:\n%s", wrong_parameter_types)

    # Check if the filename ends with h5.
    if configuration["output_file"][-3:] != ".h5":
        configuration["output_file"] += ".h5"


def validate_backend_config(configuration):
    if not configuration:
        raise ValueError("Backend configuration cannot be empty.")

    if not all(x in configuration for x in MANDATORY_BACKEND_CONFIG_PARAMETERS):
        missing_parameters = [x for x in MANDATORY_BACKEND_CONFIG_PARAMETERS if x not in configuration]
        raise ValueError("Backend configuration missing mandatory parameters: %s" % missing_parameters)


def validate_detector_config(configuration):
    if not configuration:
        raise ValueError("Detector configuration cannot be empty.")

    if not all(x in configuration for x in MANDATORY_DETECTOR_CONFIG_PARAMETERS):
        missing_parameters = [x for x in MANDATORY_DETECTOR_CONFIG_PARAMETERS if x not in configuration]
        raise ValueError("Detector configuration missing mandatory parameters: %s" % missing_parameters)


def validate_configs_dependencies(writer_config, backend_config, detector_config):
    if backend_config["bit_depth"] != detector_config["dr"]:
        raise ValueError("Invalid config. Backend 'bit_depth' set to '%s', but detector 'dr' set to '%s'."
                         " They must be equal."
                         % (backend_config["bit_depth"], detector_config["dr"]))

    if backend_config["n_frames"] != detector_config["frames"]:
        raise ValueError("Invalid config. Backend 'n_frames' set to '%s', but detector 'frames' set to '%s'. "
                         "They must be equal." % (backend_config["n_frames"], detector_config["frames"]))

    if writer_config["n_frames"] != backend_config["n_frames"]:
        raise ValueError("Invalid config. Backend 'n_frames' set to '%s', but writer 'n_frames' set to '%s'. "
                         "They must be equal." % (backend_config["n_frames"], writer_config["n_frames"]))


def interpret_status(statuses):
    _logger.debug("Interpreting statuses: %s", statuses)

    writer = statuses["writer"]
    backend = statuses["backend"]
    detector = statuses["detector"]

    def cmp(status, expected_value):

        _logger.debug("Comparing status '%s' with expected status '%s'.", status, expected_value)

        if status == ClientDisableWrapper.STATUS_DISABLED:
            return True

        if isinstance(expected_value, (tuple, list)):
            return status in expected_value
        else:
            return status == expected_value

    # If no other conditions match.
    interpreted_status = IntegrationStatus.ERROR

    # Dia after reset.
    if cmp(writer, "stopped") and cmp(detector, "idle") and cmp(backend, "INITIALIZED"):
        interpreted_status = IntegrationStatus.INITIALIZED

    elif cmp(writer, "stopped") and cmp(detector, "idle") and cmp(backend, "CONFIGURED"):
        interpreted_status = IntegrationStatus.CONFIGURED

    elif cmp(writer, ("receiving", "writing")) and cmp(detector, ("running", "waiting")) and cmp(backend, "OPEN"):
        interpreted_status = IntegrationStatus.RUNNING

    elif cmp(writer, ("receiving", "writing")) and cmp(detector, "idle") and cmp(backend, "OPEN"):
        interpreted_status = IntegrationStatus.DETECTOR_STOPPED

    elif cmp(writer, ("finished", "stopped")) and cmp(detector, "idle") and cmp(backend, "OPEN"):
        interpreted_status = IntegrationStatus.FINISHED

    _logger.debug("Statuses interpreted as '%s'.", interpreted_status)

    return interpreted_status
