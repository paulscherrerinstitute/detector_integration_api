from copy import copy
from logging import getLogger
from time import sleep

from detector_integration_api import config
from detector_integration_api.deployment.csaxs import csaxs_validation_eiger9m
from detector_integration_api.deployment.csaxs.csaxs_validation_eiger9m import IntegrationStatus
from detector_integration_api.utils import ClientDisableWrapper

_logger = getLogger(__name__)
_audit_logger = getLogger("audit_trail")


class IntegrationManager(object):
    def __init__(self, backend_client, writer_client, detector_client):
        self.backend_client = ClientDisableWrapper(backend_client)
        self.writer_client = ClientDisableWrapper(writer_client)
        self.detector_client = ClientDisableWrapper(detector_client)

        self._last_set_backend_config = {}
        self._last_set_writer_config = {}
        self._last_set_detector_config = {}

        self.last_config_successful = False

    def check_for_target_status(self, desired_status):

        status = None

        for _ in range(config.N_COLLECT_STATUS_RETRY):

            status = self.get_acquisition_status()

            if status == desired_status:
                return status

            sleep(config.N_COLLECT_STATUS_RETRY_DELAY)

        else:
            status_details = self.get_status_details()

            _logger.error("Trying to reach status '%s' but got '%s'. Status details: %s",
                          desired_status, status, status_details)

            raise ValueError("Cannot reach desired status '%s'. Current status '%s'. "
                             "Try to reset or get_status_details for more info." %
                             (desired_status, status))

    def start_acquisition(self):
        _audit_logger.info("Starting acquisition.")

        status = self.get_acquisition_status()
        if status != IntegrationStatus.CONFIGURED:
            raise ValueError("Cannot start acquisition in %s state. Please configure first." % status)

        _audit_logger.info("backend_client.open()")
        self.backend_client.open()

        _audit_logger.info("writer_client.start()")
        self.writer_client.start()

        _audit_logger.info("detector_client.start()")
        self.detector_client.start()

        return self.check_for_target_status(IntegrationStatus.RUNNING)

    def stop_acquisition(self):
        _audit_logger.info("Stopping acquisition.")

        status = self.get_acquisition_status()

        if status == IntegrationStatus.RUNNING:
            _audit_logger.info("detector_client.stop()")
            self.detector_client.stop()

            _audit_logger.info("backend_client.close()")
            self.backend_client.close()

            _audit_logger.info("writer_client.stop()")
            self.writer_client.stop()

        return self.reset()

    def get_acquisition_status(self):
        status = csaxs_validation_eiger9m.interpret_status(self.get_status_details())

        # There is no way of knowing if the detector is configured as the user desired.
        # We have a flag to check if the user config was passed on to the detector.
        if status == IntegrationStatus.CONFIGURED and self.last_config_successful is False:
            return IntegrationStatus.ERROR

        return status

    def get_acquisition_status_string(self):
        return str(self.get_acquisition_status())

    def get_status_details(self):
        _audit_logger.info("Getting status details.")

        _audit_logger.info("writer_client.get_status()")
        writer_status = self.writer_client.get_status() \
            if self.writer_client.is_client_enabled() else ClientDisableWrapper.STATUS_DISABLED

        _audit_logger.info("backend_client.get_status()")
        backend_status = self.backend_client.get_status() \
            if self.backend_client.is_client_enabled() else ClientDisableWrapper.STATUS_DISABLED

        _audit_logger.info("detector_client.get_status()")
        detector_status = self.detector_client.get_status() \
            if self.detector_client.is_client_enabled() else ClientDisableWrapper.STATUS_DISABLED

        _logger.debug("Detailed status requested:\nWriter: %s\nBackend: %s\nDetector: %s",
                      writer_status, backend_status, detector_status)

        return {"writer": writer_status,
                "backend": backend_status,
                "detector": detector_status}

    def get_acquisition_config(self):
        # Always return a copy - we do not want this to be updated.
        return {"writer": copy(self._last_set_writer_config),
                "backend": copy(self._last_set_backend_config),
                "detector": copy(self._last_set_detector_config)}

    def set_acquisition_config(self, new_config):

        if all(item in {"writer", "backend", "detector"} for item in new_config):
            raise ValueError("Specify config JSON with 3 root elements: 'writer', 'backend', 'detector'.")

        writer_config = new_config["writer"]
        backend_config = new_config["backend"]
        detector_config = new_config["detector"]

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
        if self.writer_client.client_enabled:
            csaxs_validation_eiger9m.validate_writer_config(writer_config)

        if self.backend_client.client_enabled:
            csaxs_validation_eiger9m.validate_backend_config(backend_config)

        if self.detector_client.client_enabled:
            csaxs_validation_eiger9m.validate_detector_config(detector_config)

        csaxs_validation_eiger9m.validate_configs_dependencies(writer_config, backend_config, detector_config)

        _audit_logger.info("backend_client.set_config(backend_config)")
        self.backend_client.set_config(backend_config)
        self._last_set_backend_config = backend_config

        _audit_logger.info("writer_client.set_parameters(writer_config)")
        self.writer_client.set_parameters(writer_config)
        self._last_set_writer_config = writer_config

        _audit_logger.info("detector_client.set_config(detector_config)")
        self.detector_client.set_config(detector_config)
        self._last_set_detector_config = detector_config

        self.last_config_successful = True

        return self.check_for_target_status(IntegrationStatus.CONFIGURED)

    def update_acquisition_config(self, config_updates):
        current_config = self.get_acquisition_config()

        _logger.debug("Updating acquisition config: %s", current_config)

        def update_config_section(section_name):
            if section_name in config_updates and config_updates.get(section_name):
                current_config[section_name].update(config_updates[section_name])

        update_config_section("writer")
        update_config_section("backend")
        update_config_section("detector")

        self.set_acquisition_config(current_config)

        return self.check_for_target_status(IntegrationStatus.CONFIGURED)

    def set_clients_enabled(self, client_status):

        if "backend" in client_status:
            self.backend_client.set_client_enabled(client_status["backend"])
            _logger.info("Backend client enable=%s.", self.backend_client.is_client_enabled())

        if "writer" in client_status:
            self.writer_client.set_client_enabled(client_status["writer"])
            _logger.info("Writer client enable=%s.", self.writer_client.is_client_enabled())

        if "detector" in client_status:
            self.detector_client.set_client_enabled(client_status["detector"])
            _logger.info("Detector client enable=%s.", self.detector_client.is_client_enabled())

    def get_clients_enabled(self):
        return {"backend": self.backend_client.is_client_enabled(),
                "writer": self.writer_client.is_client_enabled(),
                "detector": self.detector_client.is_client_enabled()}

    def reset(self):
        _audit_logger.info("Resetting integration api.")

        self.last_config_successful = False

        _audit_logger.info("detector_client.stop()")
        self.detector_client.stop()

        _audit_logger.info("backend_client.reset()")
        self.backend_client.reset()

        _audit_logger.info("writer_client.reset()")
        self.writer_client.reset()

        return self.check_for_target_status(IntegrationStatus.INITIALIZED)

    def get_server_info(self):
        return {
            "clients": {
                "backend_url": self.backend_client.backend_url,
                "writer_url": self.writer_client._api_address.format(url="")},
            "clients_enabled": self.get_clients_enabled(),
            "validator": "NOT IMPLEMENTED",
            "last_config_successful": self.last_config_successful
        }

    def get_metrics(self):
        # Always return a copy - we do not want this to be updated.
        return {"writer": self.writer_client.get_statistics(),
                "backend": self.backend_client.get_metrics(),
                "detector": {}}
