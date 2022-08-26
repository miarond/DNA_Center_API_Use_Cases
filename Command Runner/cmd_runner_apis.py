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
import pathlib
import os
import json


def get_accepted_commands(dnac_token, baseUrl):
    # params dnac_token, baseUrl: Strings used for making API call
    # return result: List of accepted commands from CLI Runner.

    logging.info('Getting list of accepted commands.')
    header = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    url = baseUrl + '/v1/network-device-poller/cli/legit-reads'

    response = requests.get(url, headers=header, verify=False)
    output = response.json()
    result = output['response']
    logging.debug(f'Received list of accepted commands: {result}')
    return result


def request_run_command(dnac_token, baseUrl, payload):
    # params dnac_token, baseUrl: Strings containing API token and API base URL.
    # params payload: Dictionary containing payload with parameters to POST to the
    # "/dna/intent/api/v1/network-device-poller/cli/read-request" endpoint.
    # return result: JSON formatted output

    # Uncomment section below to turn on Requests debugging
    # from http.client import HTTPConnection
    # HTTPConnection.set_debuglevel = 1
    # logging.getLogger().setLevel(logging.DEBUG)
    # requests_log = logging.getLogger("urllib3")
    # requests_log.setLevel(logging.DEBUG)
    # requests_log.propagate = True

    logging.info('Sending Command Runner request.')
    logging.debug(f'Command Runner received payload: {payload}')
    header = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    url = baseUrl + '/v1/network-device-poller/cli/read-request'

    response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    output = response.json()
    result = output['response']
    logging.debug(f'Command Runner response: {response}')
    return result, response.status_code


def get_task_status(dnac_token, baseUrl, task_id):
    # params dnac_token, baseUrl: Strings containing API token and base URL
    # params task_id: UUID of task
    # return result: Dictionary of task details

    logging.info('Checking status of task.')
    logging.debug(f'Task ID: {task_id}')
    header = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    url = baseUrl + '/v1/task/' + task_id
    response = requests.get(url, headers=header, verify=False)
    logging.debug(f'Obtained response: {response.status_code}: {response.text}')

    # Check the status of the task and respond accordingly
    output = response.json()
    result = output['response']
    return result


def download_file_by_id(dnac_token, baseUrl, file_id):
    # params dnac_token, baseUrl: Strings containing API token and base URL
    # params file_id: Unique ID of requested file
    # return result: Dictionary containing the status of the file download, file name, and location

    logging.info('Attempting to download requested file.')
    logging.debug(f'Attempting download of file ID: {file_id}')
    header = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    url = baseUrl + '/v1/file/' + file_id
    response = requests.get(url, headers=header, verify=False)

    # Create dictionary for reporting results, including filename and path where it is saved.
    result = {}

    # Check if response was successful (200 OK)
    logging.debug(f'File download response was: {response.status_code}: {response.text}')
    if response.status_code == 200:
        result['status_code'] = response.status_code
        result['status'] = 'The request was successful. The result is contained in the response body.'
        filename = response.headers['filename'] + '.json'
        pathlib.Path('files/').mkdir(parents=True, exist_ok=True)  # Create a "files/" subdirectory if it doesn't exist

        # Create file and open for writing; stream data in chunks into the file.
        with open(f'files/{filename}', 'wb') as fd:
            for chunk in response.iter_content(chunk_size=512):
                fd.write(chunk)
        result['filename'] = filename
        result['location'] = os.path.abspath(f'files/{filename}')
    else:
        result['status_code'] = response.status_code
        result['status'] = response.text
        result['filename'] = None
        result['location'] = None

    return result

