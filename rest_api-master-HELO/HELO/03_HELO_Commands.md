<head>
<meta charset="utf-8">
<title>AJA REST API - Chapter 03 - HELO Commands</title>
</head>
# Common HELO Commands

* [Recording and Streaming](#recording-and-streaming-commands)

* [Selecting Profiles](#selecting-profiles)

* [Setting the Recording Name](#setting-the-recording-name)

* [Checking the Status of Recording and Streaming](#checking-the-status-of-recording-and-streaming)

* [Recalling Presets](#recalling-presets)

* [Dealing with Authentication](#dealing-with-authentication)

* [Downloading Clips](#download-clips)



<a name="recording-and-streaming-commands">&nbsp;</a>
### Recording and Streaming Commands

The HELO subsystem which controls video delivery is known as the Replicator. You can 
control Recording and Streaming independently with the *ReplicatorCommand* parameter.

#### eParamID_ReplicatorCommand Parameter Descriptor

```json
[
  {
    "param_type": "enum",
    "descriptor_type": "enum",
    "param_id": "eParamID_ReplicatorCommand",
    "param_name": "Replicator Command",
    "persistence_type": "ephemeral",
    "register_type": "excluded",
    "factory_reset_type": "never",
    "relations": {
      
    },
    "class_names": [
      "volatile",
      "leave_enabled_during_transport"
    ],
    "string_attributes": [
      {
        "name": "description",
        "value": "Transport command."
      },
      {
        "name": "menu_number",
        "value": "125.1"
      }
    ],
    "integer_attributes": [
      
    ],
    "enum_values": [
      {
        "value": 0,
        "text": "No Command",
        "short_text": "No Command"
      },
      {
        "value": 1,
        "text": "Record Command",
        "short_text": "Record Command"
      },
      {
        "value": 2,
        "text": "Stop Recording Command",
        "short_text": "Stop Recording Command"
      },
      {
        "value": 3,
        "text": "Stream Command",
        "short_text": "Stream Command"
      },
      {
        "value": 4,
        "text": "Stop Streaming Command",
        "short_text": "Stop Streaming Command"
      },
      {
        "value": 5,
        "text": "Shutdown",
        "short_text": "Shutdown"
      }
    ],
    "min_value": 0,
    "max_value": 5,
    "default_value": 0,
    "adjust_by": 1,
    "scale_by": 1,
    "offset_by": 0,
    "display_precision": 0,
    "units": ""
  }
]
```


####  To Start Recording

To start recording, set the 'eParamID_ReplicatorCommand' to the value of "1". 

```
    http://192.168.0.2/config?action=set&paramid=eParamID_ReplicatorCommand&value=1
```

#### To Stop Recording

To stop recording, set the 'eParamID_ReplicatorCommand' to the value of "2". 

```
    http://192.168.0.2/config?action=set&paramid=eParamID_ReplicatorCommand&value=2
```

#### To Start Streaming

To start streaming, set the 'eParamID_ReplicatorCommand' to the value of "3". 

```
    http://192.168.0.2/config?action=set&paramid=eParamID_ReplicatorCommand&value=3
```

#### To Stop Streaming

To start streaming, set the 'eParamID_ReplicatorCommand' to the value of "4". 

```
    http://192.168.0.2/config?action=set&paramid=eParamID_ReplicatorCommand&value=4
```
<a name="selecting-profiles">&nbsp;</a>
### Selecting Profiles

You can select Recording and Streaming Profiles independently with the 
*eParamID_RecordingProfileSel* and *eParamID_StreamingProfileSel* parameters. 

#### eParamID_RecordingProfileSel Parameter Descriptor

```json
[
  {
    "param_type": "enum",
    "descriptor_type": "enum",
    "param_id": "eParamID_RecordingProfileSel",
    "param_name": "Recording Profile",
    "persistence_type": "persistent",
    "register_type": "included",
    "factory_reset_type": "warm",
    "relations": {
      
    },
    "class_names": [
      
    ],
    "string_attributes": [
      {
        "name": "description",
        "value": "Selects a recording profile."
      },
      {
        "name": "menu_number",
        "value": "86.1"
      }
    ],
    "integer_attributes": [
      {
        "name": "ParamGroup",
        "value": 5
      }
    ],
    "enum_values": [
      
    ],
    "min_value": 0,
    "max_value": 9,
    "default_value": 0,
    "adjust_by": 1,
    "scale_by": 1,
    "offset_by": 0,
    "display_precision": 0,
    "units": ""
  }
]
```

#### To Select a Recording Profile

To select a recording profile, set the 'eParamID_RecordingProfileSel' to a numeric 
value with a minimum value of "0" and a maximum value of "9". 

```
    http://192.168.0.2/config?action=set&paramid=eParamID_RecordingProfileSel&value=X
```

#### eParamID_StreamingProfileSel Parameter Descriptor

```json
[
  {
    "param_type": "enum",
    "descriptor_type": "enum",
    "param_id": "eParamID_StreamingProfileSel",
    "param_name": "Streaming Profile",
    "persistence_type": "persistent",
    "register_type": "included",
    "factory_reset_type": "warm",
    "relations": {
      
    },
    "class_names": [
      
    ],
    "string_attributes": [
      {
        "name": "description",
        "value": "Selects a streaming profile."
      },
      {
        "name": "menu_number",
        "value": "87.1"
      }
    ],
    "integer_attributes": [
      {
        "name": "ParamGroup",
        "value": 6
      }
    ],
    "enum_values": [
      
    ],
    "min_value": 0,
    "max_value": 9,
    "default_value": 0,
    "adjust_by": 1,
    "scale_by": 1,
    "offset_by": 0,
    "display_precision": 0,
    "units": ""
  }
]
```

#### To Select a Streaming Profile

To select a streaming profile, set the 'eParamID_StreamingProfileSel' to a numeric 
value with a minimum value of "0" and a maximum value of "9". 

```
    http://192.168.0.2/config?action=set&paramid=eParamID_StreamingProfileSel&value=X
```

<a name="setting-the-recording-name">&nbsp;</a>
### Setting the Recording Name

You can assign a base name for each recorded file.

Important: **URLs may not contain spaces**. If you wish to set a value that 
contains spaces, all of the spaces need to be replaced by "+" or "%20".

Similarily, **URLs may not contain other characters with special meanings**.
Characters like **?, &, %, /, \, :** and others have special meanings in URLs 
and must be encoded.

**URLs may not contain non-ASCII characters**.  

To set a value that contains chacters with special meanings or non-ASCII 
characters (including but not limited to kanji, katakana and hirigana, 
cyrillic, arabic, hebrew, and latin characters with diacritical marks such as ñ,
à, ç, é, ê, í, ó, ö, ...), encode the special and non-ASCII characters using 
"URL Encoding".  URL Encoding is also known as "Percent Encoding".  This web 
page will perform the encoding for you: https://www.w3schools.com/tags/ref_urlencode.asp

#### To Set the Recording Name

To change the filename prefix from the default of "clip" to "Biology Lecture", 
for example, use the following command:

```
http://192.168.0.2/config?action=set&paramid=eParamID_FilenamePrefix&value=Biology%20Lecture
```
<a name="checking-the-status-of-recording-and-streaming">&nbsp;</a>
### Checking the Status of Recording and Streaming

The current operating state of the Replicator's Recording engine and Streaming engine 
are available through the parameter descriptors 'eParamID\_ReplicatorRecordState' and 
'eParamID\_ReplicatorStreamState'.

```
    http://192.168.0.2/config?action=get&paramid=eParamID_ReplicatorRecordState
```

The response should look something like:

```javascript
    {"paramid":"2097225226","name":"eParamID_ReplicatorRecordState","value":"1","value_name":"eRRSIdle"}
```

This shows the record state value is "1", which corresponds to the name "eRRSIdle" -- Replicator Record State Idle.

#### eParamID_ReplicatorRecordState Parameter Descriptor

```json
[
  {
    "param_type": "enum",
    "descriptor_type": "enum",
    "param_id": "eParamID_ReplicatorRecordState",
    "param_name": "Replicator Record State",
    "persistence_type": "ephemeral",
    "register_type": "excluded",
    "factory_reset_type": "never",
    "relations": {
      
    },
    "class_names": [
      "readonly",
      "panel_hidden"
    ],
    "string_attributes": [
      {
        "name": "description",
        "value": "Current replicator record state."
      },
      {
        "name": "menu_number",
        "value": "125.1"
      }
    ],
    "integer_attributes": [
      
    ],
    "enum_values": [
      {
        "value": 0,
        "text": "eRRSUninitialized",
        "short_text": "eRRSUninitialized"
      },
      {
        "value": 1,
        "text": "eRRSIdle",
        "short_text": "eRRSIdle"
      },
      {
        "value": 2,
        "text": "eRRSRecording",
        "short_text": "eRRSRecording"
      },
      {
        "value": 3,
        "text": "eRRSFailingInIdle",
        "short_text": "eRRSFailingInIdle"
      },
      {
        "value": 4,
        "text": "eRRSFailingInRecord",
        "short_text": "eRRSFailingInRecord"
      },
      {
        "value": 5,
        "text": "eRRSShutdown",
        "short_text": "eRRSShutdown"
      }
    ],
    "min_value": 0,
    "max_value": 5,
    "default_value": 0,
    "adjust_by": 1,
    "scale_by": 1,
    "offset_by": 0,
    "display_precision": 0,
    "units": ""
  }
]
```

<a name="recalling-presets">&nbsp;</a>
### Recalling Presets


#### To Recall Preset #2

```
    http://192.168.0.2/config?action=set&paramid=eParamID_RegisterRecall&value=2
```

Wait a while.  Then you can check whether the recall completed successfully.

```
    http://192.168.0.2/config?action=set&paramid=eParamID_RegisterRecallResult
```
    
The resulting http response should look something like:

```javascript
    {"paramid":"1560412160","name":"eParamID_RegisterRecallResult","value":"2","value_name":"Complete"}
```

This shows the result value is "2", which corresponds to the name "Complete".

<a name="dealing-with-authentication">&nbsp;</a>
### Dealing with Authentication

You can disable or enable authentication with the *eParamID_Authentication* parameter. 

#### eParamID_Authentication Parameter Descriptor

```json
[
  {
    "param_type": "enum",
    "descriptor_type": "enum",
    "param_id": "eParamID_Authentication",
    "param_name": "User Authentication",
    "persistence_type": "persistent",
    "register_type": "excluded",
    "factory_reset_type": "cold",
    "relations": {},
    "class_names": [
      "volatile"
    ],
    "string_attributes": [
      {
        "name": "description",
        "value": "Enables or disables password protection for the web interface for this system."
      },
      {
        "name": "menu_number",
        "value": "50.9"
      }
    ],
    "integer_attributes": [
      {
        "name": "ParamGroup",
        "value": 12
      }
    ],
    "enum_values": [
      {
        "value": 0,
        "text": "Disabled",
        "short_text": "Disabled"
      },
      {
        "value": 1,
        "text": "Login",
        "short_text": "Login"
      }
    ],
    "min_value": 0,
    "max_value": 1,
    "default_value": 0,
    "adjust_by": 1,
    "scale_by": 1,
    "offset_by": 0,
    "display_precision": 0,
    "units": ""
  }
]
```

#### To Disable Authentication

```
    http://192.168.0.2/config?action=set&paramid=eParamID_Authentication&value=0
```

#### To Enable Authentication

```
    http://192.168.0.2/config?action=set&paramid=eParamID_Authentication&value=1
```

When User Authentication is disabled--that is, when 'eParamID_Authentication' is 
set to the value 0--REST accesses can be completed without worrying about passwords 
or authentication. However, when User Authentication is enabled ('eParamID_Authentication' 
is set to the value 1) then REST accesses to HELO as described elsewhere will fail 
with an error that looks like this:

```
        <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
        <html><head><title>404 Not Found</title></head><body>
        The document requested was not found on this server.
        </body></html>
```

In order for REST commands to HELO to succeed when User Authentication is enabled, a few extra steps are necessary:

1. Send a request to authenticate to HELO which contains the password using POST.
2. Save the cookie the web server sends back in the authentication response.
3. Provide the cookie in each request from then on.

### Example: Get Record State with Authentication Enabled

Via cURL with a password of honk (HELO with IP address 10.3.36.88):

1. Authenticate with password via HTTP POST.

```
        $ curl -d "password_provided=honk" -X POST "http://10.3.36.88/authenticator/login" -i
        HTTP/1.1 200 OK
        Server: Seminole/2.71 (Linux; DF7)
        Date: Mon, 19 Mar 2018 19:13:11 GMT
        Connection: keep-alive
        Cache-Control: no-cache
        Content-Type: text/html
        Set-Cookie: session=0000000e-5Qn9uwpiYiMpCxePZekIwjeREBsBA6k; path=/
        Transfer-encoding: chunked

        {"login":"success"}
```

2. Save the cookie returned by the web server. The cookie sent back in the response above is: 

```
        session=0000000e-5Qn9uwpiYiMpCxePZekIwjeREBsBA6k; path=/
```

3. Return the cookie with each REST request. In this example the cookie is simply cut and pasted onto the command line. In production it would typically be stored in a file or variable.

```
        $ curl --cookie "session=0000000e-5Qn9uwpiYiMpCxePZekIwjeREBsBA6k; path=/" "10.3.36.88/config?action=get&paramid=eParamID_ReplicatorRecordState"
        {"paramid":"2097225226","name":"eParamID_ReplicatorRecordState","value":"3","value_name":"eRRSFailingInIdle"}
```

Repeat step 3 as desired.



<a name="download-clips">&nbsp;</a>
### Downloading Clips

You can download video clips that are in .mov format from your HELO device using the cURL command line utility. 

Before you can download clips, the HELO device first needs to be in Data Transfer mode (Data – LAN mode), which can be done with the 'eParamID_MediaState' parameter. This parameter defines whether the HELO device is in normal Record-Stream mode or Data Transfer mode. If a transfer is in progress when this parameter is set back to Record-Stream mode, the transfer will be aborted. 

Once you have completed downloading clips, return the value of the parameter 'eParamID_MediaState' back to "0" so that recording and streaming can be performed again. 

#### eParamID_MediaState

```json
[
  {
    "param_type": "enum",
    "descriptor_type": "enum",
    "param_id": "eParamID_MediaState",
    "param_name": "Media State",
    "persistence_type": "ephemeral",
    "register_type": "included",
    "factory_reset_type": "warm",
    "relations": {},
    "class_names": [
        "webapp_hidden"
    ],
    "string_attributes": [
        {
          "name": "description",
          "value": "Define whether the HELO device is in normal Record-Stream or Data Transfer mode."
        },
        {
          "name": "menu_number",
          "value": "12.1"
        }
    ],
    "integer_attributes": [
        {
          "name": "ParamGroup",
          "value": 3
        }
    ],
    "enum_values": [
        {
          "value": 0,
          "text": "Record-Stream",
          "short_text": "Record-Stream"
        },
        {
          "value": 1,
          "text": "Data-LAN",
          "short_text": "Data-LAN"
        }
    ],
    "min_value": 0,
    "max_value": 3,
    "default_value": 0,
    "adjust_by": 1,
    "scale_by": 1,
    "offset_by": 0,
    "display_precision": 0,
    "units": ""
  }
]
```

####  Data - LAN mode Command

To put the HELO device into Data - LAN mode, set the 'eParamID_MediaState' parameter to the value of "1". 

```
    http://192.168.0.2/config?action=set&paramid=eParamID_MediaState&value=1
```

####  Record - Stream mode Command

To put the HELO device back into Record - Stream mode so that recording and streaming can be performed again, set the 'eParamID_MediaState' parameter to the value of "0". 

```
    http://192.168.0.2/config?action=set&paramid=eParamID_MediaState&value=0
```


#### Download Command

To download a .mov file from a HELO device, use the cURL command line utility with a terminal prompt. 

In the following command example, '--output' instructs the server to create a new file rather than sending the download to your terminal window. 

'example-filename-downloaded.mov' refers to the file name of the file after it has been downloaded. You can use any file name you like. It doesn't need to match the file name of the file you are downloading from the HELO device. 'example-filename-source.mov' refers to the file name of the .mov file that is residing on your HELO device. 

```
    curl -v0 --output example-filename-downloaded.mov http://192.168.0.2/media0/example-filename-source.mov
```

Substitute the example IP address '192.168.0.2' with your actual HELO device URL address. 

Here is an example of the HTTP download request that AJA's browser-based javascript download initiates:

```
    GET /media0/example-filename-source.mov HTTP/1.1
    Host: 192.168.0.2
    Connection: keep-alive
```

This will initiate the download of a single file/clip from the currently selected media. 

Here is an example of the response that the client will get:

```
    HTTP/1.0 200 OK
    Content-Type: video/quicktime
    Content-disposition: attachment; filename=example-filename-source.mov
    Content-Length: 359354368
```



&nbsp;
