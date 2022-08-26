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

import config_archive_apis
import logging
import urllib3
import sys
import os
import argparse
import json
import time

# Append parent directory to path so we can import from external packages
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from utils import auth, logger, get_config
from multiprocessing.pool import ThreadPool
from pprint import pprint as pp
from urllib3.exceptions import InsecureRequestWarning

# Disable certificate warnings
urllib3.disable_warnings(InsecureRequestWarning)


def process_sanitized_config(dnac_token, baseUrl, device_list):
    # param dnac_token: String containing API token for DNAC
    # param baseUrl: String containing the DNAC IP, port, and base URL
    # param device_list: List containing nested dictionaries with each device's hostname and UUID
    # return result: List of nested dictionaries containing the status and details of each configuration file
    # This function uses multiprocessing to run parallel API calls to improve performance

    iterable_list = []
    result = []

    # Create a iteration list of function arguments for thread pool
    for item in device_list:
        hostname = item['hostname']
        uuid = item['deviceUuid']
        iterable_list.append((dnac_token, baseUrl, hostname, uuid))
    with ThreadPool(10) as pool:
        # Call the "get_sanitized_config" function with arguments from "iterable_list"
        for status_code, hostname, deviceUuid, output in pool.imap_unordered(config_archive_apis.get_sanitized_config,
                                                                             iterable_list):
            if status_code == 200:
                # If config was retrieved successfully, write output to a file
                file_status = config_archive_apis.write_config_to_file(hostname, deviceUuid, output)
                result.append(file_status)
            else:
                file_status = {'status': f'Configuration request for "{hostname}" (UUID: {deviceUuid}) failed with '
                                         f'status code: {status_code}', 'filename': None, 'location': None}
                result.append(file_status)
    return result


def main(arguments):
    # params arguments: Dictionary containing logging_level, logging_file, deviceUuids, csv_file, password
    # return result: Dictionary of output result, containing status_code, status, filename, location, password

    result = {}

    # Parse arguments, separate out logging and "valid commands" arguments from the rest
    body_params = {}
    logging_level = ''
    logging_file = ''
    full_config = False
    for key, value in arguments.items():
        if key == 'logging_level':
            logging_level = value
        elif key == 'logging_file':
            logging_file = value
        elif key == 'full':
            if value:
                full_config = True
        elif key in ['password', 'csv_file'] or value is None:
            body_params[key] = value
        else:
            value_list = [x.strip() for x in str(value).split(',')]
            body_params[key] = value_list

    # Configure Logging
    logger.logger(logging_level, logging_file)
    logging.debug(f'Setting "body_params" to: {body_params}')

    # Get DNAC environment configuration
    dnac_server, dnac_port, dnac_username, dnac_password = get_config.get_config()
    baseUrl = f'https://{dnac_server}:{dnac_port}/dna/intent/api'

    # Authenticate to DNAC
    logging.info('Authenticating to DNAC.')
    dnac_token = auth.get_dnac_jwt(username=dnac_username, password=dnac_password, server=dnac_server, port=dnac_port)
    logging.debug(f'Setting "dnac_token" to: {dnac_token}')

    # Check if device UUIDs were specified or if a CSV file is being used for input
    if body_params['deviceUuids']:
        logging.debug('List of device UUIDs was specified, moving ahead.')
        pass
    elif body_params['csv_file']:
        # Call CSV function to extract device UUIDs, overwrite "deviceUuids" value in "body_params"
        logging.info('CSV filename was specified, obtaining device UUIDs from CSV file.')
        device_ids = config_archive_apis.get_csv_device_uuids(body_params['csv_file'])
        body_params['deviceUuids'] = device_ids
        logging.debug(f'List of device UUIDs obtained from CSV file: {device_ids}')
    else:
        logging.error(f'Device UUIDs or input CSV file were not found in arguments. Device UUIDs must be provided.')
        raise Exception('Proper inputs were not found.')

    # Check which type of config is requested, then obtain configurations from DNAC
    if full_config:
        archive_result, archive_password, archive_status_code = config_archive_apis.get_config_archive(
            dnac_token, baseUrl, body_params)

        # Check output of Configuration Archive results
        if archive_status_code == 200:
            # Get Task ID from response; we will ignore included URL and simply hard-code it
            archive_task_id = archive_result['taskId']
            logging.info(f'Received Task ID: {archive_task_id}')
        elif archive_status_code == 202:
            # Unsure what a 202 result looks like, check if Task ID exists.
            if 'taskId' in archive_result.keys():
                archive_task_id = archive_result['taskId']
                logging.info(f'Received Task ID: {archive_task_id}')
            else:
                logging.error(f'Configuration Archive request may not have been successful: {archive_result}')
                result['status_code'] = archive_status_code
                result['status'] = archive_result
                result['filename'] = None
                result['location'] = None
                return result
        else:
            logging.error(f'Configuration Archive request may not have been successful: {archive_result}')
            result['status_code'] = archive_status_code
            result['status'] = archive_result
            result['filename'] = None
            result['location'] = None
            return result

        # If Configuration Archive POST successful, get status of task and check if finished
        counter = 1
        while True:
            task_status = config_archive_apis.get_task_status(dnac_token, baseUrl, archive_task_id)
            if task_status['isError']:
                logging.error(f'Configuration Archive has reported an error: {task_status}')
                result['status_code'] = 500
                result['status'] = task_status
                result['filename'] = None
                result['location'] = None
                break
            elif 'endTime' in task_status.keys():
                file_url = task_status['additionalStatusURL']
                # Initiate file download once File ID becomes available.
                result = config_archive_apis.download_file_by_id(dnac_token, baseUrl, file_url)
                result['password'] = archive_password  # Append configured password for archive ZIP file
                break
            elif counter <= 4:
                logging.info(f'Currently waiting on Task ID {archive_task_id} to finish. Attempt #{counter}')
                logging.debug(f'Task is still pending, attempt #{counter}: {task_status}')
                counter += 1
                time.sleep(3)
            else:
                logging.info(f'Task ID {archive_task_id} has not completed yet. Please check for a problem in DNAC.')
                logging.error(f'Task may be stuck, key "endTime" not found in status output: {task_status}')
                result['status_code'] = 500
                result['status'] = task_status
                result['filename'] = None
                result['location'] = None
                break
    else:
        # If sanitized configuration option selected, request that version
        uuid_input = body_params['deviceUuids']
        device_list = []
        logging.info(f'Requesting sanitized configuration files for devices: {uuid_input}')

        # Obtain hostname from DNAC for each device UUID
        for device in uuid_input:
            single_device = {}
            hostname = config_archive_apis.get_hostname(dnac_token, baseUrl, device)
            single_device['hostname'] = hostname
            single_device['deviceUuid'] = device
            device_list.append(single_device)

        # Initiate parallel processes to obtain device configurations
        logging.debug(f'Compiled device list for requesting sanitized configs: {device_list}')
        result = process_sanitized_config(dnac_token, baseUrl, device_list)

    return result


