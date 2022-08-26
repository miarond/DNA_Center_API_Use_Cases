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

import csv
import json
import argparse


def main(args):
    # params args: Dictionary of parsed command line arguments
    # return Null

    input_file = open(args['input_file'])
    device_list = json.load(input_file)
    headings = []

    # Iterate through first dictionary item and append keys to "headings" list.
    for i in device_list:
        for key in i.keys():
            headings.append(key)
        break

    # Create a CSV file using "output_file" filename and open it for writing
    with open(args['output_file'], 'w', encoding='UTF8', newline='') as f:
        # Generate a list of column headers from dictionary keys in the input file

        # Write column headers to the file
        writer = csv.DictWriter(f, fieldnames=headings)
        writer.writeheader()

        # Iterate through each dictionary contained in "device_list" and write values into each row.
        for i in device_list:
            writer.writerow(i)

    return


if __name__ == '__main__':
    # Parse incoming arguments
    parser = argparse.ArgumentParser(description='This simple script is used to ingest a JSON formatted text file, '
                                    'containing a device list from DNA Center, and parse the contents into a CSV '
                                    'formatted output file. The input file is created from the output of the '
                                    '"response" key of the DNA Center "Get Device List 1" API endpoint '
                                    '(/dna/intent/api/v1/network-device).')
    parser.add_argument('--input_file', type=str, help='JSON formatted text file containing output from the "response" '
                        'key of the "/dna/intent/api/v1/network-device" API endpoint.')
    parser.add_argument('--output_file', type=str, help='Filename to use for CSV file that is created. Defaults to '
                        '"devices.csv".', default='devices.csv')

    args = parser.parse_args()
    arg_dict = vars(args)  # Convert "args" Namespace to a Dictionary

    main(arg_dict)
