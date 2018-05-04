from detector_integration_api.client.external_process_client import ExternalProcessClient


class CppWriterClient(ExternalProcessClient):
    PROCESS_STARTUP_PARAMETERS = ("output_file", "n_frames", "user_id")
    PROCESS_NAME = "writer"

    def get_execution_command(self):
        writer_command_format = "sh " + self.process_executable + " %s %s %s %s %s"
        writer_command = writer_command_format % (self.stream_url,
                                                  self.process_parameters["output_file"],
                                                  self.process_parameters.get("n_frames", 0),
                                                  self.process_port,
                                                  self.process_parameters.get("user_id", -1))

        return writer_command
