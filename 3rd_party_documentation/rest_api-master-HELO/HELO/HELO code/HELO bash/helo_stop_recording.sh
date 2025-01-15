#!/bin/bash

###############################################################################
#
# helo_stop_recording - bash shell script to stop a HELO from Recording, using
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

# 'main' stop_record function
function stop_record
{
	local DEVICE_URL=$1

	echo "Stopping Record on HELO at ${DEVICE_URL}"

	local PARAM_ID="eParamID_ReplicatorCommand"
	local VALUE=2 	# Value for "Stop Recording" Replicator command]

	echo "curling with URL ${DEVICE_URL}/config?action=set&paramid=${PARAM_ID}&value=${VALUE}"
	curl "${DEVICE_URL}/config?action=set&paramid=${PARAM_ID}&value=${VALUE}"
	
	return $?
} # end of stop_record

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
DEVICE_URL=${u}

# Call the stop_record function
stop_record "${DEVICE_URL}"

exit $?
