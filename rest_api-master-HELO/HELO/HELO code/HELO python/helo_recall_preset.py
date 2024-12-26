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

"""helo_recall_preset - Recall a Preset, and Verify that the Preset was recalled;
   use the python requests library."""

__author__ = "AJA Video Systems, Inc."
__version__ = "$Revision: 1.0 $"
__copyright__ = "Copyright (C) 2017 AJA Video Systems, Inc."
__license__ = "Apache 2.0"

##################################################################################################

import logging  # in order for basicConfig to work properly, logging must be imported before anything else!!!
logging.basicConfig(format='%(levelname)s::%(name)s::%(module)s::%(funcName)s::%(lineno)s::%(message)s',level=logging.INFO)
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
    parser.add_argument("-p", "--preset",
                        required=True,
                        help="Integer Preset # (1 through 20")

    args = parser.parse_args()

    device_url = args.url
    
    recall_successful = False
    recall_requested = recall_preset(device_url, args.preset)
    if (recall_requested):
        # Wait until the RegisterRecallResult param changes.
        wait_for_recall_completion(device_url)
    
        # Check the value of the RegisterRecallResult param 
        recall_successful = verify_recall(device_url)
    
    maybe = {True:"", False:"NOT "} # a tiny dictionary
    print("Recall of Preset {p} was {maybe}successful.".format(p=args.preset, maybe=maybe[recall_successful]))
        
    return
    
    
def recall_preset(device_url, preset_num):
    """Set the Recall Preset parameter. 

       :param device_url: complete URL string to address your HELO.  ('http://ip_address')
       :param preset_num: an integer, 1 through 20
       :return: True if Recall was successfuly requested; False otherwise
       """
    command_accepted = False # Assume nothing
    
    # start a stream
    param_id = "eParamID_RegisterRecall"
    stream_url = "{url}/config?action=set&paramid={p}&value={v}".format(url=device_url, p=param_id, v=preset_num)
                 
    response = requests.get(stream_url)
    if  (response.status_code == requests.codes.ok):
        print("Preset {p}  Recall requested.  (eParamID_RegisterRecall set to {p}.)".format(p=preset_num))
        command_accepted = True
    
    return command_accepted

def verify_recall(device_url):
    """Verify successful recall of preset.
    
       :param url: address of the HELO
       :return: True if Recall was successful; False if not.
       """
    recall_successful = True    # Return value; assume everything's gonna be OK.
    
    # If this function is called immediately after the Stream Command was given,
    # it may take a second for the Replicator to report active recall_successful. 
    time.sleep(2)   # Give replicator time to do its thing
    
    recall_result_dict = None
    param_id = "eParamID_RegisterRecallResult"
    result_url = "{url}/config?action=get&paramid={p}".format(url=device_url, p=param_id)
    response = requests.get(result_url)
    if (response.status_code == requests.codes.ok):   # Success (200)
        recall_result_dict = response.json()
        logger.debug("recall_result_dict = {r}".format(r=recall_result_dict))
        
    if (recall_result_dict):
        recall_result = recall_result_dict["value"]
        logger.debug("recall_result = {s}".format(s=recall_result))

        # We have the Replicator state.  Now compare it to possible valid values
        settings = getValidSettingsForParameter(device_url, param_id)
        # Sift through the settings to find the value/text pair for this replicator_state
        for value_text_pair in settings:
            (result_value, result_text) = value_text_pair  # Unpack 2-tuple
            #logger.debug("RegisterRecallResult {v} means {t}".format(v=result_value, t=result_text))
            if (int(result_value) == int(recall_result)):
                logger.info('RegisterRecallResult is "{s}."'.format(s=result_text))
                if ("Complete" not in result_text):
                    # We could also look for (result_value != 2).  Same thing.
                    recall_successful = False
                # TODO: If 'Recalling' in result_text, loop and try again.
    return recall_successful

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

#########################################################

def wait_for_recall_completion(device_url):
    """
        :param device_url:
        :return: True if the RegisterRecallResult param changed.
    """
    connection_id = connect(device_url)
    
    recall_complete = False
    timeout_expired = False
    start_time = time.time()
    timeout = 8 # 8 seconds
    deadline = start_time + timeout
    while ((not recall_complete) and (not timeout_expired)):
        events = wait_for_config_events(device_url, connection_id)
        logger.debug("events: {e}".format(e=events))
        
        for event in events:
            logger.debug("Got event for {e}".format(e=event['param_id']))
            if (event['param_id'] == 'eParamID_RegisterRecallResult'):
                recall_complete = True
                logger.info("The Result has arrived.")
        if (time.time() > deadline):
            timeout_expired = True
            logger.info("Timed out.  Didn't get Recall Result within {t} seconds.".format(t=timeout))

    return recall_complete
    
def wait_for_config_events(device_url, connectionid=None):
    """
    Monitor all parameter changes.
    
    :param device_url:
    :param connectionid: The ID that was returned from connect()
    :return: a list of events, in json format
             Note: each json-formatted 'event' is equivalent to a Python dictionary.
    """
    events = None
    response = requests.get("{u}/config?action=wait_for_config_events&connectionid={c}".format(u=device_url, c=connectionid), timeout=50)    # this works
    if (response.status_code == requests.codes.ok):
        events = response.json()  

    return events

def connect(device_url):
    """
    This is only used for listening for event streams.
    """
    connection_id = None
    response = requests.get("{u}/config?action=connect".format(u=device_url), timeout=5)
    if (response.status_code == requests.codes.ok) :
        result = response.json()
        # The json is also a python dictionary.
        connection_id = result.get('connectionid')
    return connection_id

if __name__ == '__main__':
    main(sys.argv[1:])
