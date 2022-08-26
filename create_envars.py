"""
Copyright (c) {{current_year}} Cisco and/or its affiliates.

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
__copyright__ = "Copyright (c) {{current_year}} Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# This script is used to ingest credentials and environment variables from a "config.ini" file, then use those values
# to set local Environmental Variables within the context of the Python Virtual Environment.  These variables are only
# stored in memory for the current Python process; when script completes the variables will be erased.  A logging
# process is also configured to generate a local log file and record output.

from configparser import ConfigParser
import os
import sys
import logging
import argparse
import pprint  # Not needed if output is not being printed to the console.

# Set up argparser to accept logging arguments
parser = argparse.ArgumentParser(description='Configure log filename and logging level.')
parser.add_argument('-l', '--level', type=str, default='INFO', dest='level', help='Sets the logging level. Options are:'
                    ' CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET.')
parser.add_argument('-f', '--filename', type=str, default='dnac_api.log', dest='filename', help='Sets the filename '
                    'used for the log file.')
args = parser.parse_args()


def logger(args):
    log_options = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
    file_name = args.filename
    level = args.level.upper()
    logging.basicConfig(filename=file_name, format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S %Z %z', level=logging.INFO)
    logging.info(__name__ + 'started log file.')
    if level in log_options:
        if level == 'CRITICAL':
            logging.basicConfig(level=logging.CRITICAL)
        if level == 'ERROR':
            logging.basicConfig(level=logging.ERROR)
        if level == 'WARNING':
            logging.basicConfig(level=logging.WARNING)
        if level == 'INFO':
            logging.basicConfig(level=logging.INFO)
        if level == 'DEBUG':
            logging.basicConfig(level=logging.DEBUG)
        if level == 'NOTSET':
            logging.basicConfig(level=logging.NOTSET)


def import_config():
    result = {}
    # Import connection details and credentials from 'config.ini' file, add them as key:value pairs to result
    # dictionary.
    config = ConfigParser()
    try:
        config.read('config.ini')
        result['DNAC_INTENT_BASEURL'] = config['DNAC']['intentBaseUrl']
        result['DNAC_USERNAME'] = config['DNAC']['username']
        result['DNAC_PASSWORD'] = config['DNAC']['password']
        result['DNAC_SERVER'] = config['DNAC']['server']
        result['DNAC_PORT'] = config['DNAC']['port']
    except:
        logging.error('An error occurred while reading the "config.ini" file.')
        sys.exit(1)
    return result


def set_envars(config):
    result = {}
    for k, v in config.items():
        # Check if variable exists, log a warning message. Finally, write new value to the variable.
        try:
            value = os.environ[k]
            logging.warning(f'Environmental variable "{k}" already exists with value "{value}". This will '
                            'be overwritten!')
        except KeyError:
            continue
        finally:
            # Set new environment variable value and log it. USE CAUTION HERE - PASSWORDS WILL BE LOGGED.
            os.environ[k] = v
            logging.info(f'Environmental variable {k} has been set to {v}.')
            result[k] = os.environ[k]
    return result


def main():
    # Pass command line arguments to the logger function.
    logger(args)
    result = import_config()
    result = set_envars(result)
    return result


if __name__ == '__main__':
    result = main()
    # Following lines can be commented out - only needed for validation that the script works.
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(result)
