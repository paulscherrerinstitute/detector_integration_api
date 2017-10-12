import json
from importlib import import_module

import bottle
import os

from detector_integration_api.manager import IntegrationManager
from detector_integration_api.rest_api.rest_server import register_rest_interface, register_debug_rest_interface


class MockBackendClient(object):
    def __init__(self):
        self.status = "INITIALIZED"
        self.backend_url = "backend_url"
        self.config = None

    def get_status(self):
        return self.status

    def set_config(self, configuration):
        self.status = "CONFIGURED"
        self.config = configuration

    def open(self):
        self.status = "OPEN"

    def close(self):
        self.status = "CLOSE"

    def reset(self):
        self.status = "INITIALIZED"


class MockDetectorClient(object):
    def __init__(self):
        self.status = "idle"
        self.config = None

    def get_status(self):
        return self.status

    def set_config(self, configuration):
        self.config = configuration

    def start(self):
        self.status = "running"

    def stop(self):
        self.status = "idle"

    def get_value(self, name):
        return self.config[name]


class MockWriterClient(object):
    def __init__(self):
        self.is_running = False
        self._api_address = "writer_url"
        self.config = None

    def get_status(self):
        return {"is_running": self.is_running}

    def set_parameters(self, configuration):
        self.config = configuration

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False


def get_test_integration_manager(validator_module="detector_integration_api.validation.debug"):
    backend_client = MockBackendClient()
    detector_client = MockDetectorClient()
    writer_client = MockWriterClient()
    validator = import_module(validator_module)

    manager = IntegrationManager(backend_client, writer_client, detector_client, validator)

    return manager


def start_test_integration_server(host, port):

    backend_client = MockBackendClient()
    writer_client = MockWriterClient()
    detector_client = MockDetectorClient()
    validator = import_module("detector_integration_api.validation.csax_eiger9m")

    integration_manager = IntegrationManager(writer_client=writer_client,
                                             backend_client=backend_client,
                                             detector_client=detector_client,
                                             validator=validator)

    app = bottle.Bottle()
    register_rest_interface(app=app, integration_manager=integration_manager)
    register_debug_rest_interface(app=app, integration_manager=integration_manager)

    bottle.run(app=app, host=host, port=port)


def get_csax9m_test_writer_parameters():
    """
    This are all the parameters you need to pass to the writer in order to write in the csax format.
    """
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "csaxs_eiger_config.json")

    with open(filename) as input_file:
        configuration = json.load(input_file)

    return configuration["writer"]
