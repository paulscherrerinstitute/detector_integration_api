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

    def start_acquisition(self):
        status = self.get_state()

        if status["status"] != "CONFIGURED":
            return {"state": "error", "message": "Cannot open in state %s" % status["status"]}
        r = requests.post(_config.backend_url + "/state/open", json={}).text
        _logger.debug("Opening backend got %s" % r)
        if r != "OPEN":
            logger.error("Cannot setart backend, aborting: %s" % r)
            return {"status": "error", "message": r["message"], "state": get_status()}

        r = requests.put(_config.writer_url + "/").text
        if json.loads(r)["status"] != "ok":
            logger.error("Cannot start writer, aborting: %s" % r)
            return {"status": "error", "message": r, "state": get_status()}
        _logger.debug("Opening writer got %s" % r)

    def stop_acquisition(self):
        status = self.get_state()
        if status["status"] != "OPEN":
            return {"state": "error", "message": "Cannot close in state %s" % status["status"]}
        r = requests.post(_config.backend_url + "/state/close", json={}).text
        _logger.debug("Stopping backend got %s" % r)
        if r != "CLOSED" and r != "CLOSING":
            logger.error("Cannot stop backend, aborting: %s" % r)
            return {"status": "error", "message": r, "state": get_status()}

        r = requests.delete(_config.writer_url + "/").text
        if json.loads(r)["status"] != "ok":
            logger.error("Cannot stop writer, aborting: %s" % r)
            return {"status": "error", "message": r["message"], "state": get_status()}
        _logger.debug("Stoppping writer got %s" % r)

    def get_acquisition_status(self):
        global _config
        backend_status = json.loads(requests.get(_config.backend_url + "/state").text)["global_state"]
        writer_status = requests.get(_config.writer_url + "/status").text
        # logger.debug("Writer got %s" % writer_status)
        writer_status = writer_statuses[json.loads(writer_status)["data"]["is_running"]]
        # logger.debug("Writer status %s" % writer_status)
        # print({"status": interpret_status(backend_status, writer_status),
        #        "details": {"backend": backend_status, "writer": writer_status}})
        return {"status": interpret_status(backend_status, writer_status),
                "details": {"backend": backend_status, "writer": writer_status}}

    def get_acquisition_config(self):
        pass

    def set_acquisition_config(self, acquisition_config):
        writer_cfg = {}
        backend_cfg = {"settings": {}}
        logger.debug("Configuration: %s" % cfg)
        for k, v in cfg["settings"].items():
            if k in writer_cfg_params:
                writer_cfg[k] = v
            if k in backend_cfg_params:
                backend_cfg["settings"][k] = v
        logger.debug("Configurations for backend and writer: %s %s" % (backend_cfg, writer_cfg))

        if "output_file" in writer_cfg:
            if writer_cfg["output_file"][-3:] != ".h5":
                writer_cfg["output_file"] += ".h5"

        r = requests.post(_config.backend_url + "/state/configure", json=backend_cfg).text
        logger.debug("Backend cfg got %s" % r)
        if r != "CONFIGURED":
            logger.error("Cannot setup backend parameters, aborting: %s" % r)
            return {"state": _config.status, "message": r}

        r = json.loads(requests.post(_config.writer_url + "/parameters", json=writer_cfg).text)
        logger.debug("Writer cfg got %s" % r)
        if r["status"] != "ok":
            logger.error("Cannot setup writer parameters, aborting: %s" % r)
            return {"state": _config.status, "message": r["message"]}

    def reset(self):
        status = get_status()
        if status["status"] != "CLOSED":
            return {"state": "error", "message": "Cannot reset in state %s" % status["status"]}
        r = requests.post(_config.backend_url + "/state/reset", json={}).text
        logger.debug("Stopping backend got %s" % r)
        if r != "INITIALIZED":
            logger.error("Cannot stop backend, aborting: %s" % r)
            return {"status": "error", "message": r, "state": get_status()}

    def interpret_status(backend, writer):
        logger.debug("Raw statuses: backend %s writer %s" % (backend, writer))
        if writer == "CONFIGURED":
            if backend != "OPEN":
                return backend
            else:
                return writer
        else:
            return backend

    def get_server_info(self):
        pass
