from logging import getLogger

_logger = getLogger(__name__)

writer_statuses = {False: "CONFIGURED", True: "OPEN"}
writer_cfg_params = ["output_file", ]
backend_cfg_params = ["bit_depth", "period", "n_frames"]


class IntegrationManager(object):

    def __init__(self, backend_client, writer_client, detector_client):
        self.backend_client = backend_client
        self.writer_client = writer_client
        self.detector_client = detector_client

        self._last_set_backend_config = {}
        self._last_set_writer_config = {}

    def start_acquisition(self):
        status = self.get_state()

        if status["status"] != "CONFIGURED":
            return {"state": "error", "message": "Cannot open in state %s" % status["status"]}

        self.backend_client.open()
        self.writer_client.start()

    def stop_acquisition(self):
        status = self.get_state()

        if status["status"] != "OPEN":
            return {"state": "error", "message": "Cannot close in state %s" % status["status"]}

        self.backend_client.close()
        self.writer_client.stop()

    def get_acquisition_status(self):

        backend_status = self.backend_client.get_status()
        writer_status = self.writer_client.get_status()["is_running"]

        status = self.interpret_status(backend_status, writer_status)

        return status

    @staticmethod
    def interpret_status(backend, writer):
        if writer == "CONFIGURED":
            if backend != "OPEN":
                return backend
            else:
                return writer
        else:
            return backend

    def get_acquisition_config(self):
        return {"last_set_writer_config": self._last_set_writer_config,
                "last_set_backend_config": self._last_set_backend_config}

    def set_acquisition_config(self, acquisition_config):
        writer_config = {}
        backend_config = {"settings": {}}

        _logger.debug("Configuration: %s" % acquisition_config)

        for k, v in acquisition_config["settings"].items():
            if k in writer_cfg_params:
                writer_config[k] = v
            if k in backend_cfg_params:
                backend_config["settings"][k] = v

        _logger.debug("Configurations for backend and writer: %s %s" % (backend_config, writer_config))

        if "output_file" in writer_config:
            if writer_config["output_file"][-3:] != ".h5":
                writer_config["output_file"] += ".h5"

        self.backend_client.set_config(backend_config)
        self._last_set_backend_config = backend_config

        self.writer_client.set_parameters(writer_config)
        self._last_set_writer_config = writer_config

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
