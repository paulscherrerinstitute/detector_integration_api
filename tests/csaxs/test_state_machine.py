import unittest

from detector_integration_api.deployment.csaxs import csaxs_manager
from detector_integration_api.deployment.csaxs.csaxs_validation_eiger9m import IntegrationStatus
from tests.utils import get_test_integration_manager


class TestCsaxsStateMachine(unittest.TestCase):
    def test_state_machine(self):
        manager = get_test_integration_manager(csaxs_manager)

        manager.writer_client.status = "stopped"
        manager.detector_client.status = "idle"
        manager.backend_client.status = "INITIALIZED"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.INITIALIZED)

        manager.writer_client.status = "stopped"
        manager.detector_client.status = "idle"
        manager.backend_client.status = "CONFIGURED"
        manager.last_config_successful = True
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.CONFIGURED)

        manager.last_config_successful = False
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.ERROR)

        manager.writer_client.status = "receiving"
        manager.detector_client.status = "running"
        manager.backend_client.status = "OPEN"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.RUNNING)

        manager.writer_client.status = "writing"
        manager.detector_client.status = "waiting"
        manager.backend_client.status = "OPEN"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.RUNNING)

        manager.writer_client.status = "receiving"
        manager.detector_client.status = "idle"
        manager.backend_client.status = "OPEN"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.DETECTOR_STOPPED)

        manager.writer_client.status = "writing"
        manager.detector_client.status = "idle"
        manager.backend_client.status = "OPEN"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.DETECTOR_STOPPED)

        manager.writer_client.status = "finished"
        manager.detector_client.status = "idle"
        manager.backend_client.status = "OPEN"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.FINISHED)

        manager.writer_client.status = "stopped"
        manager.detector_client.status = "idle"
        manager.backend_client.status = "OPEN"
        self.assertEqual(manager.get_acquisition_status(), IntegrationStatus.FINISHED)