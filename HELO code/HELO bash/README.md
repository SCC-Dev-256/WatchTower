<head>
<meta charset="utf-8">
<title>[AJA REST API - Code - Bash Example Scripts](https://gitlab.aja.com/pub/rest_api/tree/master/code/bash)</title>
</head>

# Directory Contents:

Example bash scripts to interact with the AJA HELO via its REST API.

# Requirements:

* All scripts are written in the 'bash' shell scripting language and were
tested on Linux using bash v 4.2

* All scripts require the [cURL](https://curl.haxx.se/) command line utility

* Only the <samp>helo_get_param.sh</samp> script requires [jq](https://stedolan.github.io/jq/).
All others do not require it.

# License

All scripts are made available by AJA under the Apache License v2.0.

# Example Scripts

* <samp>helo_get_param.sh</samp> - Standalone script to get any HELO parameter by name.  Requires [jq](https://stedolan.github.io/jq/)

* <samp>helo_get_recording_state.sh</samp> - Check to see if HELO is recording

* <samp>helo_get_streaming_state.sh</samp> - Check to see if HELO is streaming

* <samp>helo_set_recording_name.sh</samp> - Set HELO's recording filename

* <samp>helo_set_recording_profile.sh</samp> - Select a recording profile

* <samp>helo_set_streaming_profile.sh</samp> - Select a streaming profile

* <samp>helo_start_recording.sh</samp> - Tell HELO to begin recording

* <samp>helo_start_streaming.sh</samp> - Tell HELO to begin streaming

* <samp>helo_stop_recording.sh</samp> - Tell HELO to cease recording

* <samp>helo_stop_streaming.sh</samp> - Tell HELO to cease streaming

