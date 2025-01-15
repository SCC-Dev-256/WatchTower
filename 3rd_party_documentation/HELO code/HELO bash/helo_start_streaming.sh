#!/bin/bash

###############################################################################
#
# helo_start_streaming.sh - bash shell script to Stream from a HELO, using the
# cURL utility.
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

usage() { echo "Usage: $0 -u <url_string>"; exit 1; }


# 'main' start_stream function
function start_stream
{
	local DEVICE_URL=$1

	echo "Starting Stream on HELO at ${DEVICE_URL}"

	local PARAM_ID="eParamID_ReplicatorCommand"
	local VALUE=3 	# Value for "Start Streaming" Replicator command]

	echo "curling with URL ${DEVICE_URL}/config?action=set&paramid=${PARAM_ID}&value=${VALUE}"
	curl "${DEVICE_URL}/config?action=set&paramid=${PARAM_ID}&value=${VALUE}"
	
	return $?
} # end of start_stream

#####
##### main

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

if [ -z "${u}" ]; then
    usage
fi

echo "Device URL = ${u}"

# Process command-line arguments
#DEVICE_URL=$1
DEVICE_URL=${u}

# Call the start_stream function
start_stream "${DEVICE_URL}"

exit $?
