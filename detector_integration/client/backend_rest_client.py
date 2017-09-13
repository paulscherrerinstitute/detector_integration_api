from logging import getLogger

import requests

_logger = getLogger(__name__)


class BackendClient(object):
    def __init__(self, backend_url):
        self.backend_url = backend_url.rstrip("/")

    def open(self):
        response_text = requests.post(self.backend_url + "/state/open", json={}).text

        _logger.debug("Opening backend got %s" % response_text)

        if response_text != "OPEN":
            raise ValueError("Cannot start backend, aborting: %s" % response_text)

        return response_text

    def close(self):
        response_text = requests.post(self.backend_url + "/state/close", json={}).text

        _logger.debug("Stopping backend got %s" % response_text)

        if response_text not in ("CLOSED", "CLOSING"):
            raise ValueError("Cannot stop backend, aborting: %s" % response_text)

    def get_status(self):
        return requests.get(self.backend_url + "/state").json()["global_state"]

    def reset(self):
        response_text = requests.post(self.backend_url.backend_url + "/state/reset", json={}).text

        _logger.debug("Resetting backend got %s" % response_text)

    def set_config(self, configuration):
        response_text = requests.post(self.backend_url + "/state/configure", json=configuration).text

        _logger.debug("Backend cfg got %s" % response_text)

        if response_text != "CONFIGURED":
            raise ValueError("Cannot setup backend parameters, aborting: %s" % response_text)