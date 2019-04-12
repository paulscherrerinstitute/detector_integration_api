from logging import getLogger

from detector_integration_api.utils import compare_client_status
from detector_integration_api.default_validator import IntegrationStatus

_logger = getLogger(__name__)


MANDATORY_WRITER_CONFIG_PARAMETERS = ["n_frames", "user_id", "output_file"]
MANDATORY_BACKEND_CONFIG_PARAMETERS = ["bit_depth"]
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

    # If no other conditions match.
    interpreted_status = IntegrationStatus.ERROR

    if compare_client_status(writer, "stopped"):
        interpreted_status = IntegrationStatus.READY

    elif compare_client_status(writer, "writing"):
        interpreted_status = IntegrationStatus.RUNNING

    return interpreted_status

