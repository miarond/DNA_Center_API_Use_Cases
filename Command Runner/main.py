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

import cmd_runner_apis
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
from pprint import pprint as pp
from configparser import ConfigParser, Error
from urllib3.exceptions import InsecureRequestWarning

# Disable certificate warnings
urllib3.disable_warnings(InsecureRequestWarning)


def main(arguments):
    # param arguments: Dictionary of logging settings and accepted body parameters for
    # "/dna/intent/api/v1/network-device-poller/cli/read-request" endpoint
    # return result: Dictionary containing status of Command Runner request

    # Create result object for final return. Keys should be "status_code", "status", "filename", "location"
    result = {}

    # Parse arguments, separate out logging and "valid commands" arguments from the rest
    body_params = {}
    logging_level = ''
    logging_file = ''
    valid_commands = False
    for key, value in arguments.items():
        if key == 'logging_level':
            logging_level = value
        elif key == 'logging_file':
            logging_file = value
        elif key == 'valid_commands':
            if value:
                valid_commands = True
        elif key in ['timeout', 'name', 'description'] or value is None:
            body_params[key] = value
        else:
            value_list = str(value).split(',')
            body_params[key] = value_list

    # Configure Logging
    logger.logger(logging_level, logging_file)
    logging.debug(f'Setting "body_params" to: {body_params}')

    # Pull in DNAC config details from "config.ini"
    dnac_server, dnac_port, dnac_username, dnac_password = get_config.get_config()

    # Authenticate to DNAC
    logging.info('Authenticating to DNAC.')
    dnac_token = auth.get_dnac_jwt(username=dnac_username, password=dnac_password, server=dnac_server, port=dnac_port)
    logging.debug(f'Setting "dnac_token" to: {dnac_token}')

    baseUrl = f'https://{dnac_server}:{dnac_port}/dna/intent/api'

    # If "valid_commands" option specified, run "get_accepted_commands" only then exit script
    if valid_commands:
        logging.info('Getting list of accepted command keywords for Command Runner.')
        response = cmd_runner_apis.get_accepted_commands(dnac_token, baseUrl)
        logging.debug(f'Valid commands: {response}')
        logging.debug('Option "valid_commands" passed to script - gracefully exiting.')
        return response
        sys.exit(0)

    # Check if commands and device IDs were specified.
    if body_params['commands'] is None or body_params['deviceUuids'] is None:
        logging.error(f'Error: Commands and Device IDs must be specified: {body_params}')
        raise Exception('You must specific one or more commands and device IDs to run them on.')

    # Make Command Runner request; task will be queued and task ID will be provided
    cmd_runner_result, cmd_runner_status_code = cmd_runner_apis.request_run_command(dnac_token, baseUrl, body_params)

    # Check output of Command Runner results
    if cmd_runner_status_code == 200:
        # Get Task ID from response; we will ignore included URL and simply hard-code it
        cmd_runner_task_id = cmd_runner_result['taskId']
        logging.info(f'Received Task ID: {cmd_runner_task_id}')
    elif cmd_runner_status_code == 201 or cmd_runner_status_code == 202:
        # Unsure what a 201 or 202 result looks like, check if Task ID exists.
        if 'taskId' in cmd_runner_result.keys():
            cmd_runner_task_id = cmd_runner_result['taskId']
            logging.info(f'Received Task ID: {cmd_runner_task_id}')
        else:
            logging.error(f'Command Runner request may not have been successful: {cmd_runner_result}')
            result['status_code'] = cmd_runner_status_code
            result['status'] = cmd_runner_result
            result['filename'] = None
            result['location'] = None
            return result
    else:
        logging.error(f'Command Runner request may not have been successful: {cmd_runner_result}')
        result['status_code'] = cmd_runner_status_code
        result['status'] = cmd_runner_result
        result['filename'] = None
        result['location'] = None
        return result

    # If Command Runner POST successful, get status of task and check if finished
    counter = 1
    while True:
        task_status = cmd_runner_apis.get_task_status(dnac_token, baseUrl, cmd_runner_task_id)
        if task_status['isError']:
            logging.error(f'Command Runner has reported an error: {task_status}')
            result['status_code'] = 500
            result['status'] = task_status
            result['filename'] = None
            result['location'] = None
            break
        elif 'endTime' in task_status.keys():
            file_info = json.loads(task_status['progress'])
            # Initiate file download once File ID becomes available.
            result = cmd_runner_apis.download_file_by_id(dnac_token, baseUrl, file_info['fileId'])
            break
        elif counter <= 4:
            logging.info(f'Currently waiting on Task ID {cmd_runner_task_id} to finish. Attempt #{counter}')
            logging.debug(f'Task is still pending, attempt #{counter}: {task_status}')
            counter += 1
            time.sleep(3)
        else:
            logging.info(f'Task ID {cmd_runner_task_id} has not completed yet. Please check for a problem in DNAC.')
            logging.error(f'Task may be stuck, key "endTime" not found in status output: {task_status}')
            result['status_code'] = 500
            result['status'] = task_status
            result['filename'] = None
            result['location'] = None
            break

    return result


if __name__ == '__main__':
    # Parse incoming arguments
    parser = argparse.ArgumentParser()
    log_settings = parser.add_argument_group('Log Settings')
    log_settings.add_argument('-l', '--logging_level', type=str, help='Set logging level. Available levels are: '
                                    'CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET')
    log_settings.add_argument('-f', '--logging_file', type=str, help='Filename to use for log file.')

    cmd_runner_options = parser.add_argument_group('Command Runner Parameters')
    cmd_runner_options.add_argument('--valid_commands', help='Return a list of valid command keywords'
                                            ' accepted by Command Runner.', action='store_true')
    cmd_runner_options.add_argument('--timeout', type=int, help='Timeout value for commands being run.', default=0)
    cmd_runner_options.add_argument('--name', type=str, help='Name for Command Runner task.')
    cmd_runner_options.add_argument('--description', type=str, help='Description for Command Runner task.')
    cmd_runner_options.add_argument('--commands', type=str, help='Comma separated, double-quoted list of commands to '
                                            'run.')
    cmd_runner_options.add_argument('--deviceUuids', type=str, help='Comma separated double-quoted list of device UUIDs.')

    args = parser.parse_args()
    arg_dict = vars(args)  # Convert "args" Namespace to a Dictionary

    result = main(arg_dict)
    pp(result, indent=4)
