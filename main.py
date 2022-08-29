#!/usr/bin/env python3

# Imports
import json
import os
import requests
import time

from config import *
from const import *
from file import *


print("Data File Location: ", dataFilePath)
print("State File Location: ", stateFilePath)


# If the state file exists and load it so we maintain state
if os.path.exists(stateFilePath): 
    stateTracker = load_state_file()

# If state file doesn't exit, create one
if not os.path.exists(stateFilePath):
    stateTracker = create_state_file()

# Check for data file existence and length
if os.path.exists(dataFilePath):
   dataFileLength = get_data_file_length()


# Main loop
try:
    #Open a persistent tcp session to Splunk HEC 
    session = requests.session()
    print("Begin Main Loop")
    print("Event Batch Size:", eventsPerHecBatch)
    print("Starting at Line:", stateTracker['currentLine'])
    print("Indexed to:", splunkIndex)

    while 1==1:
        # Get one line at a time from the data file
        currentLineJson = get_line(int(stateTracker['currentLine']))

        if stateTracker['currentLine'] % speedUpInterval == 0:
            stateTracker['speedUpOffset'] += speedUpFactor

        # If timeDelta is positive, we can output logs. 
        # If timeDelta is negative we sleep for a fraction of a second (sometime multiple times) to keep in sync with current time.
        stateTracker['timeDelta'] = (time.time() + float(stateTracker['speedUpOffset'])) - (float(currentLineJson['time']) + float(stateTracker['timeOffset']))

        if debug:
            print("State Tracker:", stateTracker)

        # Send a log message to Splunk via HEC
        if stateTracker['timeDelta'] >= 0:
            sleepCounter = 0
            eventJson = {"time": time.time(), 
                        "index": splunkIndex, 
                        "host":currentLineJson['host'], 
                        "source":currentLineJson['source'], 
                        "sourcetype":currentLineJson['sourcetype'],  
                        "event": currentLineJson['event'] }

            # Group events together for sending as a batch
            eventJsonStorage += json.dumps(eventJson) + "\r\n"

            # Mod the currentLine to send as a batch per the eventsPerHecBatch factor
            if stateTracker['currentLine'] % eventsPerHecBatch == 0:                        
                r = session.post(splunkUrl, headers=splunkAuthHeader, data=eventJsonStorage, verify=False)
                eventJsonStorage = ""

                # Debug reporting (every event)
                if debug:
                    print("-> Sent up to Line: ", stateTracker['currentLine'])
 
            # Default reporting (every 2000 events)
            if stateTracker['currentLine'] % stateTrackerReportingFactor == 0:
                print("State Tracker:", stateTracker)

            # Updated state file every stateTrackerWriteToDiskFactor events
            # (happens automatically on KeyboardInterrupt as well)
            if stateTracker['currentLine'] % stateTrackerWriteToDiskFactor == 0:
                write_state_to_disk(stateTracker)

            # If we reach EoF and shouldLoop==True, then reset the stateTracker and start over.
            if int(stateTracker['currentLine']) == int(dataFileLength) and shouldLoop==True:
                print("Reached EoF - Starting Over ", stateTracker)
                
                r = session.post(splunkUrl, headers=splunkAuthHeader, data=eventJsonStorage, verify=False)
                eventJsonStorage = ""
                
                stateTracker['currentLine'] = 1
                currentLineJson = get_line(int(stateTracker['currentLine']))
                
                stateTracker['timeOffset'] = time.time() - float(currentLineJson['time'])
                stateTracker['speedUpOffset'] = 0
                
                print("State Reset Completed", stateTracker)

            # If we reach EoF and shouldLoop==False, then delete the state file and exit.
            if int(stateTracker['currentLine']) == int(dataFileLength) and shouldLoop==False:
                r = session.post(splunkUrl, headers=splunkAuthHeader, data=eventJsonStorage, verify=False)
                eventJsonStorage = ""
                delete_state_file()
                print("Reached EoF - Exiting")
                exit()    
        
            # Advance to the next line
            stateTracker['currentLine'] += 1

        else:
            # If we don't have any data available for the given second then sleep.
            # Fast forward number of times slept (sleepCounter) to the power of itself
            # so we don't have to sleep too long.
            sleepCounter += 1
            stateTracker['speedUpOffset'] += (sleepCounter ** 2)
            time.sleep(.98)


# If we get interrupted at the keyboard (Ctrl^C)
except KeyboardInterrupt:
    # Dump current state
    write_state_to_disk(stateTracker)

    # Close our HEC session
    session.close()

    # Final logs
    print("Caught Keyboard Interrupt - Quitting")
    print("State Tracker:", stateTracker)
        