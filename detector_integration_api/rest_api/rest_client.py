import requests
from detector_integration_api.rest_api.rest_server import routes


def validate_response(server_response):
    if server_response["state"] != "ok":
        raise Exception("Server exception:\n" + server_response.get("status", "Unknown error occurred."))

    return server_response


class DetectorIntegrationClient(object):
    def __init__(self, api_address):
        self.api_address = api_address.rstrip("/")

    def start(self):
        request_url = self.api_address + routes["start"]

        response = requests.post(request_url).json()

        return validate_response(response)

    def stop(self):
        request_url = self.api_address + routes["stop"]

        response = requests.post(request_url).json()

        return validate_response(response)

    def get_status(self):
        request_url = self.api_address + routes["get_status"]

        response = requests.get(request_url).json()

        return validate_response(response)

    def get_status_details(self):
        request_url = self.api_address + routes["get_status_details"]

        response = requests.get(request_url).json()

        return validate_response(response)

    def get_config(self):
        request_url = self.api_address + routes["get_config"]

        response = requests.get(request_url).json()

        return validate_response(response)

    def set_config(self, configuration):
        request_url = self.api_address + routes["set_config"]

        response = requests.put(request_url, json=configuration).json()

        return validate_response(response)

    def update_config(self, configuration):
        request_url = self.api_address + routes["update_config"]

        response = requests.post(request_url, json=configuration).json()

        return validate_response(response)

    def reset(self):
        request_url = self.api_address + routes["reset"]

        response = requests.post(request_url).json()

        return validate_response(response)

    def get_server_info(self):
        request_url = self.api_address + routes["get_server_info"]

        response = requests.get(request_url).json()

        return validate_response(response)
