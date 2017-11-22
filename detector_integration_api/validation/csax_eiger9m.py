from detector_integration_api.manager import IntegrationStatus


writer_cfg_params = ["output_file", "user_id", "group_id"]
backend_cfg_params = ["bit_depth", "n_frames"]
detector_cfg_params = ["period", "frames", "exptime", "dr"]

# Fields needed for the csax data format.
writer_cfg_params += ["date", "scan", "curr", "idgap", "harmonic", "sl0wh", "sl0ch", "sl1wh", "sl1wv", "sl1ch",
                      "sl1cv", "mokev", "moth1", "temp_mono_cryst_1", "temp_mono_cryst_2", "mobd", "sec",
                      "bpm4_gain_setting", "bpm4s", "bpm4_saturation_value", "bpm4x", "bpm4y", "bpm4z", "mith",
                      "mirror_coating", "mibd", "bpm5_gain_setting", "bpm5s", "bpm5_saturation_value", "bpm5x",
                      "bpm5y", "bpm5z", "sl2wh", "sl2wv", "sl2ch", "sl2cv", "bpm6_gain_setting", "bpm6s",
                      "bpm6_saturation_value", "bpm6x", "bpm6y", "bpm6z", "sl3wh", "sl3wv", "sl3ch", "sl3cv",
                      "fil_comb_description", "sl4wh", "sl4wv", "sl4ch", "sl4cv", "bs1x", "bs1y", "bs1_det_dist",
                      "bs1_status", "bs2x", "bs2y", "bs2_det_dist", "bs2_status", "diode", "sample_name",
                      "sample_description", "samx", "samy", "temp"]


def validate_writer_config(configuration):
    if not configuration:
        raise ValueError("Writer configuration cannot be empty.")

    if not all(x in configuration for x in writer_cfg_params):
        missing_parameters = [x for x in writer_cfg_params if x not in configuration]
        raise ValueError("Writer configuration missing mandatory parameters: %s" % missing_parameters)

    if configuration["output_file"][-3:] != ".h5":
        configuration["output_file"] += ".h5"


def validate_backend_config(configuration):
    if not configuration:
        raise ValueError("Backend configuration cannot be empty.")

    if not all(x in configuration for x in backend_cfg_params):
        missing_parameters = [x for x in backend_cfg_params if x not in configuration]
        raise ValueError("Backend configuration missing mandatory parameters: %s" % missing_parameters)


def validate_detector_config(configuration):
    if not configuration:
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


def interpret_status(statuses):
    writer = statuses["writer"]
    backend = statuses["backend"]
    detector = statuses["detector"]

    if writer is False and detector == "idle" and backend == "INITIALIZED":
        return IntegrationStatus.INITIALIZED

    elif writer is False and detector == "idle" and backend == "CONFIGURED":
        return IntegrationStatus.CONFIGURED

    elif writer is True and detector in ("running", "waiting") and backend == "OPEN":
        return IntegrationStatus.RUNNING

    elif writer is True and detector == "idle" and backend == "OPEN":
        return IntegrationStatus.DETECTOR_STOPPED

    return IntegrationStatus.ERROR
