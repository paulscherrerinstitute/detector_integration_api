import argparse
import logging

import bottle
from mflow_nodes import NodeClient

from detector_integration import config
from detector_integration.client.backend_rest_client import BackendClient
from detector_integration.client.detector_cli_client import DetectorClient
from detector_integration.manager import IntegrationManager
from detector_integration.rest_api.rest_server import register_rest_interface

_logger = logging.getLogger(__name__)


def start_integration_server(host, port, backend_url, writer_url, writer_instance_name):
    _logger.debug("Starting integration REST API with:\nBackend url: %s\nWriter url: %\nWriter instance name: %s\n",
                  backend_url, writer_url, writer_instance_name)

    detector_client = DetectorClient()
    backend_client = BackendClient(backend_url)
    writer_client = NodeClient(writer_url, writer_instance_name)

    integration_manager = IntegrationManager(writer_client, backend_client, detector_client)

    app = bottle.Bottle()
    register_rest_interface(app=app, integration_manager=integration_manager)

    try:
        bottle.run(app=app, host=host, port=port)
    finally:
        pass


def main():
    parser = argparse.ArgumentParser(description='Rest API for beamline software')
    parser.add_argument('-i', '--interface', default='0.0.0.0', help="Hostname interface to bind to")
    parser.add_argument('-p', '--port', default=8000, help="Server port")
    parser.add_argument("--log_level", default=config.DEFAULT_LOGGING_LEVEL,
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                        help="Log level to use.")
    parser.add_argument("-b", "--backend_url", default=config.DEFAULT_BACKEND_URL,
                        help="Backend REST API url.")
    parser.add_argument("-w", "--writer_url", default=config.DEFAULT_WRITER_URL,
                        help="Writer REST API url.")
    parser.add_argument("--writer_instance_name", default=config.DEFAULT_WRITER_INSTANCE_NAME,
                        help="Writer instance name.")

    arguments = parser.parse_args()

    # Setup the logging level.
    logging.basicConfig(level=arguments.log_level, format='[%(levelname)s] %(message)s')

    start_integration_server(arguments.interface, arguments.port,
                             arguments.backend_url, arguments.writer_url, arguments.writer_instance_name)

if __name__ == "__main__":
    main()
