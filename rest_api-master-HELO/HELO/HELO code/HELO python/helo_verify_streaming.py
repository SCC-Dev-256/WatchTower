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

"""helo_verify_streaming - Verify that a HELO is Streaming, using the python requests library."""

__author__ = "AJA Video Systems, Inc."
__version__ = "$Revision: 1.0 $"
__copyright__ = "Copyright (C) 2012, 2017 AJA Video Systems, Inc."
__license__ = "Apache 2.0"

##################################################################################################

import logging  # in order for basicConfig to work properly, logging must be imported before anything else!!!
logging.basicConfig(format='%(levelname)s::%(module)s::%(funcName)s::%(lineno)s::%(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

import requests # HTTP for Humans
#logging.getLogger("requests").setLevel(logging.DEBUG) # We can set the logging level for requests if we want to


##################################################################################################

import sys, time
try:
    import argparse
except ImportError:
    print("argparse is not standard in Python 2.6.  Use 2.7, or Try 'sudo pip install argparse'")
    raise


##########################################################################################################        

def main(argv):
    """The command-line interface"""
    try:                                
        description_text =  __doc__ # Reuse docstring at top of file
        
        parser = argparse.ArgumentParser(description=description_text,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
    except Exception as e:   
        print("argparse error: {exc}".format(exc=e))      
        #usage()                       
        parser.print_help()
        sys.exit(2)
    
    parser.add_argument("-u", "--url",
                        required=True,
                        help="Complete URL to AJA HELO device.  Example: http://192.168.0.3")

    args = parser.parse_args()

    device_url = args.url
        
    is_streaming = verify_streaming(device_url)
    maybe = {True:"", False:"NOT "} # a tiny dictionary
    print("HELO at {url} is {maybe}streaming.".format(url=args.url, maybe=maybe[is_streaming]))
        
    return
    
    
def verify_streaming(device_url):
    """Verify streaming activity.
    
       :param url: address of the HELO
       :return: True if device is actually Streaming; False if not.
       """
    streaming = True    # Return value; assume everything's gonna be OK.
    
    # If this function is called immediately after the Stream Command was given,
    # it may take a second for the Replicator to report active streaming. 
    time.sleep(2)   # Give replicator time to do its thing
    
    replicator_state_dict = None
    param_id = "eParamID_ReplicatorStreamState"
    state_url = "{url}/config?action=get&paramid={p}".format(url=device_url, p=param_id)
    response = requests.get(state_url)
    if (response.status_code == requests.codes.ok):   # Success (200)
        replicator_state_dict = response.json()
        logger.debug("replicator_state_dict = {d}".format(d=replicator_state_dict))
        
    if (replicator_state_dict):
        replicator_state = replicator_state_dict["value"]
        logger.debug("replicator_state = {s}".format(s=replicator_state))

        # We have the Replicator state.  Now compare it to possible valid values
        settings = getValidSettingsForParameter(device_url, param_id)
        # Sift through the settings to find the value/text pair for this replicator_state
        for value_text_pair in settings:
            (state_value, state_text) = value_text_pair  # Unpack 2-tuple
            #logger.debug("ReplicatorState {v} means {t}".format(v=state_value, t=state_text))
            if (int(state_value) == int(replicator_state)):
                logger.info('ReplicatorStreamState is "{s}."'.format(s=state_text))
                if ("Streaming" not in state_text):
                    # We could also look for (state_value != 2).  Same thing.
                    streaming = False

    return streaming

def getValidSettingsForParameter(device_url, param_id):
    """
    Returns a list of (value, description) pairs.
    ASSUMES that the Descriptor for this param has "param_type":"enum"!!!
    """
    settings = []
    # Get a dictionary representing the descriptor
    descriptor_dict = getDescriptor(device_url, param_id)
    
    if (descriptor_dict["param_type"] != "enum"):
        raise Exception('{p} is not an "enum" param'.format(p=param_id))
    enum_values = descriptor_dict["enum_values"]
    
    for value_dict in enum_values:
        settings.append((value_dict['value'],value_dict['text']))
    return settings

def getDescriptor(device_url, param_id):
    """
    Get everything the target device knows about this parameter (excluding current state).
    Returns a dictionary.
    """
    descriptor_url = '{url}/descriptors?paramid={p}'.format(url=device_url, p=param_id)
    response = requests.get(descriptor_url)
    if (response.status_code == requests.codes.ok):   # Success (200)
        descriptor_list = response.json()

    # The json will appear to be a python list containing one dictionary.
    descriptor_dict = descriptor_list[0] # This is the dictionary representing the descriptor.

    return descriptor_dict


if __name__ == '__main__':
    main(sys.argv[1:])
