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
import logging


def get_device_by_id(dnac_token, baseUrl, deviceUuid):
    # params dnac_token, baseUrl, deviceUuid: Strings containing API token, base URL, and the device UUID
    # return result: Dictionary containing all device data for specified UUID

    logging.info(f'Getting device information for device UUID: {deviceUuid}')
    header = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    url = baseUrl + '/v1/network-device/' + deviceUuid
    response = requests.get(url, headers=header, verify=False)
    logging.debug(f'Received response: {response.status_code}: {response.text}')

    output = response.json()
    result = output['response']
    return result


def get_device_chassis_detail(dnac_token, baseUrl, deviceUuid):
    # params dnac_token, baseUrl, deviceUuid: Strings containing API token, base URL, and the device UUID
    # return result: Dictionary containing all device chassis info for specified UUID

    logging.info(f'Getting device chassis information for device UUID: {deviceUuid}')
    header = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    url = baseUrl + '/v1/network-device/' + deviceUuid + '/chassis'
    response = requests.get(url, headers=header, verify=False)
    logging.debug(f'Received response: {response.status_code}: {response.text}')

    output = response.json()
    result = output['response']
    return result


def get_device_by_other(dnac_token, baseUrl, query_params):
    # param query_params: Dictionary containing subset of accepted query params for
    # "/dna/intent/api/v1/network-device" endpoint. Multiple values are accepted in List format
    # param dnac_token: String containing the DNA Center JWT from auth.py
    # param baseUrl: String containing the DNA Center server IP, port and base URL
    # return result: Dictionary containing device details

    # For the purposes of this function, we will only accept these parameters: hostname, managementIpAddress,
    # macAddress, serialNumber, id (device UUID)
    params = {}
    logging.debug(f'Received query parameters: {query_params}')

    for key, value in query_params.items():
        if key in ['hostname', 'managementIpAddress', 'macAddress', 'serialNumber', 'id']:
            if key:  # If key has a value other than "None", add that value to params dict.
                params[key] = value
            else:
                params[key] = None
    logging.debug(f'Generated the following parameters: {params}')

    url = baseUrl + '/v1/network-device'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_token}

    if params:
        device_info = requests.get(url, headers=header, params=query_params, verify=False)
    else:
        # If no parameters are specified, get details of all devices. This could be process intensive - may want to
        # throw an error instead, for large deployments.
        device_info = requests.get(url, headers=header, verify=False)
    result = device_info.json()
    logging.debug(f'Device list info obtained: {result}')
    return result['response']


def get_interface_info_by_device(dnac_token, baseUrl, deviceUuid):
    # params dnac_token, baseUrl, deviceUuid: Strings containing API token, base URL, and the device UUID
    # return result: JSON containing dictionaries of all device interface info for specified UUID

    logging.info(f'Getting device interface information for device UUID: {deviceUuid}')
    header = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    url = baseUrl + '/v1/interface/network-device/' + deviceUuid
    response = requests.get(url, headers=header, verify=False)
    logging.debug(f'Received response: {response.status_code}: {response.text}')

    output = response.json()
    result = output['response']
    return result
