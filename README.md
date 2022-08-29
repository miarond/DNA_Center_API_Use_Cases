[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/miarond/DNA_Center_API_Use_Cases)

# DNA Center API Use Cases

## Purpose:

This collection of scripts is intended to document and demonstrate interacting with the Cisco DNA Center API and perform various example operations.

## Getting Started:

### Cloning Repository

Start by cloning this repository to your local machine with the command: ```git clone <repository_url>.git```  In the root directory is a ```config.ini.template``` file where DNA 
Center appliance details can be stored.  Rename this file to ```config.ini``` and add your specific DNA Center environment details to the file.

### Creating Python Virtual Environment

In your command line application, change directory to the cloned repository folder and run the command ```python -m venv .``` (ensure you are executing this command using the Python 3 interpreter - on a Mac computer, you will need to install Python 3 and run it with the command ```python3```)

Next you will need to "activate" this virtual environment.  Do this by running the command (in Mac and Linux environments) ```source venv/bin/activate``` In Windows environments, run the ```activate.ps1``` PowerShell script instead.  When finished you can deactivate the virtual environment by simply running the command ```deactivate```

Finally, install the required external Python packages by running the command ```pip install -r requirements.txt```

### Create Config.ini File

Copy the ```config.ini.template``` and rename it to ```config.ini```.  Edit the file and replace the "server", "port", "username" and "password" variables with your environment's relevant information.  

### Optional Examples
The ```create_envars.py``` example file uses ConfigParser to ingest configuration details from ```config.ini``` (remove the ```.template``` extension when using the file) and creates local Environmental Variables within Python to store those details.  These variables are stored in memory and are removed once the script completes and the Python process terminates.  This is an alternative secure option of storing credentials for a script.

## License:

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).
