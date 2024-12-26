#!/bin/bash

###############################################################################
#
# helo_stop_streaming - bash shell script to stop a HELO from Streaming, using
# the cURL utility.
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


# 'main' stop_stream function
function stop_stream
{
	local DEVICE_URL=$1

	echo "Stopping Stream on HELO at ${DEVICE_URL}"

	local PARAM_ID="eParamID_ReplicatorCommand"
	local VALUE=4 	# Value for "Stop Streaming" Replicator command]

	echo "curling with URL ${DEVICE_URL}/config?action=set&paramid=${PARAM_ID}&value=${VALUE}"
	curl "${DEVICE_URL}/config?action=set&paramid=${PARAM_ID}&value=${VALUE}"
	
	return $?
} # end of stop_stream

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

# Call the stop_stream function
stop_stream "${DEVICE_URL}"

exit $?
