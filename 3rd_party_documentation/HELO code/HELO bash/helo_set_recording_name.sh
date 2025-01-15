#!/bin/bash

###############################################################################
#
# helo_set_recording_name - bash shell script to set the Filename Prefix for
# recordings, using the cURL utility.
#
###############################################################################
#
# Copyright 2017 AJA Video Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

usage() 
{
  echo "Usage: $0 -u <url_string> -p <prefix_string>"
  exit 1
}


# 'main' set_recording_name function
function set_recording_name
{
	local DEVICE_URL=$1
	local RECORDING_NAME=$2

	echo "Selecting Filename Prefix ${RECORDING_NAME} on HELO at ${DEVICE_URL}"

	local PARAM_ID="eParamID_FilenamePrefix"

	echo "curling with URL ${DEVICE_URL}/config?action=set&paramid=${PARAM_ID}&value=${RECORDING_NAME}"
	# Declaring and assigning the local variable here in one statement will hide the exit code from cURL
	local RESPONSE
	RESPONSE=$(curl "${DEVICE_URL}/config?action=set&paramid=${PARAM_ID}&value=${RECORDING_NAME}")
	local CURL_RESULT=$?
	echo "Response: ${RESPONSE}"
	return ${CURL_RESULT}
} # end of set_recording_name

#####
##### main

# Check dependencies

# Ensure curl is available.  More at https://curl.haxx.se/
hash curl 2>/dev/null || { echo >&2 "I require curl, a command-line tool for transferring data with URLs, but I can't find it.  Aborting."; exit 1; }

# Parse command line options
while getopts ":u:p:" opt; do
    case "${opt}" in
        u)
            u=${OPTARG}
            ;;
        p)
            p=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# Ensure we recived all required command line arguments
if [ -z "${u}" ]; then
    usage
fi
if [ -z "${p}" ]; then
    usage
fi

echo "Device URL = ${u}"
echo "Filename Prefix = ${p}"

# Process command-line arguments
DEVICE_URL=${u}
RECORDING_NAME=${p}

# Call the set_recording_name function
set_recording_name "${DEVICE_URL}" "${RECORDING_NAME}" 

exit $?
