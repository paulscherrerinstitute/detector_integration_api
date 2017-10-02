import unittest

from detector_integration_api.manager import IntegrationManager, IntegrationStatus
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


class TestIntegrationManager(unittest.TestCase):

    def get_integration_manager(self):
        backend_client = MockBackendClient()
        detector_client = MockDetectorClient()
        writer_client = MockWriterClient()
        manager = IntegrationManager(backend_client, writer_client, detector_client, csax_eiger9m.Validator)

        return manager

    def test_state_machine(self):
        manager = self.get_integration_manager()

        manager.writer_client.status = False
        manager.backend_client.status = "INITIALIZED"
        manager.detector_client.status = "status idle"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.INITIALIZED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.INITIALIZED")

        writer_status, backend_status, detector_status = manager.get_status_details()
        self.assertEqual(writer_status, manager.writer_client.status)
        self.assertEqual(backend_status, manager.backend_client.status)
        self.assertEqual(detector_status, manager.detector_client.status)

        manager.writer_client.status = False
        manager.backend_client.status = "CONFIGURED"
        manager.detector_client.status = "status idle"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.CONFIGURED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.CONFIGURED")

        manager.writer_client.status = True
        manager.backend_client.status = "OPEN"
        manager.detector_client.status = "status running"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.RUNNING)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.RUNNING")

        manager.writer_client.status = False
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.ERROR)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.ERROR")

    def test_set_config(self):
        manager = self.get_integration_manager()

        manager.writer_client.status = False
        manager.backend_client.status = "INITIALIZED"
        manager.detector_client.status = "status idle"

        writer_config = {}
        backend_config = {}
        detector_config = {}

        with self.assertRaisesRegex(ValueError, "Writer configuration missing mandatory"):
            manager.set_acquisition_config(writer_config, backend_config, detector_config)

        writer_config["output_file"] = "test.h5"

        with self.assertRaisesRegex(ValueError, "Backend configuration missing mandatory"):
            manager.set_acquisition_config(writer_config, backend_config, detector_config)

        backend_config["bit_depth"] = 16

        with self.assertRaisesRegex(ValueError, "Detector configuration missing mandatory"):
            manager.set_acquisition_config(writer_config, backend_config, detector_config)

        detector_config["exptime"] = 0.01
        detector_config["frames"] = 1
        detector_config["period"] = 0.1
        detector_config["dr"] = 32

        with self.assertRaisesRegex(ValueError, "Invalid config. Backend 'bit_depth' set to '16', "
                                                "but detector 'dr' set to '32'. They must be equal."):
            manager.set_acquisition_config(writer_config, backend_config, detector_config)

        detector_config["dr"] = 16

        manager.set_acquisition_config(writer_config, backend_config, detector_config)


