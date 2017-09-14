class Validator(object):

    @staticmethod
    def validate_writer_config(configuration):
        if "output_file" in writer_config:
            if writer_config["output_file"][-3:] != ".h5":
                writer_config["output_file"] += ".h5"
        pass

    @staticmethod
    def validate_backend_config(configuration):
        pass

    @staticmethod
    def validate_detector_config(configuration):
        pass

    writer_statuses = {False: "CONFIGURED", True: "OPEN"}
    writer_cfg_params = ["output_file", ]
    backend_cfg_params = ["bit_depth", "period", "n_frames"]

    @staticmethod
    def validate_command_execution(current_state, command):
        pass

    @staticmethod
    def interpret_status(writer, backend, detector):
        if writer == "CONFIGURED":
            if backend != "OPEN":
                return backend
            else:
                return writer
        else:
            return backend