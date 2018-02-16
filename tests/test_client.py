import signal
import unittest

from multiprocessing import Process
from threading import Thread
from time import sleep, time

import os

from detector_integration_api import DetectorIntegrationClient
from detector_integration_api.deployment import debug_manager
from detector_integration_api.deployment.csaxs import csaxs_manager
from tests.utils import start_test_integration_server, get_csax9m_test_writer_parameters


class TestRestClient(unittest.TestCase):
    def setUp(self):
        self.host = "0.0.0.0"
        self.port = 10000

        self.dia_process = Process(target=start_test_integration_server, args=(self.host, self.port, debug_manager))
        self.dia_process.start()

        # Give it some time to start.
        sleep(1)

    def tearDown(self):
        os.kill(self.dia_process.pid, signal.SIGINT)

        # Wait for the server to die.
        sleep(1)

    def test_client_workflow(self):
        client = DetectorIntegrationClient()

        client.reset()

        self.assertEqual(client.get_status()["status"], "IntegrationStatus.INITIALIZED")

        writer_config = ({"output_file": "/tmp/test.h5",
                          "n_frames": 100,
                          "user_id": 0,
                          "group_id": 0})

        backend_config = {"bit_depth": 16,
                          "n_frames": 100}

        detector_config = {"period": 0.1,
                           "frames": 100,
                           "exptime": 0.01,
                           "dr": 16}

        configuration = {"writer": writer_config,
                         "backend": backend_config,
                         "detector": detector_config}

        response = client.set_config(configuration)

        self.assertDictEqual(response["config"]["writer"], writer_config)
        self.assertDictEqual(response["config"]["backend"], backend_config)
        self.assertDictEqual(response["config"]["detector"], detector_config)

        self.assertEqual(client.get_status()["status"], "IntegrationStatus.CONFIGURED")

        client.start()

        self.assertEqual(client.get_status()["status"], "IntegrationStatus.RUNNING")

        client.stop()

        self.assertEqual(client.get_status()["status"], "IntegrationStatus.INITIALIZED")

        with self.assertRaisesRegex(Exception, "Cannot start acquisition"):
            client.start()

        client.set_last_config()

        self.assertEqual(client.get_status()["status"], "IntegrationStatus.CONFIGURED")

        client.start()

        self.assertEqual(client.get_status()["status"], "IntegrationStatus.RUNNING")

        client.stop()

        self.assertEqual(client.get_status()["status"], "IntegrationStatus.INITIALIZED")

        with self.assertRaisesRegex(Exception, "n_frames"):
            client.update_config({"writer": {"user_id": 1},
                                  "backend": {"n_frames": 50},
                                  "detector": {"frames": 50}})

        response = client.update_config({"writer": {"n_frames": 50,
                                                    "user_id": 1},
                                         "backend": {"n_frames": 50},
                                         "detector": {"frames": 50}})

        writer_config["user_id"] = 1
        writer_config["n_frames"] = 50
        backend_config["n_frames"] = 50
        detector_config["frames"] = 50

        self.assertDictEqual(response["config"]["writer"], writer_config)
        self.assertDictEqual(response["config"]["backend"], backend_config)
        self.assertDictEqual(response["config"]["detector"], detector_config)

        response = client.update_config({"writer": {"group_id": 1}})

        writer_config["group_id"] = 1

        self.assertDictEqual(response["config"]["writer"], writer_config)
        self.assertDictEqual(response["config"]["backend"], backend_config)
        self.assertDictEqual(response["config"]["detector"], detector_config)

        self.assertEqual(client.get_status()["status"], "IntegrationStatus.CONFIGURED")

        client.reset()

        self.assertEqual(client.get_status()["status"], "IntegrationStatus.INITIALIZED")

        response = client.set_last_config()

        self.assertDictEqual(response["config"]["writer"], writer_config)
        self.assertDictEqual(response["config"]["backend"], backend_config)
        self.assertDictEqual(response["config"]["detector"], detector_config)

        self.assertEqual(client.get_status()["status"], "IntegrationStatus.CONFIGURED")

        self.assertEqual(client.get_detector_value("frames"), response["config"]["detector"]["frames"])

        client.reset()

        client.set_config_from_file(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                 "debug_config.json"))

        self.assertEqual(client.get_status()["status"], "IntegrationStatus.CONFIGURED")

        self.assertTrue("server_info" in client.get_server_info())

    def test_update_config(self):
        client = DetectorIntegrationClient()

        config = client.get_config()
        self.assertEqual(config["config"]["backend"], {})
        self.assertEqual(config["config"]["writer"], {})
        self.assertEqual(config["config"]["detector"], {})

        detector_config = {"frames": 10000, "dr": 16, "period": 0.001, "exptime": 0.0001}
        backend_config = {"n_frames": 10000, "bit_depth": 16}
        writer_config = {"user_id": 16371, "output_file": "something", "n_frames": 10000}

        configuration = {"detector": detector_config,
                         "backend": backend_config,
                         "writer": writer_config}

        client.update_config(configuration)

        configuration = client.get_config()["config"]

        self.assertEqual(configuration["detector"], detector_config)
        self.assertEqual(configuration["writer"], writer_config)
        self.assertEqual(configuration["backend"], backend_config)

        with self.assertRaisesRegex(Exception, "Invalid config"):
            client.update_config({"detector": {"dr": 32}})

        client.update_config({"detector": {"dr": 32},
                              "backend": {"bit_depth": 32}})

        detector_config["dr"] = 32
        backend_config["bit_depth"] = 32

        configuration = client.get_config()["config"]
        self.assertEqual(configuration["detector"], detector_config)
        self.assertEqual(configuration["writer"], writer_config)
        self.assertEqual(configuration["backend"], backend_config)

    def test_set_detector_value(self):
        client = DetectorIntegrationClient()

        value = 0.023
        client.set_detector_value("period", value)

        self.assertEqual(value, client.get_detector_value("period"))

    def test_wait_for_status(self):

        time_to_wait = 0
        sleep_time = 1
        timeout = 1.5

        client = DetectorIntegrationClient()

        detector_config = {"frames": 10000, "dr": 16, "period": 0.001, "exptime": 0.0001}
        backend_config = {"n_frames": 10000, "bit_depth": 16}
        writer_config = {"user_id": 16371, "output_file": "something", "n_frames": 10000}

        configuration = {"detector": detector_config,
                         "backend": backend_config,
                         "writer": writer_config}

        def wait_for_status_thread():
            client2 = DetectorIntegrationClient()
            start_time = time()

            try:
                client2.wait_for_status("IntegrationStatus.RUNNING", timeout=timeout)
            except:
                pass

            nonlocal time_to_wait
            time_to_wait = time() - start_time

        wait_thread = Thread(target=wait_for_status_thread)
        wait_thread.start()

        sleep(sleep_time)

        client.reset()
        client.set_config(configuration)

        client.start()
        wait_thread.join()
        client.stop()

        self.assertTrue(time_to_wait > sleep_time)

        wait_thread = Thread(target=wait_for_status_thread)
        wait_thread.start()
        wait_thread.join()

        self.assertTrue(time_to_wait >= timeout)

    def test_clients_enabled(self):
        client = DetectorIntegrationClient()
        clients_enabled = client.get_clients_enabled()["clients_enabled"]

        self.assertTrue(clients_enabled["writer"])
        self.assertTrue(clients_enabled["backend"])
        self.assertTrue(clients_enabled["detector"])

        client.set_clients_enabled({})
        clients_enabled = client.get_clients_enabled()["clients_enabled"]

        self.assertTrue(clients_enabled["writer"])
        self.assertTrue(clients_enabled["backend"])
        self.assertTrue(clients_enabled["detector"])

        client.set_clients_enabled({"writer": False})
        clients_enabled = client.get_clients_enabled()["clients_enabled"]

        self.assertFalse(clients_enabled["writer"])
        self.assertTrue(clients_enabled["backend"])
        self.assertTrue(clients_enabled["detector"])

        client.set_clients_enabled({"writer": True,
                                    "backend": False,
                                    "detector": False})
        clients_enabled = client.get_clients_enabled()["clients_enabled"]

        self.assertTrue(clients_enabled["writer"])
        self.assertFalse(clients_enabled["backend"])
        self.assertFalse(clients_enabled["detector"])

        client.set_clients_enabled({"writer": False,
                                    "backend": False,
                                    "detector": False})
        clients_enabled = client.get_clients_enabled()["clients_enabled"]

        self.assertFalse(clients_enabled["writer"])
        self.assertFalse(clients_enabled["backend"])
        self.assertFalse(clients_enabled["detector"])
