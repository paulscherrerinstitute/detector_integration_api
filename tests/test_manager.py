import unittest

from detector_integration_api.deployment.sf.sf_manager import IntegrationStatus
from tests.utils import get_test_integration_manager, get_csax9m_test_writer_parameters


class TestIntegrationManager(unittest.TestCase):
    def test_state_machine(self):
        manager = get_test_integration_manager()

        manager.writer_client.is_running = False
        manager.backend_client.status = "INITIALIZED"
        manager.detector_client.status = "idle"
        manager.bsread_client.status = False
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.INITIALIZED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.INITIALIZED")

        statuses = manager.get_status_details()
        writer_status = statuses["writer"]
        backend_status = statuses["backend"]
        detector_status = statuses["detector"]

        self.assertEqual(writer_status, manager.writer_client.is_running)
        self.assertEqual(backend_status, manager.backend_client.status)
        self.assertEqual(detector_status, manager.detector_client.status)

        manager.writer_client.is_running = False
        manager.backend_client.status = "CONFIGURED"
        manager.detector_client.status = "idle"
        manager.bsread_client.status = False
        manager.last_config_successful = True
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.CONFIGURED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.CONFIGURED")

        manager.last_config_successful = False
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.ERROR)

        manager.writer_client.is_running = True
        manager.backend_client.status = "OPEN"
        manager.detector_client.status = "running"
        manager.bsread_client.is_running = True
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.RUNNING)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.RUNNING")

        manager.writer_client.is_running = True
        manager.backend_client.status = "OPEN"
        manager.detector_client.status = "idle"
        manager.bsread_client.is_running = True
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.DETECTOR_STOPPED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.DETECTOR_STOPPED")

        manager.writer_client.is_running = False
        manager.backend_client.status = "OPEN"
        manager.detector_client.status = "idle"
        manager.bsread_client.is_running = True
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.BSREAD_STILL_RUNNING)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.BSREAD_STILL_RUNNING")

        manager.detector_client.status = "idle"
        manager.bsread_client.is_running = False
        manager.writer_client.is_running = False
        manager.backend_client.status = "OPEN"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.FINISHED)
        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.FINISHED")

    def test_set_config(self):
        # TODO: This test is specific to cSAXS.
        pass
        # manager = get_test_integration_manager("detector_integration_api.validation.csax_eiger9m")
        #
        # manager.writer_client.is_running = False
        # manager.backend_client.status = "INITIALIZED"
        # manager.detector_client.status = "idle"
        #
        # writer_config = {"test": 1}
        # backend_config = {"test": 1}
        # detector_config = {"test": 1}
        # bsread_config = {"test": 1}
        #
        # with self.assertRaisesRegex(ValueError, "Writer configuration missing mandatory"):
        #     manager.set_acquisition_config({"writer": writer_config,
        #                                     "backend": backend_config,
        #                                     "detector": detector_config,
        #                                     "bsread": bsread_config})
        #
        # writer_config.update(get_csax9m_test_writer_parameters())
        # # See if only 1 missing parameter is still detected.
        # del writer_config["output_file"]
        #
        # with self.assertRaisesRegex(ValueError, "Writer configuration missing mandatory"):
        #     manager.set_acquisition_config({"writer": writer_config,
        #                                     "backend": backend_config,
        #                                     "detector": detector_config,
        #                                     "bsread": bsread_config})
        #
        # writer_config["output_file"] = "not_important"
        # writer_config["user_id"] = 10
        # writer_config["group_id"] = 10
        #
        # with self.assertRaisesRegex(ValueError, "Backend configuration missing mandatory"):
        #     manager.set_acquisition_config({"writer": writer_config,
        #                                     "backend": backend_config,
        #                                     "detector": detector_config,
        #                                     "bsread": bsread_config})
        #
        # backend_config["bit_depth"] = 16
        # backend_config["n_frames"] = 1000
        #
        # with self.assertRaisesRegex(ValueError, "Detector configuration missing mandatory"):
        #     manager.set_acquisition_config({"writer": writer_config,
        #                                     "backend": backend_config,
        #                                     "detector": detector_config,
        #                                     "bsread": bsread_config})
        #
        # detector_config["exptime"] = 0.01
        # detector_config["frames"] = 1
        # detector_config["period"] = 0.1
        # detector_config["dr"] = 32
        #
        # with self.assertRaisesRegex(ValueError, "Invalid config. Backend 'bit_depth' set to '16', "
        #                                         "but detector 'dr' set to '32'. They must be equal."):
        #     manager.set_acquisition_config({"writer": writer_config,
        #                                     "backend": backend_config,
        #                                     "detector": detector_config,
        #                                     "bsread": bsread_config})
        #
        # detector_config["dr"] = 16
        #
        # with self.assertRaisesRegex(ValueError, "Invalid config. Backend 'n_frames' set to '1000', "
        #                                         "but detector 'frames' set to '1'. They must be equal."):
        #     manager.set_acquisition_config({"writer": writer_config,
        #                                     "backend": backend_config,
        #                                     "detector": detector_config,
        #                                     "bsread": bsread_config})
        #
        # detector_config["frames"] = 1000
        #
        # manager.set_acquisition_config({"writer": writer_config,
        #                                 "backend": backend_config,
        #                                 "detector": detector_config,
        #                                 "bsread": bsread_config})

    def test_acquisition_procedure(self):
        manager = get_test_integration_manager()

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.INITIALIZED")

        writer_config = get_csax9m_test_writer_parameters()
        writer_config.update({"output_file": "test.h5",
                              "user_id": 1,
                              "group_id": 1})

        backend_config = {"bit_depth": 16,
                          "n_frames": 1000}

        detector_config = {"exptime": 0.01,
                           "frames": 1000,
                           "period": 0.01,
                           "dr": 16}

        bsread_config = {"output_file": "test.h5",
                         "channels": None}

        manager.set_acquisition_config({"writer": writer_config,
                                        "backend": backend_config,
                                        "detector": detector_config,
                                        "bsread": bsread_config})

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.CONFIGURED")

        manager.start_acquisition()

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.RUNNING")

        manager.stop_acquisition()

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.INITIALIZED")

        manager.set_acquisition_config({"writer": writer_config,
                                        "backend": backend_config,
                                        "detector": detector_config,
                                        "bsread": bsread_config})

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.CONFIGURED")

        manager.reset()

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.INITIALIZED")

        self.assertDictEqual(writer_config, manager.writer_client.config)
        self.assertDictEqual(backend_config, manager.backend_client.config)
        self.assertDictEqual(detector_config, manager.detector_client.config)

    def test_debug_validator(self):
        manager = get_test_integration_manager()

        writer_config = {"output_file": "test.h5",
                         "user_id": 1,
                         "group_id": 1}

        backend_config = {"bit_depth": 16,
                          "n_frames": 1000}

        detector_config = {"exptime": 0.01,
                           "frames": 1000,
                           "period": 0.01,
                           "dr": 16}

        bsread_config = {"output_file": "test.h5",
                         "channels": None}

        manager.set_acquisition_config({"writer": writer_config,
                                        "backend": backend_config,
                                        "detector": detector_config,
                                        "bsread": bsread_config})

        self.assertEqual(manager.get_acquisition_status_string(), "IntegrationStatus.CONFIGURED")
