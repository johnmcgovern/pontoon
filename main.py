#!/usr/bin/env python3

#
# main.py - Main execution logic.
#

import json
import os
import requests
import sys
import time

from config import *
from const import *
from file import *


print()

# Optionally, take in the file key from arguments
try:
    file_key = sys.argv[1]
    print("File key supplied as an argument:", sys.argv[1])
except: 
    print("No file key specified, exiting.")
    exit()

data_file_path = "./data/" + file_key + ".json"
state_file_path = "./var/" + file_key + ".state"

print("Data File Location: ", data_file_path)
print("State File Location: ", state_file_path, "\n")


# Optionally, take in the index from arguments
try:
    splunk_index = sys.argv[2]
    print("Index supplied as an argument:", sys.argv[2])
except: 
    print("No index specified, defaulting to config.")
    pass

print("Sending to Index:", splunk_index, "\n")


# If the state file exists and load it so we maintain state
if os.path.exists(state_file_path): 
    state_tracker = load_state_file(state_file_path)

# If state file doesn't exit, create one
if not os.path.exists(state_file_path):
    state_tracker = create_state_file(state_file_path)

# Check for data file existence and length
if os.path.exists(data_file_path):
   data_file_length = get_data_file_length(data_file_path)


# Main loop
try:

    #Open a persistent tcp session to Splunk HEC 
    session = requests.session()
    print("\nBegin Main Loop")
    print("Starting at Line:", state_tracker['current_line'])


    state_tracker['time_window'] = time_playout_seconds

    state_tracker['eps'] = round(data_file_length / time_playout_seconds, 0)
    if state_tracker['eps'] < 1:
        state_tracker['eps'] = 1
    print("Events Per Second:", state_tracker['eps'], "\n")

    timer_start = time.time()


    # Per line loop
    while 1==1:
        
        # Get one line at a time from the data file
        current_line_json = get_line(data_file_path, int(state_tracker['current_line']))

        eventJson = {"time": time.time(), 
                        "index": splunk_index, 
                        "host":current_line_json['host'], 
                        "source":current_line_json['source'], 
                        "sourcetype":current_line_json['sourcetype'],  
                        "event": current_line_json['event'] }

        # Group events together for sending as a batch
        event_json_storage += json.dumps(eventJson) + "\r\n"                            

        # Mod the current_line to send as a batch per the eps variable
        if state_tracker['current_line'] % state_tracker['eps'] == 0:                        
            
            # Write batch to HEC
            r = session.post(splunk_url + splunk_hec_event_endpoint, headers=splunk_auth_header, data=event_json_storage, verify=False)
            event_json_storage = ""

            # If the last batch completed in < 1 second (typically does), 
            # then sleep for the remainder of the second.
            timer_end = time.time()
            timer_duration = timer_end - timer_start
            if 1 - timer_duration > 0:
                time.sleep(1 - timer_duration)
            timer_start = time.time()

            # Per batch debug level logging
            if debug:
                print("-> Sent up to Line:", state_tracker['current_line'], "  Sleeping:", 1 - timer_duration)

        # Default reporting (every 2000 events)
        if state_tracker['current_line'] % state_tracker_reporting_factor == 0:
            print("State Tracker:", state_tracker)  

        # Advance to the next line
        state_tracker['current_line'] += 1 
        

        # If we reach EoF and should_loop==True, then reset the state_tracker and start over.
        if int(state_tracker['current_line']) == int(data_file_length) and should_loop==True:
            
            print("Reached EoF - Starting Over ", state_tracker)
            
            # Write batch to HEC
            r = session.post(splunk_url + splunk_hec_event_endpoint, headers=splunk_auth_header, data=event_json_storage, verify=False)
            
            event_json_storage = ""
            state_tracker['current_line'] = 1
            
            print("State Reset Completed", state_tracker)

        # If we reach EoF and should_loop==False, then delete the state file and exit.
        if int(state_tracker['current_line']) == int(data_file_length) and should_loop==False:
            
            # Write batch to HEC
            r = session.post(splunk_url + splunk_hec_event_endpoint, headers=splunk_auth_header, data=event_json_storage, verify=False)
            
            event_json_storage = ""
            delete_state_file(state_file_path)
            
            print("Reached EoF - Exiting")
            exit()


# If we get interrupted at the keyboard (Ctrl^C)
except KeyboardInterrupt:
    # Dump current state
    write_state_to_disk(state_file_path, state_tracker)

    # Close our HEC session
    session.close()

    # Final logs
    print("Caught Keyboard Interrupt - Quitting")
    print("State Tracker Written to Disk:", state_tracker)
        