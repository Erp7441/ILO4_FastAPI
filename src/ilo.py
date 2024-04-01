import requests
import json
from src.config import ilo_settings
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)


def _get_headers(token: str = None):
    if token is None:
        return {
            'Content-Type': 'application/json',
            'OData-Version': '4.0'
        }
    return {
        'Content-Type': 'application/json',
        'OData-Version': '4.0',
        'X-Auth-Token': token
    }


class IloApi:

    def __init__(self):
        self.last_response_code = None
        self.last_action_response_code = None
        self.settings = ilo_settings
        self.token = None
        self.session_location = None
        self.token_headers = None

    def _get_auth_token(self):
        headers = _get_headers()

        # Define the URL for the session service
        url = f'https://{self.settings.IP}/redfish/v1/SessionService/Sessions/'

        # Define the body of the request
        body = {
            'UserName': self.settings.USER_NAME,
            'Password': self.settings.PASSWORD
        }

        # Send the POST request to create a new session
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        return response

    def _login(self):
        if self.token is not None or self.session_location is not None or self.token_headers is not None:
            self._logout()

        login_response = self._get_auth_token()
        if login_response.status_code != 200:
            self.last_response_code = login_response.status_code
            pass  # TODO:: Handle errors

        self.token = login_response.headers['X-Auth-Token']
        self.session_location = login_response.headers['Location']
        self.token_headers = _get_headers(self.token)
        return self.token_headers

    def _logout(self):
        delete_response = requests.delete(self.session_location, headers=self.token_headers, verify=False)
        self.token_headers = None
        self.session_location = None
        self.token = None
        self.last_response_code = delete_response.status_code

    def get_info(self):
        headers = self._login()

        url = f'https://{self.settings.IP}/redfish/v1/Systems/1'
        response = requests.get(url, headers=headers, verify=False)
        self.last_response_code = response.status_code

        self._logout()
        return response.json()

    def custom_api_call(
            self,
            path: str = None,
            method: str = None,
            headers: dict = None,
            body: dict = None,
            raw: bool = False
    ):
        if path is None:
            return {'error': 'path is required'}
        if method is None:
            return {'error': 'type is required'}
        if headers is None:
            headers = self._login()
        if body is None or method == 'get':
            body = {}

        url = f'https://{self.settings.IP}/{path}'
        try:
            request = requests.Request(method=method, url=url, headers=headers, data=json.dumps(body))
            response = requests.Session().send(request.prepare(), verify=False)
        except Exception as e:
            self._logout()
            return {
                'error': 'invalid request',
                'exception': str(e),
                'recommendation': 'Check the request parameters'
            }

        self.last_action_response_code = response.status_code
        self._logout()

        if raw:
            try:
                dict(response)
                return response
            except Exception as e:
                return {
                    'error': 'invalid response',
                    'exception': str(e),
                    'recommendation': 'Try unsetting the raw flag'
                }

        return response.json()

    def computer_system_reset(self, reset_type: str = None):
        if reset_type is None:
            return {'error': 'reset_type is required'}

        headers = self._login()

        url = f'https://{self.settings.IP}/redfish/v1/Systems/1/Actions/ComputerSystem.Reset'
        body_off = {
            'ResetType': reset_type
        }

        response = requests.post(url, headers=headers, data=json.dumps(body_off), verify=False)
        self.last_response_code = response.status_code

        self._logout()
        return response.json()

    def power_on(self):
        return self.computer_system_reset('On')

    def power_off(self):
        return self.computer_system_reset('ForceOff')

    def restart(self):
        return self.computer_system_reset('ForceRestart')

    def push_power_button(self):
        return self.computer_system_reset('PushPowerButton')


ilo_api = IloApi()
