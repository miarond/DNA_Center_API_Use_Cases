# Powershell REST API Example Code

In some scenarios it may not be possible to download and install Python, Postman, Ansible, or even gain access to a Linux-based server, as is often the case with highly security-conscious networks.  In these situations, engineers may only have access to standardized Microsoft Windows operating systems with just the built-in tools, like Powershell.  Fortunately, Powershell includes a module named "Invoke-RestMethod" which can be used for crafting and sending REST API messages, and can be leveraged in Powershell scripts to perform the basic functionality available from out-of-the-box Python.

Below are some example Powershell code snippets to help you understand the "Invoke-RestMethod" module and leverage it to make API calls to the DNA Center platform.

## Understanding Syntax and Parameters

Documentation for the "Invoke-RestMethod" module can be found here: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-restmethod?view=powershell-7.3

The syntax for using the module follows the same guidelines as any Powershell module, and the documentation above lists the available module Parameters.  The most useful module Parameters are:

#### `-Method`
  * Specifies the HTTP Verb, or Method, of the API call.  This will typically be one of the following values: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
  * Example:
    ```powershell
    Invoke-RestMethod -Method "GET"
    ```
#### `-Uri`
  * Specifies the "URI" or web address of the target API endpoint.
  * Example:
    ```powershell
    Invoke-RestMethod -Method "GET" -Uri "http://httpbin.org/get"
    ```
#### `-ContentType`
  * Tells the target server what format type to expect in the body of the HTTP message.  Most often with REST APIs, this will be `application/json`, indicating that the body is in JSON format.
  * Example:
    ```powershell
    Invoke-RestMethod -Method "GET" -Uri "http://httpbin.org/get" -ContentType "application/json"
    ```
#### `-Authentication`
  * For API endpoints which require an authentication mechanism, this parameter specifies the authentication scheme being used.  Available options are: `None`, `Basic`, `Bearer`, and `OAuth`
  * Example:
    ```powershell
    Invoke-RestMethod -Method "GET" -Uri "http://httpbin.org/get" -ContentType "application/json" -Authentication "Basic"
    ```
  * When `Basic` is specified, the `-Credential` parameter must also be specified along with a Base64-encoded string of `username:password`.  This can easily be accomplished with an additional interactive Powershell module, named `Get-Credential`.  Below is an example snippet of code:
    ```powershell
    # Create a new variable named "creds" to store the object created by Get-Credential
    $creds = Get-Credential
    Enter your credentials.
    User: username
    Password for user username: ********

    # Note: We've switched to using Cisco DevNet's Sandbox DNA Center for this example
    Invoke-RestMethod -Method "POST" -Uri "https://sandboxdnac.cisco.com/api/system/v1/auth/token" -ContentType "application/json" -Authentication "Basic" -Credential $creds
    ```
  * When `Bearer` or `OAuth` are specificed, the `-Token` parameter must also be specified, containing the token string stored as a Powershell "SecureString".  The SecureString can be created interactively by typing in the plain-text on the Powershell CLI immediately after running the example code snippet below:
    ```powershell
    # Note: The "-AllowUnencryptedAuthentication" parameter is only required here because the URI is using HTTP, instead of HTTPS
    Invoke-RestMethod -Method "GET" -Uri "http://httpbin.org/bearer" -ContentType "application/json" -Authentication "Bearer" -Token (Read-Host -AsSecureString) -AllowUnencryptedAuthentication
    ********
    # Output below for reference
    authenticated token
    ------------- -----
             True abcd1234
    ```
#### `-Headers`
  * Allows you to define specific keys and values to be contained in the Header section of the HTTP message.  The `-Headers` parameter **REQUIRES** that you pass a Powershell IDictionary object as an argument, so you must construct one first.
  * Example:
    ```powershell
    # Create an IDictionary named "headers" containing the keys and values specified inside the {}
    $headers = @{
        "Cache-Control" = "nocache"
        "accept" = "application/json"
        "my-header-key" = "my header value"
    }
    Invoke-RestMethod -Method "GET" -Uri "http://httpbin.org/anything" -ContentType "application/json" -Headers $headers
    ```
#### `-Body`
  * Allows you to specify the content of the HTTP message body.  When the HTTP Method is set to `GET` and an IDictionary is passed to the `-Body` parameter, the contents of the IDictionary object are sent as Query Parameters in the HTTP message.  Strings can also be passed to the `-Body` parameter, containing raw text content or a single `key=value` formats.
  * Example:
    ```powershell
    # Example of sending multiple Query Parameters in an API call
    $query_params = @{
        "query1" = "value1"
        "query2" = "value2"
    }
    Invoke-RestMethod -Method "GET" -Uri "http://httpbin.org/anything" -ContentType "application/json" -Body $query_params
    ```
    ```powershell
    # Example of sending raw text in the Body
    Invoke-RestMethod -Method "POST" -Uri "http://httpbin.org/anything" -ContentType "application/json" -Body "This is the raw text body"
    ```
