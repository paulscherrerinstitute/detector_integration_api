import unittest

from detector_integration_api.manager import IntegrationStatus
from tests.utils import get_test_integration_manager


class TestIntegrationManager(unittest.TestCase):
    def test_state_machine(self):
        manager = get_test_integration_manager()

        manager.writer_client.status = False
        manager.backend_client.status = "INITIALIZED"
        manager.detector_client.status = "idle"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.INITIALIZED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.INITIALIZED")

        writer_status, backend_status, detector_status = manager.get_status_details()
        self.assertEqual(writer_status, manager.writer_client.status)
        self.assertEqual(backend_status, manager.backend_client.status)
        self.assertEqual(detector_status, manager.detector_client.status)

        manager.writer_client.status = False
        manager.backend_client.status = "CONFIGURED"
        manager.detector_client.status = "idle"
        manager.last_config_successful = True
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.CONFIGURED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.CONFIGURED")

        manager.last_config_successful = False
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.ERROR)

        manager.writer_client.status = True
        manager.backend_client.status = "OPEN"
        manager.detector_client.status = "running"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.RUNNING)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.RUNNING")

        manager.writer_client.status = False
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.ERROR)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.ERROR")

    def test_set_config(self):
        manager = get_test_integration_manager()

        manager.writer_client.status = False
        manager.backend_client.status = "INITIALIZED"
        manager.detector_client.status = "idle"

        writer_config = {"test": 1}
        backend_config = {"test": 1}
        detector_config = {"test": 1}

        with self.assertRaisesRegex(ValueError, "Writer configuration missing mandatory"):
            manager.set_acquisition_config(writer_config, backend_config, detector_config)

        writer_config["output_file"] = "test.h5"

        with self.assertRaisesRegex(ValueError, "Backend configuration missing mandatory"):
            manager.set_acquisition_config(writer_config, backend_config, detector_config)

        backend_config["bit_depth"] = 16
        backend_config["n_frames"] = 1000

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