if __name__ == '__main__':
    # Parse incoming arguments
    parser = argparse.ArgumentParser(description='This script requires at a minimum one or more Device UUIDs, or a '
                                                 'CSV file containing those IDs. The script will use the '
                                                 '"Configuration Archive" API endpoint to request encrypted ZIP files '
                                                 'containing those device configurations.')
    log_settings = parser.add_argument_group('Log Settings')
    log_settings.add_argument('-l', '--logging_level', type=str, help='Set logging level. Available levels are: '
                                                                      'CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET')
    log_settings.add_argument('-f', '--logging_file', type=str, help='Filename to use for log file.')

    # Create subparser to request full configuration files encrypted in ZIP files
    subparser = parser.add_subparsers(help='Choose to request full configuration data, including passwords and '
                                           'certificates, or sanitized configuration data.')
    parser_full = subparser.add_parser('full', help='Request full configuration data, returned in encrypted ZIP '
                                                    'format. (Slower method)')
    parser_full.add_argument('--password', type=str, help='Password used for encrypted ZIP file. '
                                                          'Password requirements for API are: '
                                                          'min length = 8, '
                                                          'at least 1 upper and lowercase letter, '
                                                          'at least one digit, '
                                                          'at least one special character. '
                                                          'Default is "Cisco123!"', default='Cisco123!')
    parser_full.add_argument('--deviceUuids', type=str, help='Comma separated double-quoted list of device '
                                                                        'UUIDs.', default=None)
    parser_full.set_defaults(full=True)
    parser_full.add_argument('--csv_file', type=str, help='Filename of a CSV input file, to be used in '
                                                                     'place of the "deviceUuids" argument. CSV file '
                                                                     'MUST have a column titled "id" containing device '
                                                                     'UUIDs.', default=None)

    # Create subparser to request sanitized configuration files in plain text
    parser_sanitized = subparser.add_parser('sanitized', help='Request sanitized configuration data in text format, '
                                                              'without any passwords or certificate information. '
                                                              '(Faster method)')
    parser_sanitized.set_defaults(full=False)
    parser_sanitized.add_argument('--deviceUuids', type=str, help='Comma separated double-quoted list of device '
                                                                        'UUIDs.', default=None)
    parser_sanitized.add_argument('--csv_file', type=str, help='Filename of a CSV input file, to be used in '
                                                                     'place of the "deviceUuids" argument. CSV file '
                                                                     'MUST have a column titled "id" containing device '
                                                                     'UUIDs.', default=None)

    args = parser.parse_args()
    arg_dict = vars(args)  # Convert "args" Namespace to a Dictionary

    result = main(arg_dict)
    pp(result, indent=4)
