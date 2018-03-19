import unittest

from detector_integration_api.client.detector_cli_client import DetectorClient
from detector_integration_api.utils import ClientDisableWrapper


class TestIntegrationManager(unittest.TestCase):
    def test_detector_process_output(self):

        self.assertEqual(DetectorClient.validate_response(b'exptime 03.10000', "exptime", 3.1), 3.1)
        self.assertEqual(DetectorClient.validate_response(b'frames 12.0000', "frames", 12), 12)

        with self.assertRaisesRegex(ValueError, "Response is empty."):
            DetectorClient.validate_response(b'', "frames")

        with self.assertRaisesRegex(ValueError, "Response for parameter 'frames' not in expected format: invalid"):
            DetectorClient.validate_response(b'invalid', "frames")

        with self.assertRaisesRegex(ValueError, "Invalid parameter_name 'invalid' when requested parameter "
                                                "was 'frames': invalid 10"):
            DetectorClient.validate_response(b'invalid 10', "frames")

        with self.assertRaisesRegex(ValueError, "Invalid parameter 'frames' value, expected "):
            DetectorClient.validate_response(b'frames 10.0000', "frames", 11)

        DetectorClient.validate_response(b'status idle', "status", ["idle", "running"])

    def test_client_wrapper_exception_handling(self):
        class TestClient(object):
            def exception(self):
                raise ValueError()

        raw_client = TestClient()
        client = ClientDisableWrapper(raw_client)

        with self.assertRaisesRegex(RuntimeError, "Cannot communicate with external component"):
            client.exception()

        client = ClientDisableWrapper(raw_client, True, "writer")

        with self.assertRaisesRegex(RuntimeError, "Cannot communicate with writer."):
            client.exception()
