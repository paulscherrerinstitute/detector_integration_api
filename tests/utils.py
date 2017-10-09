from detector_integration_api.manager import IntegrationManager
from detector_integration_api.validation import csax_eiger9m


class MockBackendClient(object):
    def __init__(self):
        self.status = "INITIALIZED"
        self.backend_url = "backend_url"

    def get_status(self):
        return self.status

    def set_config(self, configuration):
        pass


class MockDetectorClient(object):
    def __init__(self):
        self.status = "status idle"

    def get_status(self):
        return self.status

    def set_config(self, configuration):
        pass


class MockWriterClient(object):
    def __init__(self):
        self.status = False
        self._api_address = "writer_url"

    def get_status(self):
        return {"is_running": self.status}

    def set_parameters(self, configuration):
        pass


def get_test_integration_manager():
    backend_client = MockBackendClient()
    detector_client = MockDetectorClient()
    writer_client = MockWriterClient()
    manager = IntegrationManager(backend_client, writer_client, detector_client, csax_eiger9m.Validator)

    return manager
