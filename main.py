#!/usr/bin/env python3

#
# main.py - Main execution logic.
#

import json
import os
import requests
import time

from config import *
from const import *
from file import *


print("Data File Location: ", data_file_path)
print("State File Location: ", state_file_path)


# If the state file exists and load it so we maintain state
if os.path.exists(state_file_path): 
    state_tracker = load_state_file()

# If state file doesn't exit, create one
if not os.path.exists(state_file_path):
    state_tracker = create_state_file()

# Check for data file existence and length
if os.path.exists(data_file_path):
   data_file_length = get_data_file_length()


# Main loop
try:
    #Open a persistent tcp session to Splunk HEC 
    session = requests.session()
    print("Begin Main Loop")
    print("Event Batch Size:", events_per_hec_batch)
    print("Starting at Line:", state_tracker['current_line'])
    print("Indexed to:", splunk_index)

    while 1==1:
        # Get one line at a time from the data file
        current_line_json = get_line(int(state_tracker['current_line']))

        if state_tracker['current_line'] % speed_up_interval == 0:
            state_tracker['speed_up_offset'] += speed_up_factor

        # If time_delta is positive, we can output logs. 
        # If time_delta is negative we sleep for a fraction of a second (sometime multiple times) to keep in sync with current time.
        state_tracker['time_delta'] = (time.time() + float(state_tracker['speed_up_offset'])) - (float(current_line_json['time']) + float(state_tracker['time_offset']))

        if debug:
            print("State Tracker:", state_tracker)

        # Send a log message to Splunk via HEC
        if state_tracker['time_delta'] >= 0:
            sleep_counter = 0
            eventJson = {"time": time.time(), 
                        "index": splunk_index, 
                        "host":current_line_json['host'], 
                        "source":current_line_json['source'], 
                        "sourcetype":current_line_json['sourcetype'],  
                        "event": current_line_json['event'] }

            # Group events together for sending as a batch
            event_json_storage += json.dumps(eventJson) + "\r\n"

            # Mod the current_line to send as a batch per the eventsPerHecBatch factor
            if state_tracker['current_line'] % events_per_hec_batch == 0:                        
                r = session.post(splunk_url + splunk_hec_event_endpoint, headers=splunk_auth_header, data=event_json_storage, verify=False)
                event_json_storage = ""

                # Debug reporting (every event)
                if debug:
                    print("-> Sent up to Line: ", state_tracker['current_line'])
 
            # Default reporting (every 2000 events)
            if state_tracker['current_line'] % state_tracker_reporting_factor == 0:
                print("State Tracker:", state_tracker)

            # Updated state file every state_trackerWriteToDiskFactor events
            # (happens automatically on KeyboardInterrupt as well)
            if state_tracker['current_line'] % state_tracker_write_to_disk_factor == 0:
                write_state_to_disk(state_tracker)

            # If we reach EoF and should_loop==True, then reset the state_tracker and start over.
            if int(state_tracker['current_line']) == int(data_file_length) and should_loop==True:
                print("Reached EoF - Starting Over ", state_tracker)
                
                r = session.post(splunk_url + splunk_hec_event_endpoint, headers=splunk_auth_header, data=event_json_storage, verify=False)
                event_json_storage = ""
                
                state_tracker['current_line'] = 1
                current_line_json = get_line(int(state_tracker['current_line']))
                
                state_tracker['time_offset'] = time.time() - float(current_line_json['time'])
                state_tracker['speed_up_offset'] = 0
                
                print("State Reset Completed", state_tracker)

            # If we reach EoF and should_loop==False, then delete the state file and exit.
            if int(state_tracker['current_line']) == int(data_file_length) and should_loop==False:
                r = session.post(splunk_url + splunk_hec_event_endpoint, headers=splunk_auth_header, data=event_json_storage, verify=False)
                event_json_storage = ""
                delete_state_file()
                print("Reached EoF - Exiting")
                exit()    
        
            # Advance to the next line
            state_tracker['current_line'] += 1

        else:
            # If we don't have any data available for the given second then sleep.
            # Fast forward number of times slept (sleep_counter) to the power of itself
            # so we don't have to sleep too long.
            sleep_counter += 1
            state_tracker['speed_up_offset'] += (sleep_counter ** 2)
            time.sleep(.98)


# If we get interrupted at the keyboard (Ctrl^C)
except KeyboardInterrupt:
    # Dump current state
    write_state_to_disk(state_tracker)

    # Close our HEC session
    session.close()

    # Final logs
    print("Caught Keyboard Interrupt - Quitting")
    print("State Tracker:", state_tracker)
        