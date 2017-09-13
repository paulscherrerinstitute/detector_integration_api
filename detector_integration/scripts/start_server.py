import argparse
import logging

import bottle

from detector_integration import config
from detector_integration.rest_server import register_rest_interface

_logger = logging.getLogger(__name__)


def start_integration_server(host, port):

    app = bottle.Bottle()
    register_rest_interface(app=app)

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
    arguments = parser.parse_args()

    # Setup the logging level.
    logging.basicConfig(level=arguments.log_level, format='[%(levelname)s] %(message)s')

    start_integration_server(arguments.interface, arguments.port)

if __name__ == "__main__":
    main()
