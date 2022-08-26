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

import logging
import sys
import os
from configparser import ConfigParser, Error

# Append parent directory to path so we can import from external packages
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


def get_config():
    # Parse "config.ini" file to obtain DNAC appliance details and credentials.
    # return strings: dnac_server, dnac_port, dnac_username, dnac_password.

    # Check for location of "config.ini" file, prompt if it can't be found.
    if os.path.isfile('../config.ini'):
        config_file = '../config.ini'
    elif os.path.isfile('config.ini'):
        config_file = 'config.ini'
    else:
        config_file = input('File "config.ini" was not found. Enter full path to INI file: ')

    logging.info('Parsing "config.ini" file to ingest DNAC details and credentials.')
    config = ConfigParser()
    try:
        config.read(config_file)
        dnac_server = config['DNAC']['server']
        dnac_port = config['DNAC']['port']
        dnac_username = config['DNAC']['username']
        dnac_password = config['DNAC']['password']
        logging.info(f'Setting config option "dnac_server" to {dnac_server}')
        logging.info(f'Setting config option "dnac_port" to {dnac_port}')
    except Error:
        logging.warning('Error occurred while parsing "config.ini" file')  # If parsing fails, prompt for input instead
        import getpass  # Only import "getpass" module if needed
        dnac_server = input('Enter DNA Center appliance IP address: ')
        dnac_port = input('Enter DNA Center TCP port number: ')
        dnac_username = input('Enter DNA Center username: ')
        dnac_password = getpass.getpass(prompt='Enter DNA Center password: ', stream=None)
        logging.info(f'Setting config option "dnac_server" to {dnac_server}')
        logging.info(f'Setting config option "dnac_port" to {dnac_port}')
    return dnac_server, dnac_port, dnac_username, dnac_password


if __name__ == '__main__':
    get_config()
