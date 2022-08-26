# DNA Configuration Archive APIs

This project code is used to request device configuration archive downloads for the specified list of devices managed by DNA Center.  The Configuration Archive API will accept a list of Device UUIDs and a password for encrypting the ZIP archive which will contain the requested device configurations.

This project performs the following steps:

1. Execute process using the ```main.py``` script. This script accepts arguments for ```--logging_level```, ```--logging_file```, and positional arguments for ```full``` or ```sanitized``` versions of device configurations.  You must specify one of these options followed by parameters for the Configuration Archive API.  The argument ```--password``` is required for a full encrypted archive request. Either the ```--deviceUuids``` or ```--csv_file``` arguments must be specified to determine which device configurations are being requested. 
   1. The argument ```--csv_file``` accepts the path and filename to any CSV file that contains at *least* a column labeled ```id```, which contains Device UUIDs. The script will parse through the file and obtain the Device UUID list. (Note: The CSV script will check for a ```family``` column and automatically bypass any devices of type: Wireless Sensor, Unified AP, or Cisco Interfaces and Modules.)
   2. For a list of accepted arguments, execute the ```main.py``` script with the ```--help``` argument.
   3. Any device that does not have a configuration file (i.e. Wireless Sensors, Unified APs or Cisco Modules and Interfaces) but is passed to the Configuration Archive API will cause the operation to fail completely. The API does not gracefully handle unsupported devices.
2. Import environment-specific DNA Center information from a ```config.ini``` file, including IP address, TCP port number, username and password.
3. Obtain a JSON Web Token (JWT) for API authentication.
4. Depending on which positional argument is given (```full``` or ```sanitized```), one of the following actions will be taken:
   1. ```full```:
      1. Subsequent arguments provided to ```main.py``` will be processed and sent to the Configuration Archive API which will generate an asynchronous **Task ID** on DNA Center that is returned to the script.
      2. The script will check the status of the **Task ID** on DNA Center.  If the Task completes successfully, DNA Center will return a **File ID** to the script.
      3. The script will use the **File ID** to request a download of the file.  The file is an encrypted, password-protected ZIP archive which is saved in the ```files/``` sub-directory.  A status report is returned to the script containing the status, filename, location and archive password.
   2. ```sanitized```:
      1. Subsequent arguments provided to ```main.py``` will be processed and sent to the Get Device Config By ID API, which will request the stored plain-text configuration for each device from DNA Center.  This configuration data will omit any passwords and certificate information.
      2. Configuration will be returned in plain-text and will be written to text files, which will be saved under the ```files/``` sub-directory.  Each file will be named with the format ```<hostname>_<deviceUUID>_<date/time-stamp>.txt```.

This code is broken into single purpose functions which can be imported and reused in other projects however, to run the entire package interactively, execute the ```main.py``` script.