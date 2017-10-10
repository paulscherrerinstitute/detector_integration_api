import bottle

from detector_integration_api.manager import IntegrationManager
from detector_integration_api.rest_api.rest_server import register_rest_interface, register_debug_rest_interface
from detector_integration_api.validation import csax_eiger9m


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


def get_test_integration_manager():
    backend_client = MockBackendClient()
    detector_client = MockDetectorClient()
    writer_client = MockWriterClient()
    manager = IntegrationManager(backend_client, writer_client, detector_client, csax_eiger9m.Validator)

    return manager


def start_test_integration_server(host, port):

    backend_client = MockBackendClient()
    writer_client = MockWriterClient()
    detector_client = MockDetectorClient()
    validator = csax_eiger9m.Validator

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
    :return:
    """
    return {"date": 1.0,
            "scan": 1.0,
            "curr": 1.0,
            "idgap": 1.0,
            "harmonic": 1.0,
            "sl0wh": 1.0,
            "sl0ch": 1.0,
            "sl1wh": 1.0,
            "sl1wv": 1.0,
            "sl1ch": 1.0,
            "sl1cv": 1.0,
            "mokev": 1.0,
            "moth1": 1.0,
            "temp_mono_cryst_1": 1.0,
            "temp_mono_cryst_2": 1.0,
            "mobd": 1.0,
            "sec": 1.0,
            "bpm4_gain_setting": 1.0,
            "bpm4s": 1.0,
            "bpm4_saturation_value": 1.0,
            "bpm4x": 1.0,
            "bpm4y": 1.0,
            "bpm4z": 1.0,
            "mith": 1.0,
            "mirror_coating": 1.0,
            "mibd": 1.0,
            "bpm5_gain_setting": 1.0,
            "bpm5s": 1.0,
            "bpm5_saturation_value": 1.0,
            "bpm5x": 1.0,
            "bpm5y": 1.0,
            "bpm5z": 1.0,
            "sl2wh": 1.0,
            "sl2wv": 1.0,
            "sl2ch": 1.0,
            "sl2cv": 1.0,
            "bpm6_gain_setting": 1.0,
            "bpm6s": 1.0,
            "bpm6_saturation_value": 1.0,
            "bpm6x": 1.0,
            "bpm6y": 1.0,
            "bpm6z": 1.0,
            "sl3wh": 1.0,
            "sl3wv": 1.0,
            "sl3ch": 1.0,
            "sl3cv": 1.0,
            "fil_comb_description": 1.0,
            "sl4wh": 1.0,
            "sl4wv": 1.0,
            "sl4ch": 1.0,
            "sl4cv": 1.0,
            "bs1x": 1.0,
            "bs1y": 1.0,
            "bs1_det_dist": 1.0,
            "bs1_status": 1.0,
            "bs2x": 1.0,
            "bs2y": 1.0,
            "bs2_det_dist": 1.0,
            "bs2_status": 1.0,
            "diode": 1.0,
            "sample_name": 1.0,
            "sample_description": 1.0,
            "samx": 1.0,
            "samy": 1.0,
            "temp": 1.0
            }
