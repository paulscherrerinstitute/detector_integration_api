import unittest

from detector_integration_api.debug import manager as debug_manager
from detector_integration_api.debug.validator import IntegrationStatus
from tests.utils import get_test_integration_manager


class TestIntegrationManager(unittest.TestCase):
    def test_state_machine(self):
        manager = get_test_integration_manager(debug_manager)

        manager.writer_client.status = "stopped"
        manager.backend_client.status = "INITIALIZED"
        manager.detector_client.status = "idle"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.INITIALIZED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.INITIALIZED")

        statuses = manager.get_status_details()
        writer_status = statuses["writer"]
        backend_status = statuses["backend"]
        detector_status = statuses["detector"]

        self.assertEqual(writer_status, manager.writer_client.status)
        self.assertEqual(backend_status, manager.backend_client.status)
        self.assertEqual(detector_status, manager.detector_client.status)

        manager.writer_client.status = "stopped"
        manager.backend_client.status = "CONFIGURED"
        manager.detector_client.status = "idle"
        manager.last_config_successful = True
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.CONFIGURED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.CONFIGURED")

        manager.last_config_successful = False
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.ERROR)

        manager.writer_client.status = "receiving"
        manager.backend_client.status = "OPEN"
        manager.detector_client.status = "running"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.RUNNING)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.RUNNING")

        manager.writer_client.status = "writing"
        manager.backend_client.status = "OPEN"
        manager.detector_client.status = "idle"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.DETECTOR_STOPPED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.DETECTOR_STOPPED")

        manager.writer_client.status = "stopped"
        manager.detector_client.status = "idle"
        manager.backend_client.status = "OPEN"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.FINISHED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.FINISHED")

    def test_set_config(self):

        manager = get_test_integration_manager(debug_manager)

        manager.writer_client.status = "stopped"
        manager.backend_client.status = "INITIALIZED"
        manager.detector_client.status = "idle"

        writer_config = {"test": 1}
        backend_config = {"test": 1}
        detector_config = {"test": 1}

        configuration = {"detector": detector_config,
                         "backend": backend_config,
                         "writer": writer_config}

        # Note: This test relies on the order in which parameters are checked.

        with self.assertRaisesRegex(ValueError, "Writer configuration missing mandatory"):
            manager.set_acquisition_config(configuration)

        writer_config.update({"user_id": 16371, "output_file": "something", "n_frames": 10000})

        # See if only 1 missing parameter is still detected.
        del writer_config["output_file"]

        with self.assertRaisesRegex(ValueError, "Writer configuration missing mandatory"):
            manager.set_acquisition_config(configuration)

        writer_config["output_file"] = "not_important"
        writer_config["user_id"] = 10
        writer_config["group_id"] = 10

        with self.assertRaisesRegex(ValueError, "Backend configuration missing mandatory"):
            manager.set_acquisition_config(configuration)

        backend_config["bit_depth"] = 16
        backend_config["n_frames"] = 1000

        with self.assertRaisesRegex(ValueError, "Detector configuration missing mandatory"):
            manager.set_acquisition_config(configuration)

        detector_config["exptime"] = 0.01
        detector_config["frames"] = 1
        detector_config["period"] = 0.1
        detector_config["dr"] = 32

        with self.assertRaisesRegex(ValueError, "Invalid config. Backend 'bit_depth' set to '16', "
                                                "but detector 'dr' set to '32'. They must be equal."):
            manager.set_acquisition_config(configuration)

        detector_config["dr"] = 16

        with self.assertRaisesRegex(ValueError, "Invalid config. Backend 'n_frames' set to '1000', "
                                                "but detector 'frames' set to '1'. They must be equal."):
            manager.set_acquisition_config(configuration)

        detector_config["frames"] = 1000

        with self.assertRaisesRegex(ValueError, "Invalid config. Backend 'n_frames' set to '1000', "
                                                "but writer 'n_frames' set to '10000'. They must be equal."):
            manager.set_acquisition_config(configuration)

        writer_config["n_frames"] = 1000

        manager.set_acquisition_config(configuration)

    def test_acquisition_procedure(self):
        manager = get_test_integration_manager(debug_manager)

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.INITIALIZED")

        detector_config = {"frames": 10000, "dr": 16, "period": 0.001, "exptime": 0.0001}
        backend_config = {"n_frames": 10000, "bit_depth": 16}
        writer_config = {"user_id": 16371, "output_file": "something", "n_frames": 10000}

        configuration = {"detector": detector_config,
                         "backend": backend_config,
                         "writer": writer_config}

        manager.set_acquisition_config(configuration)

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.CONFIGURED")

        manager.start_acquisition()

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.RUNNING")

        manager.stop_acquisition()

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.INITIALIZED")

        manager.set_acquisition_config(configuration)

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.CONFIGURED")

        manager.reset()

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.INITIALIZED")

        self.assertDictEqual(writer_config, manager.writer_client.config)
        self.assertDictEqual(backend_config, manager.backend_client.config)
        self.assertDictEqual(detector_config, manager.detector_client.config)
