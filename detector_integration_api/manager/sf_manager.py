from copy import copy
from enum import Enum
from logging import getLogger

_logger = getLogger(__name__)
_audit_logger = getLogger("audit_trail")


class IntegrationStatus(Enum):
    INITIALIZED = "initialized",
    CONFIGURED = "configured",
    RUNNING = "running",
    DETECTOR_STOPPED = "detector_stopped",
    ERROR = "error"


class IntegrationManager(object):
    def __init__(self, backend_client, writer_client, detector_client, bsread_client, validator):
        self.backend_client = backend_client
        self.writer_client = writer_client
        self.detector_client = detector_client
        self.bsread_client = bsread_client
        self.validator = validator

        _audit_logger.info("Setting up integration manager to:\n"
                           "Backend address: %s\n"
                           "Writer address: %s\n"
                           "bsread address: %s\n",
                           self.backend_client.backend_url,
                           self.writer_client._api_address.format(url=""),
                           self.bsread_client._api_address.format(url=""))

        self._last_set_backend_config = {}
        self._last_set_writer_config = {}
        self._last_set_detector_config = {}
        self._last_set_bsread_config = {}

        self.last_config_successful = False

    def start_acquisition(self):
        _audit_logger.info("Starting acquisition.")

        status = self.get_acquisition_status()
        if status != IntegrationStatus.CONFIGURED:
            raise ValueError("Cannot start acquisition in %s state. Please configure first." % status)

        self.bsread_client.start()
        self.backend_client.open()
        self.writer_client.start()
        self.detector_client.start()

    def stop_acquisition(self):
        _audit_logger.info("Stopping acquisition.")

        status = self.get_acquisition_status()

        if status == IntegrationStatus.RUNNING:
            self.detector_client.stop()
            self.backend_client.close()
            self.writer_client.stop()
            self.bsread_client.stop()

        self.reset()

    def get_acquisition_status(self):
        status = self.validator.interpret_status(self.get_status_details())

        # There is no way of knowing if the detector is configured as the user desired.
        # We have a flag to check if the user config was passed on to the detector.
        if status == IntegrationStatus.CONFIGURED and self.last_config_successful is False:
            return IntegrationStatus.ERROR

        return status

    def get_acquisition_status_string(self):
        return str(self.get_acquisition_status())

    def get_status_details(self):
        writer_status = self.writer_client.get_status()["is_running"]
        backend_status = self.backend_client.get_status()
        detector_status = self.detector_client.get_status()
        bsread_status = self.bsread_client.get_status()["is_running"]

        _logger.debug("Detailed status requested:\nWriter: %s\nBackend: %s\nDetector: %s\nbsread: %s",
                      writer_status, backend_status, detector_status, bsread_status)

        return {"writer": writer_status,
                "backend": backend_status,
                "detector": detector_status,
                "bsread": bsread_status}

    def get_acquisition_config(self):
        # Always return a copy - we do not want this to be updated.
        return {"writer": copy(self._last_set_writer_config),
                "backend": copy(self._last_set_backend_config),
                "detector": copy(self._last_set_detector_config),
                "bsread": copy(self._last_set_bsread_config)}

    def set_acquisition_config(self, new_config):
        if {"writer", "backend", "detector", "bsread"} != set(new_config):
            raise ValueError("Specify config JSON with 4 root elements: 'writer', 'backend', 'detector', 'bsread'.")

        writer_config = new_config["writer"]
        backend_config = new_config["backend"]
        detector_config = new_config["detector"]
        bsread_config = new_config["bsread"]

        status = self.get_acquisition_status()

        self.last_config_successful = False

        if status not in (IntegrationStatus.INITIALIZED, IntegrationStatus.CONFIGURED):
            raise ValueError("Cannot set config in %s state. Please reset first." % status)

        # The backend is configurable only in the INITIALIZED state.
        if status == IntegrationStatus.CONFIGURED:
            _logger.debug("Integration status is %s. Resetting before applying config.", status)
            self.reset()

        _audit_logger.info("Set acquisition configuration:\n"
                           "Writer config: %s\n"
                           "Backend config: %s\n"
                           "Detector config: %s\n",
                           writer_config, backend_config, detector_config)

        # Before setting the new config, validate the provided values. All must be valid.
        self.validator.validate_writer_config(writer_config)
        self.validator.validate_backend_config(backend_config)
        self.validator.validate_detector_config(detector_config)
        self.validator.validate_configs_dependencies(writer_config, backend_config, detector_config, bsread_config)

        self.backend_client.set_config(backend_config)
        self._last_set_backend_config = backend_config

        self.writer_client.set_parameters(writer_config)
        self._last_set_writer_config = writer_config

        self.detector_client.set_config(detector_config)
        self._last_set_detector_config = detector_config

        self.bsread_client.set_parameters(bsread_config)
        self._last_set_bsread_config = bsread_config

        self.last_config_successful = True

    def update_acquisition_config(self, config_updates):
        current_config = self.get_acquisition_config()

        _logger.debug("Updating acquisition config: %s", current_config)

        def update_config_section(section_name):
            if section_name in config_updates and config_updates.get(section_name):
                current_config[section_name].update(config_updates[section_name])

        update_config_section("writer")
        update_config_section("backend")
        update_config_section("detector")
        update_config_section("bsread")

        self.set_acquisition_config(current_config)

    def reset(self):
        _audit_logger.info("Resetting integration api.")

        self.last_config_successful = False

        self.detector_client.stop()
        self.backend_client.reset()
        self.writer_client.reset()
        self.bsread_client.reset()

    def get_server_info(self):
        return {
            "clients": {
                "backend_url": self.backend_client.backend_url,
                "writer_url": self.writer_client._api_address.format(url=""),
                "bsread_url": self.bsread_client._api_address.format(url="")},
            "validator": self.validator.__name__,
            "last_config_successful": self.last_config_successful
        }

    def get_metrics(self):
        # Always return a copy - we do not want this to be updated.
        return {"writer": {},
                "backend": self.backend_client.get_metrics(),
                "detector": {},
                "bsread": {}}
