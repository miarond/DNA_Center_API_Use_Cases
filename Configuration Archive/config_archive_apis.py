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
import csv
import time


def get_csv_device_uuids(csv_file):
    # params csv_file: String containing path to CSV input file
    # return result: List of device UUIDs

    deviceUuids = []

    # Check Dialect of the CSV file
    with open(csv_file, 'r', newline='') as f:
        sample = f.read(64)
        file_dialect = csv.Sniffer().sniff(sample)

    # Open the CSV file contained in the "csv_file" variable
    with open(csv_file, 'r', newline='') as f:
        input_file = csv.reader(f, file_dialect)
        headers = []
        for row in input_file:
            headers = row
            break
        try:
            id_index = headers.index('id')  # Get index number of the "id" header
            logging.debug(f'Column "id" in CSV file found at index: {id_index}')
        except LookupError:
            logging.error(f'No column labeled "id" found in CSV file: {headers}')
            raise Exception(f'No column labeled "id" found in CSV file: {headers}')

        try:
            device_family_index = headers.index('family')  # Check if there is a "family" column and get the index
            logging.debug(f'Column "family" in CSV file found at index: {device_family_index}')
        except LookupError:
            device_family_index = None
            logging.debug('Column "family" not found in CSV file.')

        # Skip to line 2
        next(f)
        for row in input_file:
            # Skip device families "Wireless Sensor", "Unified AP" and "Cisco Interfaces and Modules".
            # Unsupported device families will cause the Configuration Archive API to error out,
            # even if supported devices are included.
            if device_family_index:
                if row[device_family_index].lower() not in ['wireless sensor', 'unified ap', 'cisco interfaces and modules']:
                    deviceUuids.append(row[id_index])  # Append device UUIDs to list
                else:
                    logging.debug(f'Skipping device UUID: {row[id_index]}')
            else:
                deviceUuids.append(row[id_index])  # Append device UUIDs to list
    logging.debug(f'Collected device UUIDs: {deviceUuids}')
    return deviceUuids


def get_hostname(dnac_token, baseUrl, deviceUuid):
    # params dnac_token, baseUrl, deviceUuid: Strings containing API token, base URL and device UUID
    # return hostname: String containing device hostname

    logging.debug(f'Requesting hostname for device UUID: {deviceUuid}')
    query_params = {'id': deviceUuid}
    header = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    url = baseUrl + '/v1/network-device/'
    r = requests.get(url, headers=header, params=query_params, verify=False)
    output = r.json()
    if output['response']:
        for value in output['response']:
            hostname = value['hostname']
            logging.debug(f'Found "{hostname}" for device UUID: {deviceUuid}')
    else:
        logging.debug(f'No device information was returned for device UUID: {deviceUuid}')
        hostname = None
    return hostname


def get_sanitized_config(iterable_list):
    # params iterable_list: Tuple containing API token, baseUrl, device hostname and UUID
    # return r.status_code, hostname, deviceUuid: Returning HTTP status code and device hostname/UUID to keep track of
    # each device that was processed.
    # return result: String, plain text output of device configuration

    logging.info('Requesting sanitized configuration files.')
    logging.debug(f'Received parameters: {iterable_list}')
    dnac_token, baseUrl, hostname, deviceUuid = iterable_list
    header = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    url = baseUrl + '/v1/network-device/' + deviceUuid + '/config'
    r = requests.get(url, headers=header, verify=False)
    output = r.json()
    result = output['response']
    logging.debug(f'Sanitized configuration request status was: {r.status_code}')

    return r.status_code, hostname, deviceUuid, result


def get_config_archive(dnac_token, baseUrl, body_params):
    # params dnac_token, baseUrl: Strings containing API token and base URL
    # params body_params: Dictionary containing "deviceUuids" (as nested list) and "password"
    # return result: Dictionary containing "status_code", "status", "filename", "location", "password"

    logging.info('Requesting configuration archives.')
    logging.debug(f'Received parameters: {body_params}')
    header = {'Content-Type': 'application/json', 'x-auth-token': dnac_token}
    url = baseUrl + '/v1/network-device-archive/cleartext'
    payload = {'password': body_params['password'], 'deviceId': body_params['deviceUuids']}
    logging.debug(f'Generated payload: {payload}')
    logging.debug(f'JSON Dump of payload: {json.dumps(payload)}')
    response = requests.post(url, headers=header, data=json.dumps(payload), verify=False)
    logging.debug(f'Obtained response: {response}')

    output = response.json()
    result = output['response']
    return result, payload['password'], response.status_code


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


def write_config_to_file(hostname, deviceUuid, config):
    # params deviceUuid, hostname, config: Strings containing device UUID, hostname, and configuration in text
    # return result: Dictionary containing the status of the "filename", "location"

    result = {}
    timestamp = time.strftime("%Y-%m-%d_%I-%M-%S%p_%Z", time.localtime())

    # If we received a hostname value, include it in the filename. Otherwise use just device UUID.
    if hostname:
        filename = f'{hostname}_{deviceUuid}_{timestamp}.txt'
    else:
        filename = f'{deviceUuid}_{timestamp}.txt'
    logging.info(f'Attempting to write config for {hostname} to file: {filename}')

    try:
        with open(f'files/{filename}', 'w') as f:
            f.write(config)
        result['status'] = 'Successful'
        result['filename'] = filename
        result['location'] = os.path.abspath(f'files/{filename}')
    except IOError as e:
        result['status'] = f'Failed with error {e}'
        result['filename'] = None
        result['location'] = None
        logging.debug(f'Failed to write config to file, error result: {e}')

    return result


def download_file_by_id(dnac_token, baseUrl, file_url):
    # params dnac_token, baseUrl: Strings containing API token and base URL
    # params file_id: Unique ID of requested file
    # return result: Dictionary containing the status of the file download, file name, and location

    # Remove "/api" from file_url)
    new_file_url = file_url.replace('/api', '', 1)

    logging.info('Attempting to download requested file.')
    logging.debug(f'Attempting download of file at URL: {new_file_url}')
    header = {'Content-Type': 'application/json', 'Accept-Encoding': 'gzip, deflate, br', 'Accept': '*/*',
              'x-auth-token': dnac_token}
    url = baseUrl + new_file_url
    response = requests.get(url, headers=header, verify=False)
    logging.debug(f'Response headers: {response.headers}')

    # Create dictionary for reporting results, including filename and path where it is saved.
    result = {}

    # Check if response was successful (200 OK)
    logging.debug(f'File download response was: {response.status_code}: {response.text}')
    if response.status_code == 200:
        result['status_code'] = response.status_code
        result['status'] = 'The request was successful. The result is contained in the response body.'
        filename = response.headers['fileName']
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
