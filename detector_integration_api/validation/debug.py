from detector_integration_api.manager import IntegrationStatus


writer_cfg_params = []
backend_cfg_params = []
detector_cfg_params = []


def validate_writer_config(configuration):
    if configuration is None:
        raise ValueError("Writer configuration cannot be empty.")

    if not all(x in configuration for x in writer_cfg_params):
        missing_parameters = [x for x in writer_cfg_params if x not in configuration]
        raise ValueError("Writer configuration missing mandatory parameters: %s" % missing_parameters)

    if configuration["output_file"][-3:] != ".h5":
        configuration["output_file"] += ".h5"


def validate_backend_config(configuration):
    if configuration is None:
        raise ValueError("Backend configuration cannot be empty.")

    if not all(x in configuration for x in backend_cfg_params):
        missing_parameters = [x for x in backend_cfg_params if x not in configuration]
        raise ValueError("Backend configuration missing mandatory parameters: %s" % missing_parameters)


def validate_detector_config(configuration):
    if configuration is None:
        raise ValueError("Detector configuration cannot be empty.")

    if not all(x in configuration for x in detector_cfg_params):
        missing_parameters = [x for x in detector_cfg_params if x not in configuration]
        raise ValueError("Detector configuration missing mandatory parameters: %s" % missing_parameters)


def validate_configs_dependencies(writer_config, backend_config, detector_config):
    if backend_config["bit_depth"] != detector_config["dr"]:
        raise ValueError("Invalid config. Backend 'bit_depth' set to '%s', but detector 'dr' set to '%s'."
                         " They must be equal."
                         % (backend_config["bit_depth"], detector_config["dr"]))

    if backend_config["n_frames"] != detector_config["frames"]:
        raise ValueError("Invalid config. Backend 'n_frames' set to '%s', but detector 'frames' set to '%s'. "
                         "They must be equal." % (backend_config["n_frames"], detector_config["frames"]))


def interpret_status(writer, backend, detector):

    if writer is False and detector == "idle" and backend == "INITIALIZED":
        return IntegrationStatus.INITIALIZED

    elif writer is False and detector == "idle" and backend == "CONFIGURED":
        return IntegrationStatus.CONFIGURED

    elif writer is True and detector == "running" and backend == "OPEN":
        return IntegrationStatus.RUNNING

    return IntegrationStatus.ERROR
