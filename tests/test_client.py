import unittest

from detector_integration_api import DetectorIntegrationClient


class TestRestClient(unittest.TestCase):

    def test_client_workflow(self):
        client = DetectorIntegrationClient()
        self.assertEqual(client.get_status()["status"], "IntegrationStatus.INITIALIZED")

        with self.assertRaisesRegex(Exception, "Specify config JSON with 3 root elements: "
                                               "'writer', 'backend', 'detector'."):
            client.set_config({})

        writer_config = None
        backend_config = None
        detector_config = None

        with self.assertRaisesRegex(Exception, "Writer configuration cannot be empty"):
            client.set_config({"writer": writer_config, "backend": backend_config, "detector": detector_config})

        writer_config = {"output_file": "/tmp/test.h5"}

        with self.assertRaisesRegex(Exception, "Backend configuration cannot be empty"):
            client.set_config({"writer": writer_config, "backend": backend_config, "detector": detector_config})

        backend_config = {"bit_depth": 16}

        with self.assertRaisesRegex(Exception, "Detector configuration cannot be empty"):
            client.set_config({"writer": writer_config, "backend": backend_config, "detector": detector_config})

        detector_config = {"period": 0.1, "frames": 100, "exptime": 0.01, "dr": 16}

        response = client.set_config({"writer": writer_config, "backend": backend_config, "detector": detector_config})

        self.assertDictEqual(response["config"]["writer"], writer_config)
        self.assertDictEqual(response["config"]["backend"], backend_config)
        self.assertDictEqual(response["config"]["detector"], detector_config)