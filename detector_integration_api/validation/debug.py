from detector_integration_api.manager import IntegrationStatus


writer_cfg_params = []
backend_cfg_params = []
detector_cfg_params = []


def validate_writer_config(configuration):
    if configuration is None:
        raise ValueError("Writer configuration cannot be None.")


def validate_backend_config(configuration):
    if configuration is None:
        raise ValueError("Backend configuration cannot be None.")


def validate_detector_config(configuration):
    if configuration is None:
        raise ValueError("Detector configuration cannot be None.")


def validate_configs_dependencies(writer_config, backend_config, detector_config):
    pass


def interpret_status(writer, backend, detector):

    if writer is False and detector == "idle" and backend == "INITIALIZED":
        return IntegrationStatus.INITIALIZED

    elif writer is False and detector == "idle" and backend == "CONFIGURED":
        return IntegrationStatus.CONFIGURED

    elif writer is True and detector in ("running", "waiting") and backend == "OPEN":
        return IntegrationStatus.RUNNING

    elif writer is True and detector == "idle" and backend == "OPEN":
        return IntegrationStatus.DETECTOR_STOPPED

    return IntegrationStatus.ERROR
