class ConfigValidator(object):

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

    def validate_command_execution(self, current_state, command):
        pass