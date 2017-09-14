from copy import copy
from logging import getLogger

_logger = getLogger(__name__)


class IntegrationManager(object):

    def __init__(self, backend_client, writer_client, detector_client, validator):
        self.backend_client = backend_client
        self.writer_client = writer_client
        self.detector_client = detector_client
        self.validator = validator

        self._last_set_backend_config = {}
        self._last_set_writer_config = {}
        self._last_set_detector_config = {}

    def start_acquisition(self):
        status = self.get_state()

        if status["status"] != "CONFIGURED":
            return {"state": "error", "message": "Cannot open in state %s" % status["status"]}

        self.backend_client.open()
        self.writer_client.start()
        self.detector_client.acquire()

    def stop_acquisition(self):
        status = self.get_state()

        if status["status"] != "OPEN":
            return {"state": "error", "message": "Cannot close in state %s" % status["status"]}

        self.backend_client.close()
        self.writer_client.stop()

    def get_acquisition_status(self):

        writer_status = self.writer_client.get_status()["is_running"]
        backend_status = self.backend_client.get_status()
        detector_status = self.detector_client.get_status()

        status = self.validator.interpret_status(writer_status, backend_status, detector_status)

        return status

    def get_acquisition_config(self):
        # Always return a copy - we do not want this to be updated.
        return {"writer": copy(self._last_set_writer_config),
                "backend": copy(self._last_set_backend_config),
                "detector": copy(self._last_set_detector_config)}

    def set_acquisition_config(self, writer_config, backend_config, detector_config):
        _logger.debug("Set acquisition configuration:\n"
                      "Writer config: %s\n"
                      "Backend config: %s\n",
                      "Detector config: %s" %
                      (writer_config, backend_config, detector_config))

        # Before setting the new config, validate the provided values. All must be valid.
        self.validator.validate_writer_config(writer_config)
        self.validator.validate_backend_config(backend_config)
        self.validator.validate_detector_config(detector_config)

        self.backend_client.set_config(backend_config)
        self._last_set_backend_config = backend_config

        self.writer_client.set_parameters(writer_config)
        self._last_set_writer_config = writer_config

        self.detector_client.set_config(detector_config)
        self._last_set_detector_config = detector_config

    def reset(self):
        status = self.get_status()

        if status["status"] != "CLOSED":
            return {"state": "error", "message": "Cannot reset in state %s" % status["status"]}

        self.backend_client.reset()

        if r != "INITIALIZED":
            logger.error("Cannot stop backend, aborting: %s" % r)
            return {"status": "error", "message": r, "state": get_status()}

    def get_server_info(self):
        pass
