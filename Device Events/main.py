"""
Copyright (c) 2024 Cisco and/or its affiliates.

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
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import logging
import urllib3
import sys
import os
import argparse
import json
import csv
from datetime import datetime as dt

# Append parent directory to path so we can import from external packages
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import requests
from urllib3.exceptions import InsecureRequestWarning
# From utils directory in repository, import helper functions
from utils import auth, logger, get_config


# Disable certificate warnings
urllib3.disable_warnings(InsecureRequestWarning)

def get_device_uuid(baseUrl, dnac_token, hostname):
    # param baseUrl (str): Base URL for DNAC
    # param dnac_token (str): DNA Center API token
    # param hostname (str): Hostname of device to obtain UUID for.
    # return uuid (str): UUID of device.

    url = f'{baseUrl}/v1/network-device'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_token}
    device_info = requests.get(url, headers=header, params={'hostname': hostname}, verify=False)

    if device_info.status_code == 200:
        uuid = device_info.json()['response'][0]['id']
        logging.debug(f'Device list info obtained: {device_info.json()}')
    else:
        logging.critical(f'Attempt to obtain device UUID resulted in: \n{device_info.status_code}\n{device_info.headers}\n{device_info.text}')
        sys.exit(1)
    return uuid


def get_device_events(baseUrl, dnac_token, uuid, before_ts, after_ts):
    # param baseUrl (str): Base URL for DNAC
    # param dnac_token (str): DNA Center API token
    # param uuid (str): UUID of device.
    # param before_ts, after_ts (str): Epoch timestamps (with millisecond precision).
    # return events (list): JSON formatted list of dicts containing device event data.

    # Construct new base URL - CAUTION: This is an undocumented API and is not supported by Cisco at this time
    url = baseUrl.split('/dna/intent/api')[0] + '/api/assurance/v1/events/deviceEventsView'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_token}
    # Query param 'entityType' is required, but it appears that the value doesn't affect the output.
    params = {
        'entityId': uuid,
        'entityType': 'switch',
        'order': 'desc',
        'startTime': after_ts,
        'endTime': before_ts
    }
    response = requests.get(url, headers=header, params=params, verify=False)
    if response.status_code == 200:
        logging.info(f'Received {response.json()['totalCount']} events')
        logging.debug(f'Obtained device event data: {response.json()}')
    else:
        logging.critical(f'Attempt to obtain device events resulted in: \n{response.status_code}\n{response.headers}\n{response.text}')
        sys.exit(1)
    
    # Convert epoch timestamps to ISO date/time format
    events = response.json()['response']
    for i in events:
        i['timestamp'] = dt.fromtimestamp(i['timestamp'] / 1000).isoformat()
    return events


def save_to_json(hostname, events):
    # param hostname (str): Hostname of device
    # param events (list): JSON formatted list of dicts containing event data
    # return filename (str): Name of file where output was saved

    filename = f'{hostname}_{dt.now().isoformat()}.json'
    with open(filename, 'w') as f:
        f.write(json.dumps(events, indent=4))
    f.close()
    return filename


def save_to_csv(hostname, events):
    # param hostname (str): Hostname of device
    # param events (list): JSON formatted list of dicts containing event data
    # return filename (str): Name of file where output was saved

    filename = f'{hostname}_{dt.now().isoformat()}.csv'
    # Predefine CSV column headers
    field_names = [
        'name',
        'eventName',
        'timestamp',
        'id',
        'severity',
        'mnemonic',
        'facility',
        'switch_number',
        'message_text',
        'additionalinfo',
        'message_type',
        'color_level'
    ]
    with open(filename, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        for i in events:
            # Extract dictionaries from nested "details" list and insert them in parent dictionary
            for item in i['details']:
                # Normalize key names
                i[item['key'].lower().replace(' ', '_')] = item['value']
            # Remove redundant dictionary key
            i.pop('details')
            writer.writerow(i)
    f.close()
    return filename


def main(arguments):
    # Parse CLI arguments, set logging config
    query_params = {}
    logging_level = ''
    logging_file = ''
    for key, value in vars(arguments).items():
        if key == 'logging_level':
            logging_level = value
        elif key == 'logging_file':
            logging_file = value
        else:
            query_params[key] = value

    # Configure Logging
    logger.logger(logging_level, logging_file)
    logging.debug(f'Setting "query_params" to: {query_params}')

    # Convert ISO date/time values to epoch timestamps, millisecond precision
    try:
        before_ts = int((dt.fromisoformat(arguments.before).timestamp()) * 1000)
        logging.debug(f'Converted before date/time to epoch value: {before_ts}')
    except ValueError:
        logging.critical(f'Before date/time value could not be parsed.  Please ensure your date/time value is in a valid ISO 8601 format.')
        sys.exit(1)
    try:
        after_ts = int((dt.fromisoformat(arguments.after).timestamp()) * 1000)
        logging.debug(f'Converted after date/time to epoch value: {after_ts}')
    except ValueError:
        logging.critical(f'After date/time value could not be parsed.  Please ensure your date/time value is in a valid ISO 8601 format.')
        sys.exit(1)

    # Pull in DNAC config details from "config.ini"
    dnac_server, dnac_port, dnac_username, dnac_password = get_config.get_config()

    # Authenticate to DNAC
    logging.info('Authenticating to DNAC.')
    dnac_token = auth.get_dnac_jwt(username=dnac_username, password=dnac_password, server=dnac_server, port=dnac_port)
    logging.debug(f'Setting "dnac_token" to: {dnac_token}')

    baseUrl = f'https://{dnac_server}:{dnac_port}/dna/intent/api'

    # Attempt to obtain device UUID
    device_uuid = get_device_uuid(baseUrl, dnac_token, arguments.device)
    logging.debug(f'Obtained device UUID {device_uuid} from hostname {arguments.device}')

    # Attempt to get device events
    events = get_device_events(baseUrl, dnac_token, device_uuid, before_ts, after_ts)

    # Write events to file
    if arguments.output.lower() == 'json':
        filename = save_to_json(arguments.device, events)
    else:
        filename = save_to_csv(arguments.device, events)
    print(f'Output file saved as {filename}')


if __name__ == '__main__':
    # Parse incoming arguments
    parser = argparse.ArgumentParser(description='This script obtains Assurance event data from Catalyst Center, including Syslog messages collected from devices.')
    log_settings = parser.add_argument_group('Log Settings')
    log_settings.add_argument('-l', '--logging_level', type=str, help='Set logging level. Available levels are: '
                                                                      'CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET',
                                                                      dest='logging_level')
    log_settings.add_argument('-f', '--logging_file', type=str, help='Filename to use for log file.', dest='logging_file')
    parser.add_argument('-d', '--device', type=str, help='Enter device hostname.', required=True)
    parser.add_argument('-b', '--before', required=True, help='Enter a date/time (in ISO 8601 format) for limiting results to messages before that time. (Example: 2023-09-01T10:15:00.000Z)')
    parser.add_argument('-a', '--after', required=True, help='Enter a date/time (in ISO 8601 format) for limiting results to messages after that time. (Example: 2023-09-01T10:15:00.000Z)')
    parser.add_argument('-o', '--output', type=str, help='Select output format. Possible values are: json, csv',
                        dest='output', required=True)
    args = parser.parse_args()
    main(args)