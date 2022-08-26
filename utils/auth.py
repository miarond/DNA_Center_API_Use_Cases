"""
Copyright (c) 2021 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Aron Donaldson <ardonald@cisco.com>"
__contributors__ = ""
__copyright__ = "Copyright (c) 2021 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import requests
import urllib3
from configparser import ConfigParser
from urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


def get_dnac_jwt(**kwargs):
    username = kwargs.get('username', None)
    password = kwargs.get('password', None)
    server = kwargs.get('server', None)
    port = kwargs.get('port', None)
    dnac_auth = HTTPBasicAuth(username, password)
    url = f'https://{server}:{port}/dna/system/api/v1/auth/token'
    header = {
        'content-type': 'application/json'
    }
    response = requests.post(url, auth=dnac_auth, headers=header, verify=False)
    dnac_jwt_token = response.json()['Token']
    return dnac_jwt_token


if __name__ == '__main__':
    # Parse "config.ini" file to get DNA Center configuration and credentials
    config = ConfigParser()
    config.read('../config.ini')
    server = config['DNAC']['server']
    port = config['DNAC']['port']
    username = config['DNAC']['username']
    password = config['DNAC']['password']

    dnac_token = get_dnac_jwt(username=username, password=password, server=server, port=port)
    print(dnac_token)
