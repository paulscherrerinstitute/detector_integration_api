import json
from logging import getLogger

from bottle import request, response

from detector_integration_api.config import ROUTES

_logger = getLogger(__name__)
_audit_logger = getLogger("audit_trail")


def register_rest_interface(app, integration_manager):
    @app.post(ROUTES["start"])
    def start():
        status = integration_manager.start_acquisition()

        return {"state": "ok",
                "status": str(status)}

    @app.post(ROUTES["stop"])
    def stop():
        status = integration_manager.stop_acquisition()

        return {"state": "ok",
                "status": str(status)}

    @app.get(ROUTES["get_status"])
    def get_status():
        return {"state": "ok",
                "status": integration_manager.get_acquisition_status_string()}

    @app.get(ROUTES["get_status_details"])
    def get_status_details():

        return {"state": "ok",
                "status": integration_manager.get_acquisition_status_string(),
                "details": integration_manager.get_status_details()}

    @app.post(ROUTES["set_last_config"])
    def set_last_config():
        status = integration_manager.set_acquisition_config(integration_manager.get_acquisition_config())

        return {"state": "ok",
                "status": str(status),
                "config": integration_manager.get_acquisition_config()}

    @app.get(ROUTES["get_config"])
    def get_config():
        return {"state": "ok",
                "status": integration_manager.get_acquisition_status_string(),
                "config": integration_manager.get_acquisition_config()}

    @app.put(ROUTES["set_config"])
    def set_config():
        new_config = request.json

        status = integration_manager.set_acquisition_config(new_config)

        return {"state": "ok",
                "status": str(status),
                "config": integration_manager.get_acquisition_config()}

    @app.post(ROUTES["update_config"])
    def update_config():
        config_updates = request.json

        status = integration_manager.update_acquisition_config(config_updates)

        return {"state": "ok",
                "status": str(status),
                "config": integration_manager.get_acquisition_config()}

    @app.get(ROUTES["get_detector_value"] + "/<name>")
    def get_detector_value(name):
        value = integration_manager.detector_client.get_value(name)

        return {"state": "ok",
                "status": integration_manager.get_acquisition_status_string(),
                "value": value}

    @app.post(ROUTES["set_detector_value"])
    def set_detector_value():
        parameter_request = request.json

        if not parameter_request:
            raise ValueError("Set detector value JSON request cannot be empty.")

        if "name" not in parameter_request or 'value' not in parameter_request:
            raise ValueError("'name' and 'value' must be set in JSON request.")

        parameter_name = parameter_request["name"]
        parameter_value = parameter_request["value"]

        value = integration_manager.detector_client.set_value(parameter_name, parameter_value, no_verification=True)

        return {"state": "ok",
                "status": integration_manager.get_acquisition_status_string(),
                "value": value}

    @app.post(ROUTES["reset"])
    def reset():
        status = integration_manager.reset()

        return {"state": "ok",
                "status": str(status)}

    @app.get(ROUTES["get_server_info"])
    def get_server_info():
        return {"state": "ok",
                "status": integration_manager.get_acquisition_status_string(),
                "server_info": integration_manager.get_server_info()}

    @app.get(ROUTES["get_metrics"])
    def get_metrics():
        return {"state": "ok",
                "metrics": integration_manager.get_metrics()}

    @app.get(ROUTES["backend_client"] + "/<action>")
    def get_backend_client(action):
        value = integration_manager.backend_client.__getattribute__(action)()
        return {"state": "ok", "value": value}

    @app.put(ROUTES["backend_client"] + "/<action>")
    def put_backend_client(action):
        if action not in ["open", "close", "reset", "config"]:
            raise ValueError("Action %s not supported. Currently supported actions: config" % action)
        new_config = request.json
        if action == "config":
            integration_manager.validator.validate_backend_config(new_config)
            integration_manager.backend_client.set_config(new_config)
            integration_manager._last_set_backend_config = new_config
            return {"state": "ok",
                    "status": integration_manager.backend_client.get_status(),
                    "config": integration_manager.backend_client._last_set_backend_config}
        else:
            integration_manager.backend_client.__getattribute__(action)()
            return {"state": "ok",
                    "status": integration_manager.backend_client.get_status()}

    @app.get(ROUTES["clients_enabled"])
    def get_clients_enabled():
        return {"state": "ok",
                "status": integration_manager.get_clients_enabled(),
                "clients_enabled": integration_manager.get_clients_enabled()}

    @app.post(ROUTES["clients_enabled"])
    def set_clients_enabled():
        config_clients_enable = request.json

        integration_manager.set_clients_enabled(config_clients_enable)

        return {"state": "ok",
                "status": integration_manager.backend_client.get_status(),
                "clients_enabled": integration_manager.get_clients_enabled()}

    @app.error(500)
    def error_handler_500(error):
        response.content_type = 'application/json'
        response.status = 200

        error_text = str(error.exception)

        _logger.error(error_text)
        _audit_logger.error(error_text)

        return json.dumps({"state": "error",
                           "status": error_text})
