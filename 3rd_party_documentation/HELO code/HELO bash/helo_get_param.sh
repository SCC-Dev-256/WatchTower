#!/bin/bash

###############################################################################
#
# helo_get_param - bash shell script to get the value of a parameter from a 
# HELO, by value or by name, using the cURL(1) utility.
#
# GETs the param and uses the jq(2) utility to return either the param value
# or the associated valuename
#
#
# Examples:
# 
# $ # 1) Get current replicator record state name
# $ helo_get_param.sh -u 10.3.36.88 -p eParamID_ReplicatorRecordState -n
# eRRSRecording
# 
# $ 2) Is replicator record state equal to eRRSIdle?
# $ helo_get_param.sh -u 10.3.36.88 -p eParamID_ReplicatorRecordState -i eRRSIdle -n
# $ echo \$?
# 1
# $ # It's not.  Unix convention, 0 == success, anything else is false or error
#
#---------------------------------------------------
#
# References:
#
# 1) curl: https://curl.haxx.se/
# 2) jq: https://stedolan.github.io/jq/
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
	echo "Usage: $0 -u <url_string> -p <paramid> [-i <match_string>] [-n | -j]" 
    echo ""
	echo "Options:"
    echo ""
	echo "  -i                 is; returns 1 if match, 0 if not.  Default is match by value."
	echo "                     Use -n to match by name."
	echo "  -j                 show response as pretty-printed JSON "
	echo "  -n                 output value name instead of value"
	echo "  -p                 parameter identifer"
	echo "  -u                 URL of AJA device"
	echo ""
	echo "Examples:"
	echo ""
	echo "$ # Get current replicator record state name"
	echo "$ helo_get_param.sh -u 10.3.36.88 -p eParamID_ReplicatorRecordState -n"
	echo "eRRSRecording"
	echo ""
	echo "$ # Is replicator record state equal to eRRSIdle?"
	echo "$ helo_get_param.sh -u 10.3.36.88 -p eParamID_ReplicatorRecordState -i eRRSIdle -n"
	echo "$ echo \$?"
	echo "1"
	echo "$ # It's not.  Unix convention, 0 == success, anything else is false or error" 
	echo ""
	
	exit 1; 
}

#####
##### main

# Check dependencies

# Ensure jq is available.  More at https://stedolan.github.io/jq/
hash jq 2>/dev/null || { echo >&2 "I require jq, a lightweight command-line JSON processor but I can't find it.  Aborting."; exit 1; }

# Ensure curl is available.  More at https://curl.haxx.se/
hash curl 2>/dev/null || { echo >&2 "I require curl, a command-line tool for transferring data with URLs, but I can't find it.  Aborting."; exit 1; }

# Option control variables
matchString=""
jsonField=".value"
prettyPrint=false

# Parse command line options
while getopts ":i:jnp:u:" opt; do
    case "${opt}" in
        i)
            matchString=${OPTARG}
            ;;
        n)
            jsonField=".value_name"
            ;;
        j)
            prettyPrint=true;
            ;;
        p)
            paramId=${OPTARG}
            ;;
        u)
            deviceUrl=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# Ensure we recived all required command line arguments
if [ -z "${deviceUrl}" ] || [ -z "${paramId}" ]; then
	echo "Missing arguments"
    usage
fi

# Use cURL to get the current value of parameter specified by paramId 
httpResp=$(curl -s "${deviceUrl}/config?action=get&paramid=${paramId}")

# Pretty Print full JSON response if requested; useful for debugging
if [ "${prettyPrint}" = true ] ; then
	echo "$httpResp" | jq -r .
fi

# Parse JSON response and check match if requested; exit with 0 for match.
# Otherwise output value
jqResp=$(echo "$httpResp" | jq -r "${jsonField}")
if [ "${matchString}" != "" ]; then
	[ "${matchString}" = "${jqResp}" ]
	exit $?
else
	echo "${jqResp}"
fi
exit 0
