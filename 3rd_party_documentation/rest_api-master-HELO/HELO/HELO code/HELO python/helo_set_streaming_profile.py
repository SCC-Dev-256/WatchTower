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

"""helo_set_streaming_profile - Select a Streaming Profile for a HELO.
   Uses the python 'requests' library, which must be installed.

   :param device_url: complete URL string to address your HELO.  ('http://ip_address')
   :param profile_num: an integer, 0 through 9

   Example: $ python helo_set_streaming_profile.py http://192.168.0.2 0
   """

__author__ = "AJA Video Systems, Inc."
__version__ = "$Revision: 1.0 $"
__copyright__ = "Copyright (C) 2012, 2015 AJA Video Systems, Inc."
__license__ = "Apache 2.0"

##################################################################################################

import sys
try:
    import requests # HTTP for Humans
except ImportError:
    print("Please install the Python requests library. Try 'pip install requests'")
    raise

# Command-line arguments
device_url=sys.argv[1]  
profile_num=sys.argv[2]
exit_status = 1 # Assume error

# set streaming profile
param_id = "eParamID_StreamingProfileSel"
value = int(profile_num)
profile_url = "{url}/config?action=set&paramid={p}&value={v}".format(url=device_url, p=param_id, v=value)
             
response = requests.get(profile_url)
if  (response.status_code == requests.codes.ok):
    print("Profile {p} selected.  (eParamID_StreamingProfileSel set to {v}.)".format(p=profile_num, v=value))
    exit_status = 0 # success

sys.exit(exit_status)  # Return to OS

