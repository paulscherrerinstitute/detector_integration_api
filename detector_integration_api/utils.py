import logging
from logging import getLogger
from time import sleep

from detector_integration_api import config

_logger = getLogger(__name__)


class ClientDisableWrapper(object):

    STATUS_DISABLED = "DISABLED"

    def __init__(self, client, default_enabled=True, client_name="external component"):
        self.client = client
        self.client_enabled = default_enabled
        self.client_name = client_name

    def is_client_enabled(self):
        return self.client_enabled

    def set_client_enabled(self, enabled):
        self.client_enabled = enabled

    def __getattr__(self, attr_name):
        remote_attr = object.__getattribute__(self.client, attr_name)

        if hasattr(remote_attr, '__call__'):

            def gated_function(*args, **kwargs):
                if self.is_client_enabled():

                    try:
                        result = remote_attr(*args, **kwargs)
                        return result
                    except Exception as e:
                        raise RuntimeError("Cannot communicate with %s. Please check the error logs."
                                           % self.client_name) from e

                else:
                    _logger.debug("Object '%s' disabled. Not calling method '%s'.",
                                  type(self.client).__name__, attr_name)

            return gated_function

        else:
            return remote_attr

    def __setattr__(self, key, value):
        if key in ("client_enabled", "client"):
            self.__dict__[key] = value
        else:
            self.client.__setattr__(key, value)


def check_for_target_status(get_status_function, desired_statuses):

    if not isinstance(desired_statuses, (tuple, list)):
        desired_statuses = (desired_statuses,)

    status = None

    for _ in range(config.N_COLLECT_STATUS_RETRY):

        status = get_status_function()

        if status in desired_statuses:
            return status

        sleep(config.N_COLLECT_STATUS_RETRY_DELAY)

    else:

        desired_statuses_text = ", ".join(str(x) for x in desired_statuses)

        _logger.error("Trying to reach one of the statuses '%s' but got '%s'.",
                      desired_statuses_text, status)

        raise ValueError("Cannot reach desired status '%s'. Current status '%s'. "
                         "Try to reset or get_status_details for more info." %
                         (desired_statuses_text, status))


def turn_off_requests_logging():
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