#### `-ResponseHeadersVariable`
  * Allows you to specify a variable name to capture and store the HTTP Headers from the response data.
  * Example:
    ```powershell
    Invoke-RestMethod -Method "POST" -Uri "http://httpbin.org/anything" -ContentType "application/json" -Body "This is the raw text body" -ResponseHeadersVariable "rheaders"

    # Contents of "rheaders" variable for reference
    $rheaders

    Key                              Value
    ---                              -----
    Date                             {Fri, 06 Jan 2023 21:36:07 GMT}
    Connection                       {keep-alive}
    Server                           {gunicorn/19.9.0}
    Access-Control-Allow-Origin      {*}
    Access-Control-Allow-Credentials {true}
    Content-Type                     {application/json}
    Content-Length                   {562}
    ```
#### `-OutFile`
  * Allows you specify a filename to write the captured response data to.
  * Example:
    ```powershell
    Invoke-RestMethod -Method "POST" -Uri "http://httpbin.org/anything" -ContentType "application/json" -Body "This is the raw text body" -OutFile "example.json"

    cat example.json
    {
        "args": {}, 
        "data": "This is the raw text body", 
        "files": {}, 
        "form": {}, 
        "headers": {
            "Content-Length": "25", 
            "Content-Type": "application/json", 
            "Host": "httpbin.org", 
            "User-Agent": "Mozilla/5.0 (Macintosh; Darwin 22.2.0 Darwin Kernel Version 22.2.0: Fri Nov 11 02:08:47 PST 2022; root:xnu-8792.61.2~4/RELEASE_X86_64; en-US) PowerShell/7.3.1", 
            "X-Amzn-Trace-Id": "Root=1-63b8951a-2dabb9f87292fe1f041e071c"
        }, 
        "json": null, 
        "method": "POST", 
        "origin": "72.163.2.238", 
        "url": "http://httpbin.org/anything"
    }
    ```
#### `-SkipCertificateCheck`
  * Allows you to bypass the SSL Certification Verification check for HTTPS API calls.  **This parameter is necessary when the API server is using a self-signed SSL certificate.**
  * Example:
    ```powershell
    Invoke-RestMethod -Method "GET" -Uri "https://sandboxdnac.cisco.com/dna/intent/api/v1" -SkipCertificateCheck
    ```

## DNA Center API Example Code

### Authentication

Long-form method:
```powershell
# Create a PSCredential object
$creds = Get-Credential
# Enter your credentials.
# User: username
# Password for user username: ********

# Example using long method
# Response data captured in a variable named "response"
$response = Invoke-RestMethod -Method "POST" -Authentication "Basic" -Credential $creds -ContentType "application/json" -Uri "https://sandboxdnac.cisco.com/api/system/v1/auth/token" -SkipCertificateCheck

# Store JWT token in new variable for use in upcoming API calls
$token = $response.Token
```

Condensed code format:
```powershell
# Create a PSCredential object
$creds = Get-Credential
# Enter your credentials.
# User: username
# Password for user username: ********

$params = @{
    Method = "POST"
    Uri = "https://sandboxdnac.cisco.com/api/system/v1/auth/token"
    ContentType = "application/json"
    Authentication = "Basic"
    Credential = $creds
}
$response = Invoke-RestMethod @params -SkipCertificateCheck

# Store JWT token in new variable for use in upcoming API calls
$token = $response.Token
```

### Get Device List

```powershell
$params = @{
    Method = "GET"
    Uri = "https://sandboxdnac.cisco.com/dna/intent/api/v1/network-device"
    ContentType = "application/json"
}

# Pass JWT token on all API calls, using "x-auth-token" header
$headers = @{
    "x-auth-token" = $token
}

# Optional Query Parameters to filter returned data. 
# Remove "#" comment symbol to use any of the Query Parameters below
$query = @{
    #hostname = "<device_hostname>"
    #managementIpAddress = "<device_management_ip>"
    #macAddress = "<device_mac_address>"
    #family = "<dnac_device_family>"
    #type = "<dnac_device_type>"
    #serialNumber = "<device_serial_number>"
    #platformId = "<device_pid>"
    #role = "<dnac_device_role>"
    #id = "<dnac_device_uuid>"
}

# If not using Query Parameters, omit "-Body" parameter
$response = Invoke-RestMethod @params -Headers $headers -Body $query -SkipCertificateCheck

# Print response data to screen
$response.response
```

*Optional method to save JSON response data to a file.  The `Invoke-RestMethod` module returns response data inside an object named "response", so when the `-OutFile` parameter is used, or the output is captured in a Powershell variable, it will not be stored in proper JSON format at the root level.*

*This method extracts only the contents of the "response" object, converts it to JSON format and saves it to an output file.*
```powershell
(Invoke-RestMethod @params -Headers $headers -Body $query -SkipCertificateCheck).response | ConvertTo-Json -depth 10 | Out-File "output.json"
```
