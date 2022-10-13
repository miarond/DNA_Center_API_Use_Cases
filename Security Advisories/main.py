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

import advisory_apis
import logging
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import sys
import os
import argparse
import json
import time

# External package from PyPi
from pandas import read_json

# Append parent directory to path so we can import from top-level packages
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

# Import top-level common modules from this project
from utils import auth, logger, get_config

# Disable certificate warnings
urllib3.disable_warnings(InsecureRequestWarning)

# Get current date/time in proper format
timestamp = time.strftime("%Y-%m-%d_%I-%M-%S%p_%Z", time.localtime())

def get_affected_devices(dnac_token, baseUrl, adv_list):
    """
    Function that calls the "advisory_apis.get_devices_per_advisory" function and obtains the devices 
    affected by each Security Advisory. It then calls the "advisory_apis.get_device_details_by_device_id"
    function to obtain the hostname, management IP and serial number of each device.

    params: dnac_token, baseUrl, adv_list (JSON response from Get Advisories List API)
    returns: adv_list (Modified JSON to add affected device details)
    """
    for advisory in adv_list:
        affected_devices = advisory_apis.get_devices_per_advisory(dnac_token, baseUrl, advisory['advisoryId'])
        if affected_devices == None:
            raise ValueError('"advisory_apis.get_devices_per_advisory" API returned a value of None.')
        dev_string = ''
        for item in affected_devices:
            # Create comma-separated list of device UUIDs for next API call
            dev_string += f'{item},'
        # Trim off trailing comma
        dev_string = dev_string[:-1]
        # Add device details to new "affectedDevices" key in JSON payload
        advisory['affectedDevices'] = advisory_apis.get_device_detials_by_device_id(dnac_token, baseUrl, dev_string)
    return adv_list


def main(args):
    """
    A script that queries the Security Advisory APIs for information about active Security Advisories.
    If a full list is requested, the script will identify all affected devices per Security Advisory,
    and obtain details about the device.

    The script can output the resulting information in JSON, CSV or Excel formats.

    params: args (argparse Namespace)
    """
    if args.logging_level:
        if args.logging_file:
            logger.logger(args.logging_level, args.logging_file)
        else:
            logger.logger(args.logging_level, None)

    # Get DNAC environment configuration
    dnac_server, dnac_port, dnac_username, dnac_password = get_config.get_config()
    baseUrl = f'https://{dnac_server}:{dnac_port}/dna/intent/api'

    # Authenticate to DNAC
    logging.info('Authenticating to DNAC.')
    dnac_token = auth.get_dnac_jwt(username=dnac_username, password=dnac_password, server=dnac_server, port=dnac_port)
    logging.debug(f'Setting "dnac_token" to: {dnac_token}')

    # Get Security Advisories
    filename = f'advisory_{args.report.lower()}_{timestamp}'
    if args.report.lower() == 'full':
        adv_list = advisory_apis.get_advisory_list(dnac_token, baseUrl)
        result = get_affected_devices(dnac_token, baseUrl, adv_list)
        if result == None:
            raise ValueError('"advisory_apis.get_advisory_list" API returned a value of None.')
    else:
        result = advisory_apis.get_advisory_summary(dnac_token, baseUrl)
        if result == None:
            raise ValueError('"advisory_apis.get_advisory_summary" API returned a value of None.')
        
    # Format the output
    if args.output.lower() == 'json':
        with open(f'{filename}.json', 'w') as f:
            f.write(json.dumps(result, indent=4))
            f.close()
        logging.info(f'Output saved to "{filename}.json".')
    elif args.output.lower() == 'csv':
        data = read_json(json.dumps(result))  # Here is where Pandas package is used
        data.to_csv(f'{filename}.csv', index=False)
        logging.info(f'Output saved to "{filename}.csv".')
    else:
        data = read_json(json.dumps(result)) # Here is where Pandas package is used
        data.to_excel(f'{filename}.xlsx', index=False) 
        logging.info(f'Output saved to "{filename}.xlsx".')


if __name__ == '__main__':
    # Parse incoming arguments
    parser = argparse.ArgumentParser(description='This script queries the Security Advisory APIs '
                                                'for information about current vulnerabilities and '
                                                'any affected devices.')
    parser.add_argument('-r', '--report', help='Choose the level of report you want.  Options are "full" or "summary".',
                        required=True)
    log_settings = parser.add_argument_group('Log Settings')
    log_settings.add_argument('-l', '--logging_level', type=str, help='Set logging level. Available levels are: '
                                                                      'CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET',
                                                                      dest='logging_level')
    log_settings.add_argument('-f', '--logging_file', type=str, help='Filename to use for log file.', dest='logging_file')
    parser.add_argument('-o', '--output', type=str, help='Select output format. Possible values are: json, csv, excel',
                        dest='output', required=True)
    args = parser.parse_args()
    main(args)
