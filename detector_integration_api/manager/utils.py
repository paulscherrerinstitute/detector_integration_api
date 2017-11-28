from logging import getLogger

_logger = getLogger(__name__)


class ClientDisableWrapper(object):

    STATUS_DISABLED = "DISABLED"

    def __init__(self, client, default_enabled=True):
        self.client = client
        self.client_enabled = default_enabled

    def is_client_enabled(self):
        return self.client_enabled

    def set_client_enabled(self, enabled):
        self.client_enabled = enabled

    def __getattr__(self, attr_name):
        remote_attr = object.__getattribute__(self.client, attr_name)

        if hasattr(remote_attr, '__call__'):

            def gated_function(*args, **kwargs):
                if self.is_client_enabled():
                    result = remote_attr(*args, **kwargs)
                    return result
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
