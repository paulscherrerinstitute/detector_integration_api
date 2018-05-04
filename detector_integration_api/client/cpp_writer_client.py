from detector_integration_api.client.external_process_client import ExternalProcessClient


class CppWriterClient(ExternalProcessClient):
    PROCESS_STARTUP_PARAMETERS = ("output_file", "n_frames", "user_id")