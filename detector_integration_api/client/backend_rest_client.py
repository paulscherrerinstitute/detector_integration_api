from logging import getLogger

import requests

from detector_integration_api import config

_logger = getLogger(__name__)


class BackendClient(object):
    def __init__(self, backend_url):
        self.backend_url = backend_url.rstrip("/") + config.BACKEND_URL_SUFFIX

    def open(self):
        response_text = requests.post(self.backend_url + "/state/open", json={}).text

        _logger.debug("Opening backend got %s" % response_text)

        if response_text != "OPEN":
            raise ValueError("Cannot start backend, aborting: %s" % response_text)

        return response_text

    def close(self):
        _logger.debug("Stopping backend.")

        response_text = requests.post(self.backend_url + "/state/close", json={}).text

        _logger.debug("Response from backend: %s" % response_text)

        if response_text not in ("CLOSED", "CLOSING"):
            raise ValueError("Cannot stop backend, aborting: %s" % response_text)

    def get_status(self):
        return requests.get(self.backend_url + "/state").json()["global_state"]

    def reset(self):
        _logger.debug("Resetting backend.")

        response_text = requests.post(self.backend_url + "/state/reset", json={}).text

        _logger.debug("Response from backend: %s" % response_text)

    def set_config(self, configuration):
        _logger.debug("Configuring backend.")

        response_text = requests.post(self.backend_url + "/state/configure", json={"settings": configuration}).text

        _logger.debug("Response from backend %s" % response_text)

        if response_text != "CONFIGURED":
            raise ValueError("Cannot setup backend parameters, aborting: %s" % response_text)

    def get_metrics(self, metrics=["received_frames", "sent_frames"]):
        _logger.debug("Getting backend metrics.")
        # TODO: do a default selection here
        answer = requests.get(self.backend_url + "/metrics").json()["value"]["backend"]
        # selecting answers
        if metrics != []:
            ret = {k: answer.get(k, None) for k in metrics}
        else:
            ret = answer

        return ret
