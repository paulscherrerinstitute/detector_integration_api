from detector_integration_api.client.detector_cli_client import DetectorClient
from sls_detector import Eiger


class EigerClientWrapper(object):
    def __init__(self):
        self.new_client = Eiger()
        self.old_client = DetectorClient()

    def start(self):
        self.new_client.start_detector()

    def stop(self):
        self.new_client.stop_detector()

    def set_config(self, configuration):
        self.old_client.set_config(configuration)

    def get_status(self):
        return self.new_client.status

    def set_threshold(self, energy):
        self.new_client.threshold = energy
