#! /usr/bin/env python

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

"""helo_stop_recording - Send a 'stop recording' command to the HELO's Replicator.  
   Uses the python 'requests' library, which must be installed.
   
   :param device_url: complete URL string to address your HELO.  ('http://ip_address')

   Example: $ python helo_stop_recording.py http://192.168.0.2
   """

__author__ = "AJA Video Systems, Inc."
__version__ = "$Revision: 1.0 $"
__copyright__ = "Copyright (C) 2017 AJA Video Systems, Inc."
__license__ = "Apache 2.0"

##################################################################################################

import sys
try:
    import requests # HTTP for Humans
except ImportError:
    print("Please install the Python requests library. Try 'pip install requests'")
    raise

    
replicator_command_map = {"START_RECORDING" : 1,
                          "STOP_RECORDING"  : 2,
                          "START_STREAMING" : 3,
                          "STOP_STREAMING"  : 4}

device_url=sys.argv[1]  # Command-line argument should be our URL.
exit_status = 1 # Assume error

# stop record
param_id = "eParamID_ReplicatorCommand"
value = replicator_command_map["STOP_RECORDING"]
stop_url = "{url}/config?action=set&paramid={p}&value={v}".format(url=device_url, p=param_id, v=value)
             
response = requests.get(stop_url)
if  (response.status_code == requests.codes.ok):
    print("Stopping Recording...")
    exit_status = 0 # success

sys.exit(exit_status)  # Return to OS

