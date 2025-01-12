import copy
from datetime import datetime, timezone
import requests
from requests.auth import HTTPBasicAuth

from project.example_responses.example_data_handler import (OctopusData)


class Octopus:
    def __init__(self, offline_debug, api_key):
        self.offline_debug = offline_debug
        self.api_key = api_key
        self.account_number = "A-3946408C"
        self.base_url = "https://api.octopus.energy"
        self.auth = HTTPBasicAuth(self.api_key, '')

    def get_tariff_data(self):
        if self.offline_debug:
            return copy.deepcopy(OctopusData.agile_tariff())
        else:
            product_code = "AGILE-23-12-06"
            tariff_code = f"E-1R-{product_code}-G"
            tariff_url = f"{self.base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates/"

            # Get the current datetime in UTC
            current_time = datetime.now(timezone.utc)

            # Format the datetime as an ISO 8601 string with UTC indication
            formatted_time = current_time.strftime('%Y-%m-%dT%H:%MZ')

            # parameters = {"period_from": formatted_time}
            # parameters = {"page": 2}
            # response = requests.get(url=tariff_url, params=parameters, auth=self.auth)
            response = requests.get(url=tariff_url, auth=self.auth)

            return response.json()

    def get_account_data(self):
        # https://api.octopus.energy/v1/accounts/< ACCOUNT >/
        if self.offline_debug:
            return copy.deepcopy(OctopusData.agile_tariff())
        else:
            tariff_url = f"{self.base_url}/v1/accounts/{self.account_number}/"
            response = requests.get(url=tariff_url, auth=self.auth)
            return response.json()