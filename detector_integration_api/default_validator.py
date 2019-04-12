from enum import Enum


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
    if not configuration:
        raise ValueError("Writer configuration cannot be empty.")

    # Check if all mandatory parameters are present.
    if not all(x in configuration for x in MANDATORY_WRITER_CONFIG_PARAMETERS.keys()):
        missing_parameters = [x for x in MANDATORY_WRITER_CONFIG_PARAMETERS.keys() if x not in configuration]

        raise ValueError("Writer configuration missing mandatory parameters: %s" % missing_parameters)

    # Check if all format parameters are of correct type.
    wrong_parameter_types = ""
    for parameter_name, parameter_type in MANDATORY_WRITER_CONFIG_PARAMETERS.items():
        if not isinstance(configuration[parameter_name], parameter_type):

            # If the input type is an int, but float is required, convert it.
            if parameter_type == float and isinstance(configuration[parameter_name], int):
                configuration[parameter_name] = float(configuration[parameter_name])
                continue

            wrong_parameter_types += "\tWriter parameter '%s' expected of type '%s', but received of type '%s'.\n" % \
                                     (parameter_name, parameter_type, type(configuration[parameter_name]))

    if wrong_parameter_types:
        raise ValueError("Received parameters of invalid type:\n%s", wrong_parameter_types)

    user_id = configuration["user_id"]
    if user_id != -1 and (user_id < E_ACCOUNT_USER_ID_RANGE[0] or user_id > E_ACCOUNT_USER_ID_RANGE[1]):
            raise ValueError("Provided user_id %d outside of specified range [%d-%d]."
                             % (user_id, E_ACCOUNT_USER_ID_RANGE[0], E_ACCOUNT_USER_ID_RANGE[1]))

    # Check if the filename ends with h5.
    if configuration["output_file"][-3:] != ".h5":
        configuration["output_file"] += ".h5"
