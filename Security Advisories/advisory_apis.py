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
__copyright__ = "Copyright (c) 2022 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import requests
import logging
import json

def get_advisory_summary(dnac_token, baseUrl):
    """
    Retrieve an aggregate summary of current Security Advisories.

    params: dnac_token, baseUrl
    returns: Dictionary of advisory levels and counts
    """
    url = baseUrl + '/v1/security-advisory/advisory/aggregate'
    headers = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    logging.info('Getting Security Advisory Summary.')
    r = requests.get(url, headers=headers, verify=False)
    logging.debug(f'Security Advisory Summary response:\n{r.status_code}\n{r.headers}\n{r.json()}')
    if r.status_code != 200:
        logging.critical(f'Security Advisory Summary API responded with code: {r.status_code}')
        logging.critical(f'Response contents:\n{json.dumps(r.json(), indent=4)}')
        return None
    else:
        return r.json()['response']


def get_advisory_list(dnac_token, baseUrl):
    """
    Retrieve full list of active Security Advisories and their details.

    params: dnac_token, baseUrl
    returns: List of advisories and their details (JSON format)
    """
    url = baseUrl + '/v1/security-advisory/advisory'
    headers = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    logging.info('Getting Security Advisory List.')
    r = requests.get(url, headers=headers, verify=False)
    logging.debug(f'Security Advisory List response:\n{r.status_code}\n{r.headers}\n{r.json()}')
    if r.status_code != 200:
        logging.critical(f'Security Advisory List API responded with code: {r.status_code}')
        logging.critical(f'Response contents:\n{json.dumps(r.json(), indent=4)}')
        return None
    else:
        return r.json()['response']


def get_devices_per_advisory(dnac_token, baseUrl, advisory_id):
    """
    For a given Advisory ID, return the list of affected Device UUIDs.

    params: dnac_token, baseUrl, advisory_id
    returns: List of affected Device UUIDs
    """
    url = baseUrl + '/v1/security-advisory/advisory/' + advisory_id + '/device'
    headers = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    logging.info(f'Getting affected device UUIDs for Security Advisory {advisory_id}.')
    r = requests.get(url, headers=headers, verify=False)
    logging.debug(f'Devices Per Security Advisory response:\n{r.status_code}\n{r.headers}\n{r.json()}')
    if r.status_code != 200:
        logging.critical(f'Devices per Security Advisory API responded with code: {r.status_code}')
        logging.critical(f'Response contents:\n{json.dumps(r.json(), indent=4)}')
        return None
    else:
        return r.json()['response']


def get_device_detials_by_device_id(dnac_token, baseUrl, device_ids):
    """
    For a given list of Device UUIDs, return the device hostnames.

    params: dnac_token, baseUrl, device_ids (String)
    returns: List of device hostnames, management IPs, serial numbers and UUIDs (JSON Format).
    Schema:
    [
        {
            'id': '<device_uuid>',
            'hostname': '<device_hostname>',
            'managementIPAddress': '<mgmt_ip>',
            'serialNumber': '<serial_number>'
        },
    ]
    """
    url = baseUrl + '/v1/network-device'
    headers = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    params = {'id': device_ids}
    logging.debug(f'Getting hostnames for device UUIDs: {device_ids}')
    r = requests.get(url, headers=headers, params=params, verify=False)
    logging.debug(f'Get Device List response:\n{r.status_code}\n{r.headers}\n{r.json()}')
    if r.status_code != 200:
        logging.critical(f'Get Device List API responded with code: {r.status_code}')
        logging.critical(f'Response contents:\n{json.dumps(r.json(), indent=4)}')
        return None
    else:
        result = []
        for item in r.json()['response']:
            device = {} 
            device['id'] = item['id']
            device['hostname'] = item['hostname']
            device['managementIpAddress'] = item['managementIpAddress']
            device['serialNumber'] = item['serialNumber']
            result.append(device)
        return result
