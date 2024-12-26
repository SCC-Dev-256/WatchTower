#!/bin/bash

###############################################################################
#
# helo_verify_recording.sh - bash shell script to check if a HELO is 
# recording, using the using the cURL utility.
#
# GETs the ReplicatorRecordState, prints the numeric value.
# Exits with 
#	0 if recording
#	1 if not recording
#   255 on error 
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

usage() { echo "Usage: $0 -u <url_string>"; exit 255; }

function jsonval {
	local json=$1
	local key=$2
    temp=`echo $json | sed 's/\\\\\//\//g' | sed 's/[{}]//g' | awk -v k="text" '{n=split($0,a,","); for (i=1; i<=n; i++) print a[i]}' | sed 's/\"\:\"/\|/g' | sed 's/[\,]/ /g' | sed 's/\"//g' | grep -w $key`
    echo ${temp##*|}
	return ${temp##*|}
}

# Get recording state, exit with 0 (true) if recording, 1 otherwise
function get_record_state
{
	local IS_RECORDING=1	# Assume False
	local DEVICE_URL=$1
	local VALUE=2			# 2 is the value for replicator record state recording

	echo "Checking record state on HELO at ${DEVICE_URL}"

	local PARAM_ID="eParamID_ReplicatorRecordState"

	echo "curling with URL ${DEVICE_URL}/config?action=get&paramid=${PARAM_ID}"
	local HTTP_RESPONSE=$(curl -sS "${DEVICE_URL}/config?action=get&paramid=${PARAM_ID}")

	# Call the quick-and-dirty JSON parsing function above.
	# For something more sophisticated, see helo_get_param.sh, which uses jq.
	jsonval $HTTP_RESPONSE 'value'
	[ $? -eq $VALUE ]
	IS_RECORDING=$?
	if [ "$IS_RECORDING" -eq 0 ]; then
		echo "${DEVICE_URL} is recording."
	else
		echo "${DEVICE_URL} is not recording."
	fi
	exit ${IS_RECORDING}
} # end of get_record_state

#####
##### main

# Check dependencies

# Ensure curl is available.  More at https://curl.haxx.se/
hash curl 2>/dev/null || { echo >&2 "I require curl, a command-line tool for transferring data with URLs, but I can't find it.  Aborting."; exit 1; }

# Parse command line options
while getopts ":u:" opt; do
    case "${opt}" in
        u)
            u=${OPTARG}
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

echo "Device URL = ${u}"

# Process command-line arguments
# Trim off trailing backslash if there is one so we don't end up with two;
# curl errors out on URLs like http://192.168.0.1//..."
DEVICE_URL=${u%/}

# Call the get_record_state function
get_record_state "${DEVICE_URL}"

# get_record_state exits, so we should never get here.
# In case we do, return error.
exit 255
