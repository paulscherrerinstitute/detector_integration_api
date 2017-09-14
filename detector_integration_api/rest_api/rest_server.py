from logging import getLogger

from bottle import request, response

_logger = getLogger(__name__)

routes = {
    "start": "/api/v1/start",
    "stop": "/api/v1/stop",
    "reset": "/api/v1/reset",

    "get_status": "/api/v1/status",
    "get_config": "/api/v1/config",
    "set_config": "/api/v1/config",
    "update_config": "/api/v1/config",

    "get_server_info": "/api/v1/info",
}


def register_rest_interface(app, integration_manager):
    @app.post(routes["start"])
    def start():
        integration_manager.start_acquisition()

        return {"state": "ok",
                "status": integration_manager.get_acquisition_status()}

    @app.post(routes["stop"])
    def stop():
        integration_manager.stop_acquisition()

        return {"state": "ok",
                "status": integration_manager.get_acquisition_status()}

    @app.get(routes["get_status"])
    def get_status():
        return {"state": "ok",
                "status": integration_manager.get_acquisition_status()}

    @app.get(routes["get_config"])
    def get_config():
        return {"state": "ok",
                "status": integration_manager.get_acquisition_status(),
                "config": integration_manager.get_acquisition_config()}

    @app.put(routes["set_config"])
    def set_config():
        new_config = request.json

        if {"writer", "backend", "detector"} != set(new_config):
            raise ValueError("Specify config JSON with 3 root elements: 'writer', 'backend', 'detector'.")

        integration_manager.set_acquisition_config(new_config["writer"], new_config["backend"], new_config["detector"])

        return {"state": "ok",
                "status": integration_manager.get_acquisition_status(),
                "config": integration_manager.get_acquisition_config()}

    @app.post(routes["update_config"])
    def update_config():
        config_updates = request.json

        current_config = integration_manager.get_acquisition_config()

        def update_config_section(section_name):
            if section_name in config_updates:
                current_config[section_name].update(config_updates[section_name])

        update_config_section("writer")
        update_config_section("backend")
        update_config_section("detector")

        integration_manager.set_acquisition_config(current_config["writer"],
                                                   current_config["backend"],
                                                   current_config["detector"])

        return {"state": "ok",
                "status": integration_manager.get_acquisition_status(),
                "config": integration_manager.get_acquisition_config()}

    @app.post(routes["reset"])
    def reset():
        integration_manager.reset()

        return {"state": "ok",
                "status": integration_manager.get_acquisition_status()}

    @app.get(routes["get_server_info"])
    def get_server_info():
        return {"state": "ok",
                "server_info": integration_manager.get_server_info()}

    @app.error(500)
    def error_handler_500(error):
        response.content_type = 'application/json'
        response.status = 200

        error_text = str(error.exception)

        _logger.error(error_text)

        return {"state": "error",
                "status": error_text}

