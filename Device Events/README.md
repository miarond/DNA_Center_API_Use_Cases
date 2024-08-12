# Get Device Events from Catalyst Center

This Python script will query Catalyst Center for device Assurance events occurring between within the given date/time window, then save those events to a local file.

:warning: **This script makes use of Catalyst Center's Assurance API interface which is undocumented and not fully supported by Cisco TAC or the product Business Unit.**  Functionality and stability of this API interface is not guaranteed - please use this solution at your own risk.

  > *Note: Support for querying Assurance events has been added to the API for Catalyst Center v2.3.7, with the following endpoints: [Get details of a single assurance event](https://developer.cisco.com/docs/dna-center/2-3-7/get-details-of-a-single-assurance-event/), [Query assurance events](https://developer.cisco.com/docs/dna-center/2-3-7/query-assurance-events/), [Query assurance events with filters](https://developer.cisco.com/docs/dna-center/2-3-7/query-assurance-events-with-filters/).  The API endpoint used in this script is not one of these supported interfaces and remains undocumented, though it has been tested successfully in v2.3.5.5.*

You can choose between two file output formats: JSON or CSV.  Each file will be saved in the 
current working directory with an appropriate name that includes the device hostname and current date/time stamp.

The command line options for this script are:

```
  -d DEVICE, --device DEVICE
                        Enter device hostname.
  -b BEFORE, --before BEFORE
                        Enter a date/time (in ISO 8601 format) for limiting results to messages before that time. (Example: 2023-09-01T10:15:00.000Z)
  -a AFTER, --after AFTER
                        Enter a date/time (in ISO 8601 format) for limiting results to messages after that time. (Example: 2023-09-01T10:15:00.000Z)
  -o OUTPUT, --output OUTPUT
                        Select output format. Possible values are: json, csv

Log Settings:
  -l LOGGING_LEVEL, --logging_level LOGGING_LEVEL
                        Set logging level. Available levels are: CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
  -f LOGGING_FILE, --logging_file LOGGING_FILE
                        Filename to use for log file.
```

For information on the available command line options, run the following command (or similar):

```
python3 main.py --help
```

### Notes on API

The API endpoint used in this script is undocumented and as such, information about the capacity and maximum returned values is not available.  However, in testing the following behaviors have been observed:

- The following query parameters appear to be required:
    - `entityId`: The device UUID.
    - `entityType`: The type of device (router, switch, etc). The value in this parameter does not appear to be used, though; specifying `switch` while giving the UUID of a router still returns the correct records.
    - `startTime`: Earliest record to return, using Unix epoch timestamps with millisecond precision
    - `endTime`: Latest record to return, using Unix epoch timestamps with millisecond precision
- Dates older than 180 days from the current date are not allowed
- The `totalCount` key indicating the number of returned records does not appear to accurately represent the number of events returned.  The maximum number returned in this field is `10000`, even when fewer events are actually included.  

    ```
    {
        "version": "1.0",
        "response": [...],
        "totalCount": 10000
    }
    ```
    - In testing, using the `offset` and `limit` query parameters, a maximum limit of `5131` was observed, though this may not be the actual maximum accepted value for this parameter.
