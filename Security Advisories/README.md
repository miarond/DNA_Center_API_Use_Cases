# Security Advisories Script

This Python script will query the DNA Center "Security Advisory" APIs to obtain data on the currently active
Security Advisories logged by the system.  Based on your CLI argument options, you can obtain a Summary Report
which returns only the counts of Advisories in each severity category, or you can obtain a Full List Report 
which returns all the details about each Advisory, with the addition of affected device information being
added to the JSON data for each Advisory.

You can choose between three file output formats: JSON, CSV, or Excel  Each file will be saved in the 
current working directory with an appropriate name that includes the current date/time stamp.

For information on the available command line options, run the following command (or similar):

```
python3 main.py --help
```

### Additional Required Packages

This use case requires that additional Python Packages be downloaded and installed from the Python Package
Index (https://pypi.org).  To use this script you must install the additional packages listed in the 
`requirements.txt` file by using the following command (or similar): 

```
pip install -r requirements.txt
```