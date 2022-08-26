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


def logger(logging_level, logging_file):
    # param logging_level: Level of logging output
    # Logging levels: 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'
    # param logging_file: Filename for output of log messages - default is not to log to a file

    # Error check content of 'logging_level', set to 'CRITICAL' (50) as default
    if logging_level:
        numeric_log_level = getattr(logging, logging_level.upper())
        if not isinstance(numeric_log_level, int):
            # Quietly fail and set logging level to 'CRITICAL'
            numeric_log_level = 50
    else:
        numeric_log_level = 50

    # Check content of 'logging_file', omit 'filename' argument as default
    if logging_file is None:
        logging.basicConfig(format='%(asctime)s.%(msecs)03d:%(levelname)s:%(message)s',
                            datefmt='%Y-%m-%d  %Z %z: %H:%M:%S', level=numeric_log_level)
    else:
        logging.basicConfig(filename=logging_file, format='%(asctime)s.%(msecs)03d:%(levelname)s:%(message)s',
                        datefmt='%Y-%m-%d  %Z %z: %H:%M:%S', level=numeric_log_level)

    logging.info('Started logging...')
    return
