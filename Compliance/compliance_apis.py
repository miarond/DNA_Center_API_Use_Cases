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
import sys
import logging


def get_device_info(dnac_token, baseUrl, **kwargs):
    # param query_params: Dictionary of accepted query params for "/dna/intent/api/v1/network-device" endpoint.
    # param dnac_token: String containing the DNA Center JWT from auth.py
    # param baseUrl: String containing the DNA Center server IP, port and base URL
    # return result: JSON output of API endpoint

    query_params = kwargs.get('query_params', None)
    logging.debug(f'Received the following query parameters: {query_params}')
    try:
        isinstance(query_params, dict)
        isinstance(dnac_token, str)
        isinstance(baseUrl, str)
    except TypeError:
        logging.error('Function argument(s) were not of the correct type.')
        sys.exit(1)

    url = f'{baseUrl}/v1/network-device'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_token}

    if query_params:
        device_info = requests.get(url, headers=header, params=query_params, verify=False)
    else:
        device_info = requests.get(url, headers=header, verify=False)
    result = device_info.json()
    logging.debug(f'Device list info obtained: {result.text}')
    return result['response']


def get_compliance_details(iterable_list):
    # param iterable_list: List containing "dnac_token", "baseUrl", "hostname", "deviceUuid"
    # return result: JSON output of API endpoint

    logging.debug(f'Received iterable list argument: {iterable_list}')
    dnac_token, baseUrl, hostname, deviceUuid = iterable_list
    header = {'content-type': 'application/json', 'x-auth-token': dnac_token}
    url = f'{baseUrl}/v1/compliance/{deviceUuid}/detail?diffList=True'
    r = requests.get(url, headers=header, verify=False)
    output = r.json()
    result = output['response']

    # Insert device hostname into each dictionary because it is not part of compliance output
    for item in result:
        item['hostname'] = hostname
    logging.debug(f'Obtained compliance info: {result}')
    return result


