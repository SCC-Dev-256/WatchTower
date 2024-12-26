#!/bin/bash

###############################################################################
#
# helo_set_streaming_profile - bash shell script to select a Streaming Profile
# on a HELO, using the cURL utility.
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
  echo "Usage: $0 -u <url_string> -p <profile_num>"
  exit 1
}


# 'main' select_streaming_profile function
function select_streaming_profile
{
	local DEVICE_URL=$1
	local PROFILE_NUM=$2

	echo "Selecting Streaming Profile ${PROFILE_NUM} on HELO at ${DEVICE_URL}"

	local PARAM_ID="eParamID_StreamingProfileSel"

	echo "curling with URL ${DEVICE_URL}/config?action=set&paramid=${PARAM_ID}&value=${PROFILE_NUM}"
	# Declaring and assigning the local variable here in one statement will hide the exit code from cURL
	local RESPONSE
	RESPONSE=$(curl "${DEVICE_URL}/config?action=set&paramid=${PARAM_ID}&value=${PROFILE_NUM}")
	local CURL_RESULT=$?
	echo "Response: ${RESPONSE}"
	# The Descriptor for eParamID_StreamingProfileSel indicates that it is an "enum" type parameter,
	# but its 'enum_values' list is empty, which may cause some consternation.
	echo 'NOTE: Response may indicate "value_name":"Invalid".  This is normal.'
	return ${CURL_RESULT}
} # end of select_streaming_profile

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
echo "Streaming Profile # = ${p}"

# Process command-line arguments
DEVICE_URL=${u}
PROFILE_NUM=${p}

# Call the select_streaming_profile function
select_streaming_profile "${DEVICE_URL}" "${PROFILE_NUM}" 

exit $?
