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
MANDATORY_DETECTOR_CONFIG_PARAMETERS = ["period", "frames", "dr", "exptime"]


def validate_writer_config(configuration):
    if not configuration:
        raise ValueError("Writer configuration cannot be empty.")

    writer_cfg_params = MANDATORY_WRITER_CONFIG_PARAMETERS

    # Check if all mandatory parameters are present.
    if not all(x in configuration for x in writer_cfg_params):
        missing_parameters = [x for x in writer_cfg_params if x not in configuration]
        raise ValueError("Writer configuration missing mandatory parameters: %s" % missing_parameters)


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
