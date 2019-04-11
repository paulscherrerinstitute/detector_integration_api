import logging
from logging import getLogger
from time import sleep

from detector_integration_api import config
from detector_integration_api.utils.client_disable_wrapper import ClientDisableWrapper

_logger = getLogger(__name__)


def try_catch(func, error_message_prefix):
    def wrapped(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except Exception as e:
            _logger.error(error_message_prefix, e)

    return wrapped


def compare_client_status(status, expected_value):

    _logger.debug("Comparing status '%s' with expected status '%s'.", status, expected_value)

    if status == ClientDisableWrapper.STATUS_DISABLED:
        return True

    if isinstance(expected_value, (tuple, list)):
        return status in expected_value
    else:
        return status == expected_value


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
    _logger.info("Disabling logging on Requests.")

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("bottle").setLevel(logging.WARNING)
