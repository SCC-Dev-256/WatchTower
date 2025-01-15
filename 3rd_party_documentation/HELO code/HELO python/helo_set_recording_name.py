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

"""helo_set_recording_name - Select the Filename Prefix used for HELO recordings.
   'legalize' the given prefix if necessary.
   (URLs may not contain spaces or other characters with special meanings,
   nor non-ASCII characters.  These characters must be encoded.)
   Uses the python 'requests' library, which must be installed.

   :param device_url: complete URL string to address your HELO.  ('http://ip_address')
   :param filename_prefix: a string
   """

__author__ = "AJA Video Systems, Inc."
__version__ = "$Revision: 1.0 $"
__copyright__ = "Copyright (C) 2012, 2017 AJA Video Systems, Inc."
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
filename_prefix=sys.argv[2] 
exit_status = 1 # Assume error

'''Encode any special characters within the string.'''
'''requests has a quote utility to take care of this.'''
legalized_prefix = requests.utils.quote(filename_prefix)

# set name
param_id = "eParamID_FilenamePrefix"
name_url = "{url}/config?action=set&paramid={p}&value={n}".format(url=device_url, p=param_id, n=legalized_prefix)
             
response = requests.get(name_url)
if  (response.status_code == requests.codes.ok):
    print("Recording name set to {p}.".format(p=legalized_prefix))
    exit_status = 0 # success
else:
    print("Recording name could not be set to {p}.".format(p=legalized_prefix))

sys.exit(exit_status)  # Return to OS
