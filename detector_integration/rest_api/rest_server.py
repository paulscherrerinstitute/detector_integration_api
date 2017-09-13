from bottle import request

routes = {
    "start": "/api/v1/open",
    "stop": "/api/v1/close",
    "get_status": "/api/v1/state",
    "get_config": "/api/v1/configure",
    "set_config": "/api/v1/configure",
    "reset": "/api/v1/reset",

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

    @app.post(routes["set_config"])
    def set_config():

        integration_manager.set_acquisition_config(request.json)

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
