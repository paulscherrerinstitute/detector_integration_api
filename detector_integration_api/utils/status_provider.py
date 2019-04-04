from logging import getLogger

from detector_integration_api.validation import IntegrationStatus
from detector_integration_api.utils.client_disable_wrapper import ClientDisableWrapper

_audit_logger = getLogger("audit_trail")
_logger = getLogger(__name__)


class StatusProvider(object):
    def __init__(self, backend_client, writer_client, detector_client):
        self.backend_client = backend_client
        self.writer_client = writer_client
        self.detector_client = detector_client

    def get_quick_status_details(self):

        _logger.info("Getting quick status details.")

        _audit_logger.info("writer_client.get_status()")
        try:
            writer_status = self.writer_client.get_status() \
                if self.writer_client.is_client_enabled() else ClientDisableWrapper.STATUS_DISABLED
        except:
            writer_status = IntegrationStatus.COMPONENT_NOT_RESPONDING

        backend_status = None
        detector_status = None

        _logger.debug("Detailed status requested:\nWriter: %s\nBackend: %s\nDetector: %s",
                      writer_status, backend_status, detector_status)

        return {"writer": writer_status,
                "backend": backend_status,
                "detector": detector_status}

    def get_complete_status_details(self):

        _logger.info("Getting complete status details.")

        _audit_logger.info("writer_client.get_status()")
        try:
            writer_status = self.writer_client.get_status() \
                if self.writer_client.is_client_enabled() else ClientDisableWrapper.STATUS_DISABLED
        except:
            writer_status = IntegrationStatus.COMPONENT_NOT_RESPONDING

        _audit_logger.info("backend_client.get_status()")
        try:
            backend_status = self.backend_client.get_status() \
                if self.backend_client.is_client_enabled() else ClientDisableWrapper.STATUS_DISABLED
        except:
            backend_status = IntegrationStatus.COMPONENT_NOT_RESPONDING

        _audit_logger.info("detector_client.get_status()")
        try:
            detector_status = self.detector_client.get_status() \
                if self.detector_client.is_client_enabled() else ClientDisableWrapper.STATUS_DISABLED
        except:
            detector_status = IntegrationStatus.COMPONENT_NOT_RESPONDING

        _logger.debug("Detailed status requested:\nWriter: %s\nBackend: %s\nDetector: %s",
                      writer_status, backend_status, detector_status)

        return {"writer": writer_status,
                "backend": backend_status,
                "detector": detector_status}
