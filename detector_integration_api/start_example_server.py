import argparse
import logging

import bottle
from detector_integration_api import config
from detector_integration_api.debug import manager
from detector_integration_api.rest_api.rest_server import register_rest_interface
from tests.utils import MockBackendClient, MockDetectorClient, MockExternalProcessClient

_logger = logging.getLogger(__name__)


def start_integration_server(host, port):

    _logger.info("Starting debug integration REST API.")

    backend_client = MockBackendClient()
    writer_client = MockExternalProcessClient()
    detector_client = MockDetectorClient()

    integration_manager = manager.IntegrationManager(writer_client=writer_client,
                                                     backend_client=backend_client,
                                                     detector_client=detector_client)

    app = bottle.Bottle()
    register_rest_interface(app=app, integration_manager=integration_manager)

    try:
        bottle.run(app=app, host=host, port=port, debug=True)
    finally:
        pass


def main():
    parser = argparse.ArgumentParser(description='Rest API for beamline software')
    parser.add_argument('-i', '--interface', default=config.DEFAULT_SERVER_INTERFACE,
                        help="Hostname interface to bind to")
    parser.add_argument('-p', '--port', default=config.DEFAULT_SERVER_PORT, help="Server port")
    parser.add_argument("--log_level", default=config.DEFAULT_LOGGING_LEVEL,
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                        help="Log level to use.")

    arguments = parser.parse_args()

    # Setup the logging level.
    logging.basicConfig(level=arguments.log_level, format='[%(levelname)s] %(message)s')

    start_integration_server(host=arguments.interface,
                             port=arguments.port)


if __name__ == "__main__":
    main()
