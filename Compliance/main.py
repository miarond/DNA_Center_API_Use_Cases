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

import compliance_apis
import logging
import urllib3
import sys
import os
import argparse

# Append parent directory to path so we can import from external packages
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from utils import auth, logger, get_config
from pprint import pprint as pp
from multiprocessing.pool import ThreadPool
from configparser import ConfigParser, Error
from urllib3.exceptions import InsecureRequestWarning

# Disable certificate warnings
urllib3.disable_warnings(InsecureRequestWarning)


def get_device_uuid(device_info):
    # param device_info: Dictionary of device list output from "/dna/intent/api/v1/network-device" endpoint
    # return device_uuids: List of nested dictionaries containing device hostname and UUID values

    logging.info('Parsing device list from DNAC, extracting hostname and ID.')
    device_uuids = []
    for item in device_info:
        device = {'hostname': item['hostname'], 'id': item['id']}
        device_uuids.append(device)
    logging.debug(f'List of unique devices: {device_uuids}')
    return device_uuids


def compliance_status(dnac_token, baseUrl, device_uuid):
    # param dnac_token: String containing API token for DNAC
    # param baseUrl: String containing the DNAC IP, port, and base URL
    # param device_uuid: List of device UUIDs from "/dna/intent/api/v1/network-device" endpoint
    # return result: List of nested dictionaries containing the compliance status of each device UUID
    # This function uses multiprocessing to run parallel API calls to improve performance
    iterable_list = []
    result = []

    # Create a iteration list of function arguments for thread pool
    for item in device_uuid:
        try:
            hostname = item['hostname']
        except Exception:
            hostname = Null
        id = item['id']
        iterable_list.append((dnac_token, baseUrl, hostname, id))
    with ThreadPool(10) as pool:
        # Call the "get_compliance_details" function with arguments from "iterable_list"
        for output in pool.imap_unordered(compliance_apis.get_compliance_details, iterable_list):
            logging.debug(f'Compliance result: {output}')
            result.append(output)
    return result


def main(arguments):
    # param arguments: Dictionary of logging settings and accepted query params for
    # "/dna/intent/api/v1/network-device" endpoint
    # return compliance_info: List of nested dictionaries containing each device's compliance info

    # Parse arguments
    query_params = {}
    logging_level = ''
    logging_file = ''
    for key, value in arguments.items():
        if key == 'logging_level':
            logging_level = value
        elif key == 'logging_file':
            logging_file = value
        else:
            query_params[key] = value

    # Configure Logging
    logger.logger(logging_level, logging_file)
    logging.debug(f'Setting "query_params" to: {query_params}')

    # Pull in DNAC config details from "config.ini"
    dnac_server, dnac_port, dnac_username, dnac_password = get_config.get_config()

    # Authenticate to DNAC
    logging.info('Authenticating to DNAC.')
    dnac_token = auth.get_dnac_jwt(username=dnac_username, password=dnac_password, server=dnac_server, port=dnac_port)
    logging.debug(f'Setting "dnac_token" to: {dnac_token}')

    baseUrl = f'https://{dnac_server}:{dnac_port}/dna/intent/api'

    # Check for existence of arguments, determine whether list of device UUIDs was provided or must be obtained.
    device_uuid = []
    logging.info('Checking for "Get Device List" query parameters.')
    try:
        if query_params:
            # Get list of device UUIDs from full device list JSON output.
            device_info = compliance_apis.get_device_info(dnac_token, baseUrl, query_params=query_params)
            device_uuid = get_device_uuid(device_info)
            logging.debug(f'Obtained list of device UUIDs: {device_uuid}')
        else:
            # Get list of device UUIDs from full device list JSON output
            device_info = compliance_apis.get_device_info(dnac_token, baseUrl)
            device_uuid = get_device_uuid(device_info)
            logging.debug(f'Obtained list of device UUIDs: {device_uuid}')
    except TypeError:
        # Get list of device UUIDs from full device list JSON output
        logging.warning('Function argument is not of type "dict".')
        device_info = compliance_apis.get_device_info(dnac_token, baseUrl)
        device_uuid = get_device_uuid(device_info)
        logging.debug(f'Obtained list of device UUIDs: {device_uuid}')

    # Initiate parallel processes to obtain compliance status for each device
    logging.info('Getting device compliance status and info.')
    compliance_info = compliance_status(dnac_token, baseUrl, device_uuid)
    logging.debug(f'Obtained list of device compliance info: {compliance_info}')

    return compliance_info


if __name__ == '__main__':
    # Parse incoming arguments
    parser = argparse.ArgumentParser()
    log_settings = parser.add_argument_group('Log Settings')
    log_settings.add_argument('-l', '--logging_level', help='Set logging level. Available levels are: CRITICAL, ERROR,'
                                                      ' WARNING, INFO, DEBUG, NOTSET')
    log_settings.add_argument('-f', '--logging_file', help='Filename to use for log file.')
    query_settings = parser.add_argument_group('Query Parameters')
    query_settings.add_argument('--hostname', help='Hostname query parameter for "/dna/intent/api/v1/network-device"')
    query_settings.add_argument('--managementIpAddress', help='Management IP address query parameter for '
                                                      '"/dna/intent/api/v1/network-device"')
    query_settings.add_argument('--macAddress', help='MAC Address query parameter for "/dna/intent/api/v1/network-device"')
    query_settings.add_argument('--locationName', help='Location name query parameter for "/dna/intent/api/v1/network-device"')
    query_settings.add_argument('--serialNumber', help='Serial Number query parameter for "/dna/intent/api/v1/network-device"')
    query_settings.add_argument('--family', help='Family query parameter for "/dna/intent/api/v1/network-device"')
    query_settings.add_argument('--type', help='Type query parameter for "/dna/intent/api/v1/network-device"')
    query_settings.add_argument('--role', help='Role query parameter for "/dna/intent/api/v1/network-device"')
    query_settings.add_argument('--id', help='Device UUID query parameter for "/dna/intent/api/v1/network-device".'
                                     ' Accepts comma separated list of device UUIDs.')
    args = parser.parse_args()
    arg_dict = vars(args)  # Convert "args" Namespace to a Dictionary

    compliance_info = main(arg_dict)
    pp(compliance_info, indent=4)
