# Automating the Onboarding Process for DNA Center

DNA Center has a robust set of built-in capabilities to provide Zero-Touch, Plug and Play functionality for newly discovered network devices.  However, there are still some manual hands-on steps required to move a device from Unclaimed to Provisioned within the DNA Center GUI.  In this project we will be utilizing the DNA Center Intent APIs for Device Onboarding to fully automate those manual workflow steps.

  > *NOTE: This guide is based on the API and GUI for DNA Center software version 2.2.2.x.*

## Table of Contents

#### Procedure

  1. [Authenticate to DNA Center](#authenticate-to-dna-center)
  2. [List the Unclaimed Devices](#list-the-unclaimed-devices)
  3. [Obtain the Desired Site ID](#obtain-the-desired-site-id)
  4. [Obtain Configuration Template Details](#obtain-configuration-template-details)
  5. [Obtain Software Image UUID](#obtain-software-image-uuid)
  6. [Claim the Device to a Site](#claim-the-device-to-a-site)
  7. [Reset a Failed Device](#reset-a-failed-device)
  8. [Check Device History and Status](#check-device-history-and-status)

#### API Endpoints
  1. [Authenticating to DNA Center](#authenticating-to-dna-center)
  2. [Get PnP Device List](#get-pnp-device-list)
  3. [Get Site Topology](#get-site-topology)
  4. [Get Site](#get-site)
  5. [Get Available Templates](#get-available-templates)
  6. [Get Template Details](#get-template-details)
  7. [Get Software Image Details](#get-software-image-details)
  8. [Claim a Device to a Site](#claim-a-device-to-a-site)
  9. [Reset Device](#reset-device)
  10. [Get Device History](#get-device-history)
  11. [Get Device by ID](#get-device-by-id)

#### References
  - [References](#references-1)

#### Contributors
  - [Contributors](#contributors-1)

---

## Procedure

### Authenticate to DNA Center

DNA Center utilzies an ephemeral token system for authenticating API calls, and that token is obtained via the [Authenticating to DNA Center](#authenticating-to-dna-center) API endpoint.

  1. Using the **`POST`** method, make a call to the API endpoint with the following headers:
      
      a. NOTE: The Authorization header uses HTTP Basic authentication.  See the API endpoint section for details. 

  ```json
  {
      "Content-Type": "application/json",
      "Authorization": "Basic abcdABCD12345678"
  }
  ```
  2. The Response will be in JSON format and will include the key `Token`.  Save the value of the `Token` key in a variable for use with future API calls.  The lifetime of the token should be 60 minutes.
  3. In subsequent API calls, add the header key `x-auth-token` and pass the token as the value for that key.

[Return to ToC](#table-of-contents)

---

### List the Unclaimed Devices

During the Discovery process, DNA Center will identify new network devices and add them to the "Plug and Play" **Unclaimed** list, under the *Menu --> Provision --> Network Devices --> Plug and Play* menu.  As devices are added to this list they are assigned a unique ID, which you will need in order to claim the device via the API. (Note: This is NOT the device UUID; that value is not created and assigned until a device is "claimed".)

  1. Using the [Get PnP Device List](#get-pnp-device-list) API endpoint, make the API call with a Query Parameter of `state=Unclaimed`.
  2. Parse through the JSON response to identify the desired device - normally you will be using device Serial Number, which will look like this snippet:

  ```json
  [
      {
        "deviceInfo": {
            "serialNumber": "ABCD1234"
        },
        "id": "618c05b76433b0730232b3de"
      }
  ]
  ```
  
  3. Store the value of the `id` key shown above.  This is the unique identifier that will be used to target this device in the "Claim a Device to a Site" API later on.

[Return to ToC](#table-of-contents)

---

### Obtain the Desired Site ID

The end result of this prodecure will be to claim an "Unclaimed" device, push a Day 0 onboarding configuration template to it, and finally assign it to a site.  Each object tracked by DNA Center is assigned a UUID value which is often used by the DNA Center APIs to idenify the object you're interacting with.  You will need to obtain the Site UUID for each site that you want to assign a new device to.

If you do not know the exact hierarchy name of the desired site (ex: "Global/Minneapolis, MN/HQ/Floor 4"), then you will most likely need to use the [Get Site Topology](#get-site-topology) API to list all of the sites in your DNA Center.  If you *do* know the exact hierarchy name of the site, you can use the [Get Site](#get-site) API with a query parameter similar to: `name=Global/Minneapolis, MN/HQ/Floor 4`.

  1. Using the [Get Site Topology](#get-site-topology) API, get the complete list of available sites.
  2. Parse through the JSON response to identify the desired site, then store the value of the `id` field for later use.  The output will look similar to this snippet:

  ```json
    {
        "response": {
            "sites": [
                {
                "id": "ec9519f5-db86-4454-9883-a0a4b45b572d",
                "name": "Floor 4",
                "parentId": "412e89eb-cc29-4dc2-982f-d9f21442c060",
                "latitude": "",
                "longitude": "",
                "locationType": "floor",
                "locationAddress": "7900 International Drive, Bloomington, Minnesota 55425, United States",
                "locationCountry": "",
                "displayName": "14561549",
                "groupNameHierarchy": "Global/Minneapolis, MN/HQ/Floor 4"
                }
            ]
        },
        "version": "1.0"
    }
  ```

[Return to ToC](#table-of-contents)

---

### Obtain Configuration Template Details

When claiming a device to a site in DNA Center, a Day 0 configuration template must be applied to the device.  There are initial steps for creating and assigning this template which, for the purposes of this document, are assumed to have been completed:

  - Create a Network Hierarchy
  - Create a Network Profile
  - Create a Day 0 template (with or without variables)
  - Save and commit the template
  - Assign the template to one or more Network Profiles

Configuration templates can be hard-coded configuration, or they can include variables which can be assigned values at the time of deployment.  When deploying a template to a device, you must have the following information:

  - Template UUID
  - Template variable names
  - Template variable types (i.e. string, integer, etc)

  1. Use the [Get Available Templates](#get-available-templates) API endpoint to identify the correct Day 0 template, then store its `templateId` UUID for later use.  The results can be filtered with the use Query Parameters - the most useful will likely be `projectNames=<array_of_project_name(s)>`.  The JSON response will look similar to this snippet:

  ```json
    [
        {
            "name": "labday0",
            "projectName": "Onboarding Configuration",
            "projectId": "71715223-035b-40d3-85db-be39a332400b",
            "templateId": "57b73266-131e-427d-8edd-7262812aefca",
            "versionsInfo": [
                **** TRUNCATED ****
            ]
        }
    ]
  ```

  2. Use the [Get Template Details](#get-template-details) API endpoint to obtain detailed information about the template, including all of the variables and their data types (i.e. string, integer, etc).  These variables will be listed in the `templateParams` key of the JSON response data, and will be stored in an "array" data type.
    
      a. In the `templateParams` array, you will need to collect and store the `parameterName` and `dataType` values.  These will identify the name of the template variable and its data type.  Here is an example snippet:

      ```json
        "templateParams": [
            {
                "parameterName": "VLAN_ID",
                "dataType": "INTEGER",
                "defaultValue": null,
                "description": null,
                "required": true,
                "notParam": false,
                "paramArray": false,
                "displayName": "Voice VLAN ID",
                "instructionText": null,
                "group": null,
                "order": 2,
                "customOrder": 2,
                "selection": {
                    "selectionType": null,
                    "selectionValues": {},
                    "defaultSelectedValues": [],
                    "id": "a6af7349-0e9f-43fb-9500-728fd61a65ca"
                },
                "range": [],
                "key": null,
                "provider": null,
                "binding": "",
                "id": "244b2a1b-3643-456c-ab2b-159ce2dc5be5"
            }
      ```

[Return to ToC](#table-of-contents)

---

### Obtain Software Image UUID

When claiming a device to a site, you will be required to provide the UUID of the desired software image you want to apply to the device.  This is normally the "Golden Image" you have selected in the DNA Center Image Repository.

  1. Using the [Get Software Image Details](#get-software-image-details) API, optionally with Query Parameters of `isTaggedGolden=true` and `family=<device_family>` to filter results, obtain the resulting software image details.
  2. Parse through the JSON response to obtain the value of the `imageUuid` key for your desired software image.  Here is a snippet of the API output:

  ```json
    {
        "response": [
            {
                "imageUuid": "ce3149e4-3ddb-4a98-8734-eed4959ec3de",
                "name": "cat9k_iosxe.16.12.01.SPA.bin",
                "family": "CAT9K",
                "version": "16.12.1.0.544",
                "displayVersion": "16.12.1",
                "md5Checksum": "58755699355bb269be61e334ae436685",
                "shaCheckSum": "9486e30459410640fb652d18eb1bd5e82cd35da9ab772d1a00d9fc6bc751aea3de8069084341af029555b7ae0818656630ec84eebc8bde0a1ae02d89a671b740",
                "createdTime": "2019-11-13 15:42:23.0",
                "imageType": "SYSTEM_SW",
                "fileSize": "810207530 bytes",
                "imageName": "cat9k_iosxe.16.12.01.SPA.bin",
                "applicationType": "",
                "feature": "",
                "fileServiceId": "d7708de9-e5b5-4158-96cc-4c859b6b569e",
                "isTaggedGolden": true,
            **** TRUNCATED ****
            }
        ],
        "version": "1.0"
    }
  ```

[Return to ToC](#table-of-contents)

---

### Claim the Device to a Site

After collecting all of the information specified in the steps above (unclaimed device ID, site UUID, template UUID, template variables, and software image UUID), you can move on to the final step of claiming the device and assigning it to a site.

  1. Using the [Claim a Device to a Site](#claim-a-device-to-a-site) API and the **`POST`** method, send a JSON payload in the body of the HTTP message that follows this format:

  ```json
    {
        "deviceId": "<device_id>",
        "siteId": "<site_uuid>",
        "type": "Default",
        "imageInfo": {
            "imageId": "<image_uuid>",
            "skip": false
        },
        "configInfo": {
            "configId": "<day0_template_uuid>",
            "configParameters": [
                {
                    "key": "<variable_1_name>",
                    "value": "<variable_1_value>"
                },
                {
                    "key": "<variable_2_name>",
                    "value": 100 <variable_2_value_integer_example>
                },
                {
                    "key": "<variable_3_name>",
                    "value": "<variable_3_value>"
                }
            ]
        }
    }
  ```

  > a. The API documentation for the "Claim a Device to a Site" on the https://developer.cisco.com website is incomplete and does not mention the `imageInfo` or `configInfo` sections of the payload.  This is a known issue and has been reported to DevNet however, at the time this document was written it has not yet been fixed.

  > b. The `skip` key under the `imageInfo` dictionary is a Boolean data type.  We have not fully tested this option but setting it to "true" may bypass a code upgrade on the target device, if it is not currently running the specified software image.

  2. The following are examples of the JSON response data:

      a. Successfully claimed a device:

        ```json
        {
            "response": "Device Claimed",
            "version": "1.0"
        }
        ```

      b. Failed to claim a device:

      ```json
        {
            "response": {
                "errorCode":"NCOB01276",
                "message":"NCOB01276: Invalid request for claiming device(s). Refer to details for more information",
                "detail":"[{\"message\":\"A device cannot be claimed in error state, it must be Reset.\",\"deviceId\":\"62194d82c754c051c271a638\"}]",
                "href":"/onboarding/pnp-device/site-claim"
            },
            "version":"1.0"
        }
      ```
  
  3. The onboarding process can take several minutes to complete so periodic monitoring of the status will be helpful.  Also, if a device claim API call fails, the device will be put in an error state and will need to be reset.  Both of those operations will be explained in the following two sections.

[Return to ToC](#table-of-contents)

---

### Reset a Failed Device

If a device claim operation fails for some reason, the device will be moved to the "Error" tab on the **Plug and Play** page and will be kept in that status until it is reset.  This can be done via the GUI or an API call:

  1. Using the [Reset Device](#reset-device) API and the **`POST`** method, send the following payload containing just the `deviceId` value for the failed device:

        ```json
        {
            "deviceResetList": [
                {
                    "configList": [
                        {
                            "configId": null,
                            "configParameters": [
                                {
                                    "key": null,
                                    "value": null
                                }
                            ]
                        }
                    ],
                    "deviceId": "<device_id>",
                    "licenseLevel": null,
                    "licenseType": null,
                    "topOfStackSerialNumber": null
                }
            ],
            "projectId": null,
            "workflowId": null
        }
        ```
  
  2. The following are examples of the JSON response data:

      a. Successful device reset:
      
      ```json
        {
            "message":"Device(s) Reset",
            "statusCode":200
        }
      ```

      b. Failed device reset:

      ```json
        {
            "response": {
                "errorCode": "NCOB01278",
                "message": "NCOB01278: Invalid request for resetting device(s). Refer to details for more information",
                "detail": "[{\"message\":\"This device has completed provisioning. This device may be deleted. No other actions are applicable.\",\"deviceId\":\"62194d82c754c051c271a638\"},{\"message\":\"This device has completed provisioning. This device may be deleted. No other actions are applicable.\",\"deviceId\":\"62194d82c754c051c271a638\"}]",
                "href": "/onboarding/pnp-device/reset"
            },
            "version": "1.0"
        }
      ```

  3. A device reset will take several minutes to complete so periodic monitoring of the status will be helpful.  This will be covered in the following section.

[Return to ToC](#table-of-contents)

---

### Check Device History and Status

Information on the history of actions performed on a managed device can be obtained from the [Get Device History](#get-device-history) API:

  1. Obtain the Serial Number of the device and provide that as the Query Parameter `serialNumber=<device_sn>`. You can also specify sort fields and sort order with the optional `sort` and `sortOrder` Query Parameters.
  2. The JSON reponse from this API endpoint is very large and contains the historical log of all Plug and Play actions executed for this device.  By default the results are sorted in "descending" order by the value of the `timestamp` key - this value is represented in **[Epoch time format](https://en.wikipedia.org/wiki/Unix_time)** with millisecond precision.

Information on the current status of the device can be obtained from the [Get Device by ID](#get-device-by-id) API endpoint.  This API returns data about the entire device, including its onboarding state.

  1. Obtain the Plug and Play device ID (can be found in the output of the [Get PnP Device List](#get-pnp-device-list) API) for the network device and provide that as a **URL Parameter** in the API URL:
    
      ```
      https://<dnac_ip/hostname>:<port>/dna/intent/api/v1/onboarding/pnp-device/{id}
      ```

  2. Parse the JSON response data and check the value of the `onbState` key.  Here is an example snippet of the output:

      ```json
        {
            "version": 2,
            "deviceInfo": {
                "serialNumber": "FJC2330E0NJ",
                "name": "FJC2330E0NJ",
                "agentType": "IOS",
                "pid": "C9300-24UX",
                "lastSyncTime": 0,
                "addedOn": 1645825410332,
                "lastUpdateOn": 1646153239165,
                "firstContact": 1645825410330,
                "lastContact": 1646153239163,
                "lastContactDuration": 5043,
                "provisionedOn": 1646153233729,
                "state": "Provisioned",
                "onbState": "Provisioned",
                "cmState": "Authenticated",
                "imageFile": "flash:packages.conf",
                "imageVersion": "17.3.4",
                "mode": "INSTALL",
            **** TRUNCATED ****
            }
        }
      ```

      a. The output contains additional helpful information about the workflow, valid actions that can be taken, etc.  It is a good idea to inspect the output of this API during the onboarding process, to look for additional details.

[Return to ToC](#table-of-contents)

---
---

## API Endpoints

### Authenticating to DNA Center

**Method:**

<pre><code><b>POST</b></code></pre>

**API URL:**
```
https://<dnac_ip/hostname>:<port>/api/system/v1/auth/token
```
  > [API Docs](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-2-2-2-api-api-authentication-authentication-api)

**Headers:**
```json
{
    "Content-Type": "application/json",
    "Authorization": "Basic abcdABCD12345678"
}
```
> **Note:** Authorization uses HTTP Basic Auth method. The Authorization string is the word "Basic" followed by a space, then the Base64 encoded string of the values `username:password`. Note that `username` and `password` are separated by a (`:`) colon.

**Response:**
```json
{
    "Token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1YzZjZDNjOTg0NzZmOTAwOTAzMjEwMjAiLCJhdXRoU291cmNlIjoiaW50ZXJuYWwiLCJ0ZW5hbnROYW1lIjoiVE5UMCIsInJvbGVzIjpbIjVjNmNkMzhmZDM4ODFhMTRmZTJhNTdiZSJdLCJ0ZW5hbnRJZCI6IjVjNmNkM2M3ODQ3NmY5MDA5MDMyMTAxZiIsImV4cCI6MTY0NTAyODYwNiwiaWF0IjoxNjQ1MDI1MDA2LCJqdGkiOiI0M2FhM2M4My1lZjcxLTRmZTQtYjY5Zi0zYmRhMmU3NDA5NDkiLCJ1c2VybmFtZSI6ImFkbWluIn0.kPNq4fddrBbpTtg8JiEkRZofWEKwqfVvAqNCJOFxjmJ-vpIcGxFhqO1ZSh4EgzQg8-Q6uOW3E4DjiDkGia0fzydEEIiY4tRVKjp-YlYQVNaJ7z_Ax3rzj-i0EIz6jBCUvoqxkQbQNoji9-byrrZ7VxhaZ8k5ci2qiFDegBO1K8pMyRVCiMmpYtKOJ_6VpvfrN9pIWekj6ecSExqmetXoMUGmmVGxf8vdjlbhVCMCvWggGJu0DZxND90eETsEwkHAFFfnZlWx2hDbAzxjVgfG68ZZIL0CIQIWEQvGwHY-8_hnpXuNRCM19JfgknvoVD7dwN8Pw_zhHOVJpT6FrB73yg"
}
```

**Usage:**

Once obtained, store the string value for the key `Token` in a variable, and in future API calls specify the string in the header key `x-auth-token`.  For example:

```json
{
    "Content-Type": "application/json",
    "x-auth-token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1YzZjZDNjOTg0NzZmOTAwOTAzMjEwMjAiLCJhdXRoU291cmNlIjoiaW50ZXJuYWwiLCJ0ZW5hbnROYW1lIjoiVE5UMCIsInJvbGVzIjpbIjVjNmNkMzhmZDM4ODFhMTRmZTJhNTdiZSJdLCJ0ZW5hbnRJZCI6IjVjNmNkM2M3ODQ3NmY5MDA5MDMyMTAxZiIsImV4cCI6MTY0NTAyODYwNiwiaWF0IjoxNjQ1MDI1MDA2LCJqdGkiOiI0M2FhM2M4My1lZjcxLTRmZTQtYjY5Zi0zYmRhMmU3NDA5NDkiLCJ1c2VybmFtZSI6ImFkbWluIn0.kPNq4fddrBbpTtg8JiEkRZofWEKwqfVvAqNCJOFxjmJ-vpIcGxFhqO1ZSh4EgzQg8-Q6uOW3E4DjiDkGia0fzydEEIiY4tRVKjp-YlYQVNaJ7z_Ax3rzj-i0EIz6jBCUvoqxkQbQNoji9-byrrZ7VxhaZ8k5ci2qiFDegBO1K8pMyRVCiMmpYtKOJ_6VpvfrN9pIWekj6ecSExqmetXoMUGmmVGxf8vdjlbhVCMCvWggGJu0DZxND90eETsEwkHAFFfnZlWx2hDbAzxjVgfG68ZZIL0CIQIWEQvGwHY-8_hnpXuNRCM19JfgknvoVD7dwN8Pw_zhHOVJpT6FrB73yg"
}
```

[Return to ToC](#table-of-contents)

---

### Get PnP Device List

**Method**
<pre><code><b>GET</b></code></pre>

**API URL:**
```
https://<dnac_ip/hostname>:<port>/dna/intent/api/v1/onboarding/pnp-device
```
  > [API Docs](https://developer.cisco.com/docs/dna-center/#!get-pnp-device-list)

**Headers:**
```json
{
    "Content-Type": "application/json",
    "x-auth-token": <dnac_auth_token>
}
```

**Query Parameters:**
```
state=Unclaimed
```
>**Note:** There are many query parameters for this API endpoint. To filter the returned data to include *only* devices in an "Unclaimed" state, we will specify this single query parameter.  Query parameters are appended to the end of an API URL in the format: 
  
  `?parameter1=value1&parameter2=value2`

**Response:**
```json
[
    {
        "version": 2,
        "deviceInfo": {
            "serialNumber": "97ZD4PGRLUS",
            "name": "97ZD4PGRLUS",
            "deviceType": "Catalyst WLC",
            "agentType": "IOS",
            "pid": "C9800-CL-K9",
            "lastSyncTime": 0,
            "addedOn": 1636566455293,
            "lastUpdateOn": 1645025155065,
            "firstContact": 1636566455291,
            "lastContact": 1645025155065,
            "lastContactDuration": 4,
            "provisionedOn": 0,
            "state": "Unclaimed",
            "onbState": "Initialized",
            "cmState": "Secured Connection",
            "imageFile": "bootflash:packages.conf",
            "imageVersion": "17.5.1",
            "mode": "INSTALL",
            "httpHeaders": [
                {
                    "key": "clientAddress",
                    "value": "172.16.202.146"
                }
            ],
********** OUTPUT TRUNCATED ***********
        },
        "workflowParameters": {},
        "dayNCmdQueue": [],
        "runSummaryList": [],
        "id": "618c05b76433b0730232b3de"
    }
]
```

[Return to ToC](#table-of-contents)

---

### Get Site Topology

**Method**
<pre><code><b>GET</b></code></pre>

**API URL:**
```
https://<dnac_ip/hostname>:<port>/dna/intent/api/v1/topology/site-topology
```
  > [API Docs](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-2-2-2-api-api-topology-get-site-topology)

**Headers:**
```json 
{
    "Content-Type": "application/json",
    "x-auth-token": <dnac_auth_token>
}
```

**Response:**

```json
{
    "response": {
        "sites": [
            {
                "id": "ec9519f5-db86-4454-9883-a0a4b45b572d",
                "name": "Floor 4",
                "parentId": "412e89eb-cc29-4dc2-982f-d9f21442c060",
                "latitude": "",
                "longitude": "",
                "locationType": "floor",
                "locationAddress": "7900 International Drive, Bloomington, Minnesota 55425, United States",
                "locationCountry": "",
                "displayName": "14561549",
                "groupNameHierarchy": "Global/Minneapolis, MN/HQ/Floor 4"
            },
********** OUTPUT TRUNCATED ***********
        ]
    },
    "version": "1.0"
}
```

[Return to ToC](#table-of-contents)

---

### Get Site

**Method**
<pre><code><b>GET</b></code></pre>

**API URL:**
```
https://<dnac_ip/hostname>:<port>/dna/intent/api/v1/site
```
  > [API Docs](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-2-2-2-api-api-sites-get-site)

**Headers:**
```json
{
    "Content-Type": "application/json",
    "x-auth-token": <dnac_auth_token>
}
```

**Query Parameters:**

> *Query parameters are optional*
```
name=<siteNameHierarchy> (ex: global/groupName)
siteId=<sideId>
type=<siteType> (ex: area, building, floor)
offset=<offset/starting row> (default is 1)
limit=<number> (number of sites to be retrieved, default is 500)
```

**Response:**

```json
{
    "response": {
        "parentId": "412e89eb-cc29-4dc2-982f-d9f21442c060",
        "additionalInfo": [
            {
                "nameSpace": "Location",
                "attributes": {
                    "address": "7900 International Drive, Bloomington, Minnesota 55425, United States",
                    "addressInheritedFrom": "412e89eb-cc29-4dc2-982f-d9f21442c060",
                    "type": "floor"
                }
            },
            {
                "nameSpace": "mapsSummary",
                "attributes": {
                    "rfModel": "46046",
                    "floorIndex": "4"
                }
            },
            {
                "nameSpace": "mapGeometry",
                "attributes": {
                    "offsetX": "0.0",
                    "offsetY": "0.0",
                    "length": "100.0",
                    "width": "100.0",
                    "height": "10.0"
                }
            }
        ],
        "name": "Floor 4",
        "instanceTenantId": "5c6cd3c78476f9009032101f",
        "id": "ec9519f5-db86-4454-9883-a0a4b45b572d",
        "siteHierarchy": "22b1bd92-07c2-4294-b2e5-017ecfa32126/63c50285-521f-4e1a-bdcc-0a37577d16d4/412e89eb-cc29-4dc2-982f-d9f21442c060/ec9519f5-db86-4454-9883-a0a4b45b572d",
        "siteNameHierarchy": "Global/Minneapolis, MN/HQ/Floor 4"
    }
}
```

[Return to ToC](#table-of-contents)

---

### Get Available Templates

**Method**
<pre><code><b>GET</b></code></pre>

**API URL:**
```
https://<dnac_ip/hostname>:<port>/dna/intent/api/v1/template-programmer/template
```
  > [API Docs](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-2-2-2-api-api-configuration-templates-gets-the-templates-available)

**Headers:**
```json
{
    "Content-Type": "application/json",
    "x-auth-token": <dnac_auth_token>
}
```

**Query Parameters:**

> *Query parameters are optional, used for filtering the results returned.*
```
projectId=<project_UUID>
softwareType=<software_type>
softwareVersion=<software_version>
productFamily=<product_family> (Filter by device family.)
productSeries=<product_series> (Filter based on device series.)
productType=<product_type> (Filter based on device type.)
filterConflictingTemplates=<true/false> (Boolean value)
tags=[<tag>, <tag>] (Array of template tag values)
projectNames=[<name>, <name>] (Array of project names)
unCommitted=<true/false> (Boolean value, filter on committed vs uncommitted templates)
sortOrder=<asc/des> (Sort results in Ascending or Descending order)
```

**Response:**

```json
[
    {
        "name": "ardonald_Day0_Template",
        "projectName": "Onboarding Configuration",
        "projectId": "71715223-035b-40d3-85db-be39a332400b",
        "templateId": "3c39900d-a5b1-4c36-b7d2-c721c06770e7",
        "versionsInfo": [
            {
                "id": "60e7e3f8-dd91-40ed-bdeb-26cc0c23e888",
                "description": "Base configuration template for onboarding",
                "author": "admin",
                "version": "2",
                "versionComment": "added support for 9500",
                "versionTime": 1637014839724
            },
            {
                "id": "667ea90c-788b-466d-99c7-56f966f99e87",
                "description": "Base configuration template for onboarding",
                "author": "admin",
                "version": "1",
                "versionComment": "First commit",
                "versionTime": 1634746929241
            }
        ],
        "composite": false,
        "tags": [],
        "softwareType": "IOS-XE",
        "deviceTypes": [
            {
                "productFamily": "Switches and Hubs",
                "productSeries": "Cisco Catalyst 9500 Series Switches"
            },
            {
                "productFamily": "Switches and Hubs",
                "productSeries": "Cisco Catalyst 9300 Series Switches"
            },
            {
                "productFamily": "Switches and Hubs",
                "productSeries": "Cisco Catalyst 9200 Series Switches"
            }
        ]
    }
]
```

[Return to ToC](#table-of-contents)

---

### Get Template Details

**Method**
<pre><code><b>GET</b></code></pre>

**API URL:**
```
https://<dnac_ip/hostname>:<port>/dna/intent/api/v1/template-programmer/template/{templateId}
```
  > [API Docs](https://developer.cisco.com/docs/dna-center/#!get-template-details)

**Headers:**
```json
{
    "Content-Type": "application/json",
    "x-auth-token": <dnac_auth_token>
}
```

**URL Parameters:**

> *URL parameters are embedded within the API URL and are required.*
```
templateId=<template_UUID>
```

**Query Parameters:**

> *Query parameters are optional.*
```
latestVersion=<true/false> (Boolean, return only the latest committed version of the template.)
```

**Response:**

```json
{
    "name": "ardonald_Day0_Template",
    "description": "Base configuration template for onboarding",
    "author": "admin",
    "deviceTypes": [
        {
            "productFamily": "Switches and Hubs",
            "productSeries": "Cisco Catalyst 9500 Series Switches"
        },
        {
            "productFamily": "Switches and Hubs",
            "productSeries": "Cisco Catalyst 9300 Series Switches"
        },
        {
            "productFamily": "Switches and Hubs",
            "productSeries": "Cisco Catalyst 9200 Series Switches"
        }
    ],
    "softwareType": "IOS-XE",
    "softwareVariant": "XE",
    "templateContent": "(Configuration template contents, use '\n' for line breaks)",
********** OUTPUT TRUNCATED ***********
    "rollbackTemplateContent": "",
    "templateParams": [
        {
            "parameterName": "hostname",
            "dataType": "STRING",
            "defaultValue": null,
            "description": null,
            "required": true,
            "notParam": false,
            "paramArray": false,
            "displayName": null,
            "instructionText": null,
            "group": null,
            "order": 1,
            "customOrder": 0,
            "selection": {
                "selectionType": null,
                "selectionValues": {},
                "defaultSelectedValues": [],
                "id": "fcae3464-26f5-4451-a22d-cebe85b65f83"
            },
            "range": [],
            "key": null,
            "provider": null,
            "binding": "",
            "id": "3b207aec-f908-4e9b-b351-cfea560419f8"
        },
        {
            "parameterName": "vlan_id",
            "dataType": "INTEGER",
            "defaultValue": null,
            "description": null,
            "required": true,
            "notParam": false,
            "paramArray": false,
            "displayName": null,
            "instructionText": null,
            "group": null,
            "order": 2,
            "customOrder": 0,
            "selection": {
                "selectionType": null,
                "selectionValues": {},
                "defaultSelectedValues": [],
                "id": "dc25494b-c9a4-41f6-b472-5b16ea4bce93"
            },
            "range": [],
            "key": null,
            "provider": null,
            "binding": "",
            "id": "4faf732c-a325-4ad8-ba91-cf62506763b8"
        },
        {
            "parameterName": "vlan_name",
            "dataType": "STRING",
            "defaultValue": null,
            "description": null,
            "required": true,
            "notParam": false,
            "paramArray": false,
            "displayName": null,
            "instructionText": null,
            "group": null,
            "order": 3,
            "customOrder": 0,
            "selection": null,
            "range": [],
            "key": null,
            "provider": null,
            "binding": "",
            "id": "a53049cd-889d-465d-b33e-d1ec081a3432"
        }
    ],
    "rollbackTemplateParams": [],
    "composite": false,
    "containingTemplates": [],
    "language": "JINJA",
    "id": "60e7e3f8-dd91-40ed-bdeb-26cc0c23e888",
    "version": "2",
    "customParamsOrder": false,
    "createTime": 1634746915378,
    "lastUpdateTime": 1637014825843,
    "latestVersionTime": 1637014839724,
    "projectName": "Onboarding Configuration",
    "projectId": "71715223-035b-40d3-85db-be39a332400b",
    "parentTemplateId": "3c39900d-a5b1-4c36-b7d2-c721c06770e7",
    "validationErrors": {
        "templateErrors": [],
        "rollbackTemplateErrors": [],
        "templateId": "60e7e3f8-dd91-40ed-bdeb-26cc0c23e888",
        "templateVersion": null
    },
    "projectAssociated": true,
    "documentDatabase": false
}
```

[Return to ToC](#table-of-contents)

---

### Get Software Image Details

**Method**
<pre><code><b>GET</b></code></pre>

**API URL:**
```
https://<dnac_ip/hostname>:<port>/dna/intent/api/v1/image/importation
```
  > [API Docs](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-2-2-2-api-api-software-image-management-swim-get-software-image-details)

**Headers:**
```json
{
    "Content-Type": "application/json",
    "x-auth-token": <dnac_auth_token>
}
```

**Query Parameters:**

> *This API endpoint has many query parameters for filtering results; below are the most useful.*
```
family=<device_type_family> (ex: "CAT9K")
imageName=<software_image_filename> (ex: "cat9k_iosxe.16.12.01.SPA.bin")
version=<software_image_version_number> (ex: "16.12.1.0.544")
isTaggedGolden=true/false (Boolean, is image tagged as a Golden image?)
```

**Response Body:**

```json
{
    "response": [
        {
            "imageUuid": "ce3149e4-3ddb-4a98-8734-eed4959ec3de",
            "name": "cat9k_iosxe.16.12.01.SPA.bin",
            "family": "CAT9K",
            "version": "16.12.1.0.544",
            "displayVersion": "16.12.1",
            "md5Checksum": "58755699355bb269be61e334ae436685",
            "shaCheckSum": "9486e30459410640fb652d18eb1bd5e82cd35da9ab772d1a00d9fc6bc751aea3de8069084341af029555b7ae0818656630ec84eebc8bde0a1ae02d89a671b740",
            "createdTime": "2019-11-13 15:42:23.0",
            "imageType": "SYSTEM_SW",
            "fileSize": "810207530 bytes",
            "imageName": "cat9k_iosxe.16.12.01.SPA.bin",
            "applicationType": "",
            "feature": "",
            "fileServiceId": "d7708de9-e5b5-4158-96cc-4c859b6b569e",
            "isTaggedGolden": true,
********** OUTPUT TRUNCATED ***********
                    "sites": [],
                    "show": false,
                    "userDefined": false
                }
            ],
            "importSourceType": "FILESYSTEM",
            "ccoreverseSync": true
        }
    ],
    "version": "1.0"
}
```

[Return to ToC](#table-of-contents)

---

### Claim a Device to a Site

**Method**
<pre><code><b>POST</b></code></pre>

**API URL:**
```
https://<dnac_ip/hostname>:<port>/dna/intent/api/v1/onboarding/pnp-device/site-claim
```
  > [API Docs](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-2-2-2-api-api-device-onboarding-pnp-claim-a-device-to-a-site)

**Headers:**
```json
{
    "Content-Type": "application/json",
    "x-auth-token": <dnac_auth_token>
}
```

**Request Body:**

The following values are required and may be obtained from API calls listed above:
  - **Device ID**
    - The unique identifier for a discovered device in the Plug and Play list.
    - Obtained from the [Get PnP Device List](#get-pnp-device-list) API
        > *NOTE: This is NOT the device's UUID. That unique identifier is not created or assigned until the device has been completely onboarded to DNA Center.*
  - **Site UUID**
    - A DNA Center site's unique identifier.
    - Obtained from the [Get Site Topology](#get-site-topology) or [Get Site](#get-site) API endpoints. If you do not know the exact site name hierarchy (ex: "Global/Minneapolis, MN/HQ/Floor 4"), you will want to use the "Get Site Topology" API for a list of all sites.
  - **Sofware Image UUID**
    - Unique identifier of the software image file in SWIM that should be applied to this device during onboarding.
    - Obtained from the [Get Software Image Details](#get-software-image-details) API endpoint. It may be necessary to apply several query parameter filters to the API call in order to narrow search results.
  - **Configuration Template UUID**
    - Unique identifier for the Day 0 onboarding template you want to apply to the device.
    - Obtained from the [Get Available Templates](#get-available-templates) API endpoint.
  - **Template Configuration Parameters**
    - All variables from the Day 0 onboarding template which need to be defined during deployment.
    - Obtained from the [Get Template Details](#get-template-details) API endpoint, once you have obtained the template UUID.
      > *NOTE: Config parameters are listed as an array of dictionaries where the key `key` is equal to the variable name, and the key `value` is equal to that variable's value.*

*Default method*
```json
{
    "deviceId": <pnp_device_id>,
    "siteId": <site_uuid>,
    "type": "Default",
    "imageInfo": {
        "imageId": <software_image_uuid>,
        "skip": false
    },
    "configInfo": {
            "configId": <day0_onboarding_template_uuid>,
            "configParameters":[
                {
                "key":"template_variable_name",
                "value": "template_variable_value"
                },
                {
                "key":"template_variable_name",
                "value": "template_variable_value"
                }
            ]
    }
}
```

*Stack Switch method*
```json
{
    "deviceId": <pnp_device_id>,
    "siteId": <site_uuid>,
    "type": "StackSwitch",
    "topOfStackSerialNumber": <device_sn>,
    "imageInfo": {
        "imageId": <software_image_uuid>,
        "skip": false
    },
    "configInfo": {
            "configId": <day0_onboarding_template_uuid>,
            "configParameters":[
                {
                "key":"template_variable_name",
                "value": "template_variable_value"
                },
                {
                "key":"template_variable_name",
                "value": "template_variable_value"
                }
            ]
    }
}
```

*Example payload:*
```json
{
    "deviceId": "62194d82c754c051c271a638",
    "siteId": "ec9519f5-db86-4454-9883-a0a4b45b572d",
    "type": "Default",
    "imageInfo": {
        "imageId": "42038603-17b0-44de-98b5-6ee54e3c20bc",
        "skip": false
    },
    "configInfo": {
        "configId": "60e7e3f8-dd91-40ed-bdeb-26cc0c23e888",
        "configParameters": [
            {
                "key": "hostname",
                "value": "EdgeSW2"
            },
            {
                "key": "vlan_id",
                "value": 1
            },
            {
                "key": "vlan_name",
                "value": "Management_VLAN"
            }
        ]
    }
}
```

**Response Body:**

*Successful claim request:*

```json
{
    "response": "Device Claimed",
    "version": "1.0"
}
```

*Failed claim request:*

```json
{
    "response": {
        "errorCode":"NCOB01276",
        "message":"NCOB01276: Invalid request for claiming device(s). Refer to details for more information",
        "detail":"[{\"message\":\"A device cannot be claimed in error state, it must be Reset.\",\"deviceId\":\"62194d82c754c051c271a638\"}]",
        "href":"/onboarding/pnp-device/site-claim"
    },
    "version":"1.0"
}
```
> ***Note:*** *If an error was encountered, status code will be 404 and "response" key will contain additional details.*

[Return to ToC](#table-of-contents)

---

### Reset Device

*Recovers a device from a workflow execution error state. This performs a factory reset on the device.*

**Method**
<pre><code><b>POST</b></code></pre>

**API URL:**
```
https://<dnac_ip/hostname>:<port>/dna/intent/api/v1/onboarding/pnp-device/reset
```
  > [API Docs](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-2-2-2-api-api-device-onboarding-pnp-reset-device)

**Headers:**
```json
{
    "Content-Type": "application/json",
    "x-auth-token": <dnac_auth_token>
}
```

**Request Body:**

  > *NOTE: The body payload can contain several values, as documented in the API Docs however, it is sufficient to send a single parameter of the `deviceId` to this API endpoint (as demonstrated below).*

```json
{
    "deviceResetList": [
        {
            "configList": [
                {
                    "configId": null,
                    "configParameters": [
                        {
                            "key": null,
                            "value": null
                        }
                    ]
                }
            ],
            "deviceId": "62194d82c754c051c271a638",
            "licenseLevel": null,
            "licenseType": null,
            "topOfStackSerialNumber": null
        }
    ],
    "projectId": null,
    "workflowId": null
}
```

**Response:**

*Successful reset request:*

```json
{
    "message": "Device(s) Reset",
    "statusCode": 200
}
```

*Failed reset request:*

```json
{
    "response": {
        "errorCode": "NCOB01278",
        "message": "NCOB01278: Invalid request for resetting device(s). Refer to details for more information",
        "detail": "[{\"message\":\"This device has completed provisioning. This device may be deleted. No other actions are applicable.\",\"deviceId\":\"62194d82c754c051c271a638\"},{\"message\":\"This device has completed provisioning. This device may be deleted. No other actions are applicable.\",\"deviceId\":\"62194d82c754c051c271a638\"}]",
        "href": "/onboarding/pnp-device/reset"
    },
    "version": "1.0"
}
```

[Return to ToC](#table-of-contents)

---

### Get Device History

*Obtain the onboarding history of a device.*

**Method**
<pre><code><b>GET</b></code></pre>

**API URL:**
```
https://<dnac_ip/hostname>:<port>/dna/intent/api/v1/onboarding/pnp-device/history
```
  > [API Docs](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-2-2-2-api-api-device-onboarding-pnp-get-device-history)

**Headers:**
```json
{
    "Content-Type": "application/json",
    "x-auth-token": <dnac_auth_token>
}
```

**Query Parameters:**

```
serialNumber=<device_serial_number>
sort=<comma_separated_list> (Comma separated list of fields to sort on.)
sortOrder=asc/des
```

**Response:**

```json
{
    "response": [
        {
            "timestamp": 1646085694355,
            "details": "NCOB04014: Failed to apply configuration on the device. Invalid input in the configuration applied. ",
            "historyTaskInfo": {
                "name": "Site Config Task",
                "type": "SiteConfig",
                "timeTaken": 0,
                "workItemList": [
                    {
********** OUTPUT TRUNCATED ***********
                    }
                ],
                "addnDetails": [
                    {
                        "key": "Day 0 Config Generation Time Taken",
                        "value": "0.09 seconds"
                    },
                    {
                        "key": "Site Name",
                        "value": "Global/Minneapolis, MN/HQ/Floor 4"
                    },
                    {
                        "key": "Template Name",
                        "value": "ardonald_Day0_Template"
                    }
                ]
            },
            "commandResponse": {
                "ConfigUpgradeResponse": {
                    "cmdId": "0062c941-f823-4f0f-bbf8-a4181b4e0a0d",
                    "serialNumber": "FJC2330E0NJ",
                    "authStatus": "AUTHENTICATED",
                    "cmdOutput": "" 
********** OUTPUT TRUNCATED ***********
                    "errorSeverity": "ERROR",
                    "errorMessage": "Invalid input detected",
                    "errorCode": "PnP Service Error 1413",
                    "platformId": "C9300-24UX",
                    "encoding": "HTML_ESCAPED",
                    "status": false,
                    "timestamp": 1646085694329
                }
            },
            "errorFlag": true
        },
        {
            "timestamp": 1646085686891,
            "details": "Executing Task: Site Config Task",
            "errorFlag": false
        }
********** OUTPUT TRUNCATED ***********
    ],
    "statusCode": 200
}
```

[Return to ToC](#table-of-contents)

---

### Get Device By ID

*Obtain the status and device information for a Plug and Play device.*

**Method**
<pre><code><b>GET</b></code></pre>

**API URL:**
```
https://<dnac_ip/hostname>:<port>/dna/intent/api/v1/onboarding/pnp-device/{id}
```
  > [API Docs](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-2-2-2-api-api-device-onboarding-pnp-get-device-by-id)

**Headers:**
```json
{
    "Content-Type": "application/json",
    "x-auth-token": <dnac_auth_token>
}
```

**URL Parameters:**

```
id=<device_id>
```

  > *NOTE: These parameters are specified as part of the API URL and are required.  NOTE: The "device ID" is obtained from the [Get PnP Device List](#get-pnp-device-list) API - this is NOT the device's UUID.*

**Response:**

```json
{
    "version": 2,
    "deviceInfo": {
        "serialNumber": "FJC2330E0NJ",
        "name": "FJC2330E0NJ",
        "agentType": "IOS",
        "pid": "C9300-24UX",
        "lastSyncTime": 0,
        "addedOn": 1645825410332,
        "lastUpdateOn": 1646153239165,
        "firstContact": 1645825410330,
        "lastContact": 1646153239163,
        "lastContactDuration": 5043,
        "provisionedOn": 1646153233729,
        "state": "Provisioned",
        "onbState": "Provisioned",
        "cmState": "Authenticated",
        "imageFile": "flash:packages.conf",
        "imageVersion": "17.3.4",
        "mode": "INSTALL",
        "httpHeaders": [
            {
                "key": "clientAddress",
                "value": "172.16.2.23"
            }
        ],
        "projectId": "5e82e20ea5e2ae000859f4c7",
        "workflowId": "621e4da7c754c051c27279bb",
        "projectName": "Default",
        "workflowName": "Default_621e4da7c754c051c27279ba",
        "siteId": "ec9519f5-db86-4454-9883-a0a4b45b572d",
        "siteName": "Global/Minneapolis, MN/HQ/Floor 4",
********** OUTPUT TRUNCATED ***********
        "capwapBackOff": false,
        "redirectionState": "NONE",
        "dayN": false,
        "errorDetails": {
            "timestamp": 1646152821793,
            "details": "NCOB02073: Unexpected reload detected",
            "errorFlag": true
        },
        "deviceCheckpoint": "PROVISIONED",
        "dayNClaimOperation": "NO_OP",
        "tlsState": "NO_OP",
        "reProvision": false,
        "authOperation": "AUTHORIZATION_NOT_REQUIRED",
        "apProvisionStatus": "DAY0",
        "stack": false,
        "sudiRequired": false,
        "validActions": {
            "editSUDI": false,
            "editWfParams": false,
            "delete": true,
            "claim": false,
            "unclaim": false,
            "reset": false,
            "authorize": false,
            "editWfParamsMsg": "This device has completed provisioning. This device may be deleted. No other actions are applicable.",
            "editSUDIMsg": "This device has completed provisioning. This device may be deleted. No other actions are applicable.",
            "claimMsg": "This device has completed provisioning. This device may be deleted. No other actions are applicable.",
            "resetMsg": "This device has completed provisioning. This device may be deleted. No other actions are applicable.",
            "authorizeMsg": "This Device is not in PendingAuthorization state."
        },
        "siteClaimType": "Default"
    },
    "workflowParameters": {
        "configList": [
            {
                "configId": "57b73266-131e-427d-8edd-7262812aefca",
                "configParameters": [
                    {
                        "key": "hostname",
                        "value": "EdgeSW2"
                    },
                    {
                        "key": "VLAN_ID",
                        "value": 100
                    },
                    {
                        "key": "voice_vlan_name",
                        "value": "Voice_VLAN"
                    }
                ]
            }
        ]
    },
    "dayNCmdQueue": [],
    "runSummaryList": [
        {
            "timestamp": 1646153234767,
            "details": "Device added to Site Global/Minneapolis, MN/HQ/Floor 4",
            "errorFlag": false
        }
    ],
    "tenantId": "5c6cd3c78476f9009032101f",
    "id": "62194d82c754c051c271a638"
}
```

[Return to ToC](#table-of-contents)

---
---

## References

 - [DNA Center Journey - Config Guides](https://www.cisco.com/c/m/en_us/products/cloud-systems-management/dna-center/use-case-device-onboarding.html#~your-cisco-dna-center-journey)
 - [DNA Center API Docs](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-2-2-2-api-api-authentication-import-certificate)
 - [DNA Center API Onboarding Guide](https://developer.cisco.com/docs/dna-center/#!device-onboarding/device-onboarding-guide)
 - [Cisco Blogs - Adam Radford](https://blogs.cisco.com/author/adamradford)
 - [Github - DNAC Onboarding Tools - Adam Radford](https://github.com/CiscoDevNet/DNAC-onboarding-tools)

[Return to ToC](#table-of-contents)

---
