import copy
import requests

from project.example_responses.example_data_handler import *


"""
https://givenergy.cloud/docs/api/v1#introduction
"""

class GivEnergy:
    def __init__(self, offline_debug, api_key):
        self.offline_debug = offline_debug
        self.base_url = 'https://api.givenergy.cloud'
        self.api_key = api_key
        self.system_specs_raw = self.get_system_specifications()
        self.system_specs = {}
        self.inverter_serial_number = self.extract_inverter_serial_number()

    def get_system_specifications(self):
        """
        https://givenergy.cloud/docs/api/v1#communication-device
        """
        if self.offline_debug:
            return copy.deepcopy(GivEnergyData.communication_device())
        else:
            url = f'{self.base_url}/v1/communication-device'
            params = {
                'page': '1',
            }
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            try:
                response = requests.request('GET', url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as http_error:
                raise http_error
            except requests.exceptions.ConnectionError as connection_error:
                raise connection_error
            except requests.exceptions.Timeout as timeout_error:
                raise timeout_error
            except requests.exceptions.RequestException as error:
                raise error

    def extract_inverter_serial_number(self):
        # Extract inverter serial number
        if self.system_specs_raw is not None:
            return self.system_specs_raw['data'][0]['inverter']['serial']

    def get_inverter_systems_data(self):
        """
        https://givenergy.cloud/docs/api/v1#inverter-data-GETinverter--inverter_serial_number--system-data-latest
        """
        if self.offline_debug:
            pass
        else:
            url = f'{self.base_url}/v1/inverter/{self.inverter_serial_number}/system-data/latest'
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            try:
                response = requests.request('GET', url, headers=headers)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as http_error:
                raise http_error
            except requests.exceptions.ConnectionError as connection_error:
                raise connection_error
            except requests.exceptions.Timeout as timeout_error:
                raise timeout_error
            except requests.exceptions.RequestException as error:
                raise error

    def get_energy_usage(self, start_date, end_date, e_types):
        """
        https://givenergy.cloud/docs/api/v1#energy-flow-data-POSTinverter--inverter_serial_number--energy-flows
        """
        if self.offline_debug:
            pass
        else:
            payload = {"start_time": start_date,
                       "end_time": end_date,
                       "grouping": 0,
                       "types": e_types}

            url = f'{self.base_url}/v1/inverter/{self.inverter_serial_number}/energy-flows'
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            try:
                response = requests.request('POST', url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as http_error:
                raise http_error
            except requests.exceptions.ConnectionError as connection_error:
                raise connection_error
            except requests.exceptions.Timeout as timeout_error:
                raise timeout_error
            except requests.exceptions.RequestException as error:
                raise error

    def get_inverter_settings(self):
        """
        https://givenergy.cloud/docs/api/v1#inverter-control-GETinverter--inverter_serial_number--settings
        """
        if self.offline_debug:
            return copy.deepcopy(GivEnergyData.inverter_settings())
        else:
            url = f'{self.base_url}/v1/inverter/{self.inverter_serial_number}/settings'
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'}
            try:
                response = requests.request('GET', url, headers=headers)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as http_error:
                raise http_error
            except requests.exceptions.ConnectionError as connection_error:
                raise connection_error
            except requests.exceptions.Timeout as timeout_error:
                raise timeout_error
            except requests.exceptions.RequestException as error:
                raise error

    def read_inverter_setting(self, setting):
        """
        https://givenergy.cloud/docs/api/v1#inverter-control-POSTinverter--inverter_serial_number--settings--setting_id--read
        """
        if self.offline_debug:
            return copy.deepcopy(GivEnergyData.read_inverter_setting())
        else:
            url = f'{self.base_url}/v1/inverter/{self.inverter_serial_number}/settings/{setting}/read'
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            try:
                response = requests.request('POST', url, headers=headers)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as http_error:
                raise http_error
            except requests.exceptions.ConnectionError as connection_error:
                raise connection_error
            except requests.exceptions.Timeout as timeout_error:
                raise timeout_error
            except requests.exceptions.RequestException as error:
                raise error

    def update_inverter_setting(self, setting, value):
        """
        https://givenergy.cloud/docs/api/v1#inverter-control-POSTinverter--inverter_serial_number--settings--setting_id--write
        """
        if not self.offline_debug:
            url = f'{self.base_url}/v1/inverter/{self.inverter_serial_number}/settings/{setting}/write'
            payload = {"value": f"{value}"}
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'}
            try:
                response = requests.request('POST', url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as http_error:
                raise http_error
            except requests.exceptions.ConnectionError as connection_error:
                raise connection_error
            except requests.exceptions.Timeout as timeout_error:
                raise timeout_error
            except requests.exceptions.RequestException as error:
                raise error

    def extract_system_spec(self):
        battery_voltage = self.system_specs_raw['data'][0]['inverter']['info']['battery'][
            'nominal_voltage']
        battery_capacity_ah = self.system_specs_raw['data'][0]['inverter']['info']['battery'][
            'nominal_capacity']
        battery_capacity_wh = battery_voltage * battery_capacity_ah
        max_charge_rate = self.system_specs_raw['data'][0]['inverter']['info']['max_charge_rate']
        house_avg_base_load = 300

        hours_to_charge = round(battery_capacity_wh / (max_charge_rate - house_avg_base_load), 4)

        self.system_specs = {"battery_spec": {"voltage": battery_voltage,
                                              "amp_hour": battery_capacity_ah,
                                              "watt_hour": battery_capacity_wh,
                                              "max_charge_rate_watts": max_charge_rate,
                                              "hours_to_charge_full": hours_to_charge},
                             "inverter_spec": {},
                             "general_spec": {}
                             }





if __name__ == '__main__':
    offline_debug = False
    giv_energy = GivEnergy(offline_debug, os.environ.get("GE_API_KEY"))
    data = giv_energy.read_inverter_setting(64)
    print(1)

    # "id": 64,
    # "name": "AC Charge 1 Start Time",

    # "id": 65,
    # "name": "AC Charge 1 End Time",

    # "id": 28,
    # "name": "AC Charge 2 Start Time",
    #
    # "id": 29,
    # "name": "AC Charge 2 End Time",

    # "id": 66,
    # "name": "AC Charge Enable",

