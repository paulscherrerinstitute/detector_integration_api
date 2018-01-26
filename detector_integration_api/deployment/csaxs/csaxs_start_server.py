import argparse
import logging

import bottle

from detector_integration_api import config
from detector_integration_api.client.backend_rest_client import BackendClient
from detector_integration_api.client.cpp_writer_client import CppWriterClient
from detector_integration_api.client.detector_cli_client import DetectorClient
from detector_integration_api.deployment.csaxs import csaxs_manager
from detector_integration_api.rest_api.rest_server import register_rest_interface

_logger = logging.getLogger(__name__)


def start_integration_server(host, port, backend_api_url, backed_stream_url, writer_port):
    _logger.info("Starting integration REST API with:\nBackend api url: %s\nBackend stream url: %s\nWriter port: %s",
                 backend_api_url, backed_stream_url, writer_port)

    backend_client = BackendClient(backend_api_url)
    writer_client = CppWriterClient(backed_stream_url, writer_port)
    detector_client = DetectorClient()

    integration_manager = csaxs_manager.IntegrationManager(writer_client=writer_client,
                                                           backend_client=backend_client,
                                                           detector_client=detector_client)

    app = bottle.Bottle()
    register_rest_interface(app=app, integration_manager=integration_manager)

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
    parser.add_argument("-s", "--backend_stream", default="tcp://10.30.10.3:40000",
                        help="Output stream address from the backend.")
    parser.add_argument("-b", "--backend_url", default="http://xbl-daq-28:8080",
                        help="Backend REST API url.")
    parser.add_argument("-w", "--writer_port", default=10000,
                        help="Writer REST API port.")

    arguments = parser.parse_args()

    # Setup the logging level.
    logging.basicConfig(level=arguments.log_level, format='[%(levelname)s] %(message)s')

    start_integration_server(arguments.interface, arguments.port,
                             backend_api_url=arguments.backend_url,
                             backend_stream_url=arguments.backend_stream,
                             writer_port=arguments.writer_port)


if __name__ == "__main__":
    main()
