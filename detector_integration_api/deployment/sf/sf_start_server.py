import argparse
import logging

import bottle
from mflow_nodes import NodeClient

from detector_integration_api import config
from detector_integration_api.client.backend_rest_client import BackendClient
from detector_integration_api.client.detector_cli_client import DetectorClient
from detector_integration_api.deployment.sf import sf_manager
from detector_integration_api.rest_api.rest_server import register_rest_interface, register_debug_rest_interface

_logger = logging.getLogger(__name__)


def start_integration_server(host, port, backend_url, writer_url, writer_instance_name,
                             bsread_url, bsread_instance_name, disable_bsread):
    _logger.info("Starting integration REST API with:\nBackend url: %s\nWriter url: %s\nWriter instance name: %s\n",
                 backend_url, writer_url, writer_instance_name)

    backend_client = BackendClient(backend_url)
    writer_client = NodeClient(writer_url, writer_instance_name)
    bsread_client = NodeClient(bsread_url, bsread_instance_name)
    detector_client = DetectorClient()

    integration_manager = sf_manager.IntegrationManager(writer_client=writer_client,
                                                        backend_client=backend_client,
                                                        detector_client=detector_client,
                                                        bsread_client=bsread_client)

    _logger.info("Bsread writer disabled at startup: %s", disable_bsread)
    if disable_bsread:
        integration_manager.set_clients_enabled({"bsread": False})

    app = bottle.Bottle()
    register_rest_interface(app=app, integration_manager=integration_manager)
    register_debug_rest_interface(app=app, integration_manager=integration_manager)

    try:
        bottle.run(app=app, host=host, port=port)
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
    parser.add_argument("-b", "--backend_url", default=config.DEFAULT_BACKEND_URL,
                        help="Backend REST API url.")
    parser.add_argument("-w", "--writer_url", default=config.DEFAULT_WRITER_URL,
                        help="Writer REST API url.")
    parser.add_argument("-s", "--bsread_url", default=config.DEFAULT_BSREAD_URL,
                        help="Writer REST API url.")
    parser.add_argument("--writer_instance_name", default=config.DEFAULT_WRITER_INSTANCE_NAME,
                        help="Writer instance name.")
    parser.add_argument("--bsread_instance_name", default=config.DEFAULT_BSREAD_INSTANCE_NAME,
                        help="Writer instance name.")
    parser.add_argument("--disable_bsread", action='store_true',
                        help="Disable the bsread writer at startup.")

    arguments = parser.parse_args()

    # Setup the logging level.
    logging.basicConfig(level=arguments.log_level, format='[%(levelname)s] %(message)s')

    start_integration_server(arguments.interface, arguments.port,
                             arguments.backend_url,
                             arguments.writer_url, arguments.writer_instance_name,
                             arguments.bsread_url, arguments.bsread_instance_name,
                             arguments.disable_bsread)


if __name__ == "__main__":
    main()
