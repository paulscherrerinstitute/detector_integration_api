from enum import Enum

from detector_integration_api.utils import validate_mandatory_parameters


class IntegrationStatus(Enum):
    READY = "ready",
    RUNNING = "running",
    ERROR = "error",
    COMPONENT_NOT_RESPONDING = "component_not_responding"


E_ACCOUNT_USER_ID_RANGE = [10000, 29999]


MANDATORY_WRITER_CONFIG_PARAMETERS = {
    "n_frames": int, "user_id": int, "output_file": str
}

MANDATORY_BACKEND_CONFIG_PARAMETERS = {
    "bit_depth": int
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


def validate_backend_config(configuration):
    try:
        validate_mandatory_parameters(configuration, MANDATORY_BACKEND_CONFIG_PARAMETERS)
    except Exception as ex:
        raise ValueError("Invalid backend configuration") from ex
