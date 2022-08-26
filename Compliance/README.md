# DNA Center Compliance APIs

This project code initiates API calls to DNA Center to obtain Compliance Status information for the specified list of devices.  

The project performs the following steps:

1. Start by  the ```main.py``` script. This script accepts arguments for logging level, log file name, and query parameters for the "Get Device List" API endpoint.
   1. For a list of accepted arguments, execute the ```main.py``` script with the ```--help``` argument.
2. Import environment-specific DNA Center information from a ```config.ini``` file, including IP address, TCP port number, username and password.
3. Obtain a JSON Web Token (JWT) for API authentication.
4. Obtain a list of all devices and device info from DNA Center.
5. Parse list and extract ```hostname``` and ```id``` (device Universally Unique Identifier, or "UUID")
6. Utilize multiprocessing capability in Python to make up to 10 parallel API calls to DNA Center to obtain compliance status information for each unique device.
7. Return data as a list of nested dictionaries, containing compliance status information for each device.

This code is broken into single purpose functions which can be imported and reused in other projects however, to run the entire package interactively, execute the ```main.py``` script.