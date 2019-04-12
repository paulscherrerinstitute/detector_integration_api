from enum import Enum

from detector_integration_api.utils import validate_mandatory_parameters, compare_client_status


class IntegrationStatus(Enum):
    READY = "ready",
    RUNNING = "running",
    ERROR = "error",
    COMPONENT_NOT_RESPONDING = "component_not_responding"


E_ACCOUNT_USER_ID_RANGE = [10000, 29999]

MANDATORY_WRITER_CONFIG_PARAMETERS = {
    "n_frames": int, "user_id": int, "output_file": str
}


def validate_writer_config(configuration):
    try:
        validate_mandatory_parameters(configuration, MANDATORY_WRITER_CONFIG_PARAMETERS)
    except Exception as ex:
        raise ValueError("Invalid writer configuration") from ex

    user_id = configuration["user_id"]
    if user_id != -1 and (user_id < E_ACCOUNT_USER_ID_RANGE[0] or user_id > E_ACCOUNT_USER_ID_RANGE[1]):
            raise ValueError("Provided user_id %d outside of specified range [%d-%d]."
                             % (user_id, E_ACCOUNT_USER_ID_RANGE[0], E_ACCOUNT_USER_ID_RANGE[1]))

    # Check if the filename ends with h5.
    if configuration["output_file"][-3:] != ".h5":
        configuration["output_file"] += ".h5"


MANDATORY_BACKEND_CONFIG_PARAMETERS = {
    "bit_depth": int
}


def validate_backend_config(configuration):
    try:
        validate_mandatory_parameters(configuration, MANDATORY_BACKEND_CONFIG_PARAMETERS)
    except Exception as ex:
        raise ValueError("Invalid backend configuration") from ex


MANDATORY_DETECTOR_CONFIG_PARAMETERS = {
    "period": float, "frames": int, "dr": int
}


def validate_detector_config(configuration):
    try:
        validate_mandatory_parameters(configuration, MANDATORY_DETECTOR_CONFIG_PARAMETERS)
    except Exception as ex:
        raise ValueError("Invalid detector configuration") from ex


def validate_configs_dependencies(writer_config, backend_config, detector_config):
    if backend_config["bit_depth"] != detector_config["dr"]:
        raise ValueError("Invalid config. Backend 'bit_depth' set to '%s', but detector 'dr' set to '%s'."
                         " They must be equal." % (backend_config["bit_depth"], detector_config["dr"]))

    if detector_config["timing"] == "auto":
        if detector_config["frames"] != writer_config["n_frames"]:
            raise ValueError("Invalid config for timing auto. "
                             "Detector 'n_frames' set to '%s', but writer 'n_frames' set to '%s'."
                             " They must be equal."
                             % (detector_config["n_frames"], writer_config["n_frames"]))

    elif detector_config["timing"] == "trigger" or detector_config["timing"] == "gating":
        if detector_config["cycles"] != writer_config["n_frames"]:
            raise ValueError("Invalid config for timing trigger. "
                             "Detector 'cycles' set to '%s', but writer 'n_frames' set to '%s'."
                             " They must be equal."
                             % (detector_config["cycles"], writer_config["n_frames"]))
    else:
        raise ValueError("Unexpected detector timing config '%s'. Use 'timing' or 'auto'." % detector_config["timing"])


def interpret_status(statuses):
    writer = statuses["writer"]

    # If no other conditions match.
    interpreted_status = IntegrationStatus.ERROR

    if compare_client_status(writer, "stopped"):
        interpreted_status = IntegrationStatus.READY

    elif compare_client_status(writer, "writing"):
        interpreted_status = IntegrationStatus.RUNNING

    return interpreted_status
