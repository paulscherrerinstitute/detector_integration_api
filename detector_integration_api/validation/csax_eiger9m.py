from detector_integration_api.manager import IntegrationStatus


class Validator(object):
    writer_cfg_params = ["output_file"]
    backend_cfg_params = ["bit_depth"]
    detector_cfg_params = ["period", "frames", "exptime", "dr"]

    @staticmethod
    def validate_writer_config(configuration):
        if not all(x in configuration for x in Validator.writer_cfg_params):
            raise ValueError("Writer configuration missing mandatory parameters: %s", Validator.writer_cfg_params)

        if configuration["output_file"][-3:] != ".h5":
            configuration["output_file"] += ".h5"

    @staticmethod
    def validate_backend_config(configuration):
        if not all(x in configuration for x in Validator.backend_cfg_params):
            raise ValueError("Backend configuration missing mandatory parameters: %s", Validator.backend_cfg_params)

    @staticmethod
    def validate_detector_config(configuration):
        if not all(x in configuration for x in Validator.detector_cfg_params):
            raise ValueError("Detector configuration missing mandatory parameters: %s", Validator.detector_cfg_params)

    @staticmethod
    def validate_configs_dependencies(writer_config, backend_config, detector_config):
        if backend_config["bit_depth"] != detector_config["dr"]:
            raise ValueError("Invalid config. Backend 'bit_depth' set to '%s', but detector 'dr' set to '%s'."
                             " They must be equal."
                             % (backend_config["bit_depth"], detector_config["dr"]))

    @staticmethod
    def interpret_status(writer, backend, detector):

        if writer is False and detector == "idle" and backend == "INITIALIZED":
            return IntegrationStatus.INITIALIZED

        elif writer is False and detector == "idle" and backend == "CONFIGURED":
            return IntegrationStatus.CONFIGURED

        elif writer is True and detector == "running" and backend == "OPEN":
            return IntegrationStatus.RUNNING

        return IntegrationStatus.ERROR
