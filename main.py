#!/usr/bin/env python3

# Imports
import json
import linecache
import os
import requests
import time
import urllib3

from config import *


print("Data File Location: ", dataFilePath)
print("State File Location: ", stateFilePath)

# JSON object to hold all of the state information such as line number and time offset
# Gets written to disk at an interval
stateTracker = {"currentLine": 1, 
                "timeOffset": 0.0,
                "timeDelta": 0.0, 
                "speedUpOffset": 0 }

splunkAuthHeader = {'Authorization': 'Splunk {}'.format(splunkHecToken)}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Check if the state file exists and load if so
if os.path.exists(stateFilePath): 
    stateFile = open(stateFilePath, "r")
    stateTracker = json.loads(stateFile.read())
    stateFile.close()
    print("Loaded State File: ", stateTracker)

# If state file doesn't exit, write one
if not os.path.exists(stateFilePath):
    print("Creating New State File: ", stateFilePath)

    lineData = linecache.getline(dataFilePath, 1)
    currentLineJson = json.loads(lineData)
    firstEpochTime = currentLineJson["time"]
    print("State File - First Timestamp", firstEpochTime)

    lineData = linecache.getline(dataFilePath, 1)
    currentLineJson = json.loads(lineData)
    stateTracker['timeOffset'] = time.time() - float(currentLineJson['time'])
    print("State File - Current Timestamp:", time.time())
    print("State File - Calculated Offset: ", stateTracker['timeOffset'])

    file = open(stateFilePath, "w")
    json.dump(stateTracker, file)
    file.close()
    print("Created New State File", stateFilePath)


# Check for data file existence and length
if os.path.exists(dataFilePath):
    dataFile = open(dataFilePath, "r")
    for dataFileLength, line in enumerate(dataFile):
        pass
    dataFileLength += 1
    dataFile.close()
    print("Data File Length: ", dataFileLength)


# Main loop
try:
    #Open a persistent tcp session to Splunk HEC 
    session = requests.session()
    eventJsonStorage = ""
    print("Begin Main Loop")

    while 1==1:
        # Get one line at a time from the data file
        lineData = linecache.getline(dataFilePath, int(stateTracker['currentLine']))
        currentLineJson = json.loads(lineData)

        if stateTracker['currentLine'] % speedUpInterval == 0:
            stateTracker['speedUpOffset'] += speedUpFactor

        # If timeDelta is positive, we can output logs. 
        # If timeDelta is negative we sleep for a fraction of a second (sometime multiple times) to keep in sync with current time.
        stateTracker['timeDelta'] = (time.time() + float(stateTracker['speedUpOffset'])) - (float(currentLineJson['time']) + float(stateTracker['timeOffset']))

        if debug:
            print("Line", int(stateTracker['currentLine']), "Time Delta:", stateTracker['timeDelta'])

        # Send a log message to Splunk via HEC
        if stateTracker['timeDelta'] >= 0:
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
 
            # Default reporting (every 2000 events)
            if stateTracker['currentLine'] % stateTrackerReportingFactor == 0:
                print("State Tracker:", stateTracker)

            # Debug reporting (every event)
            if debug:
                print("Sent Line: ", stateTracker['currentLine'])

            # Updated state file every 100 events by default 
            # (happens automatically on KeyboardInterrupt as well)
            if stateTracker['currentLine'] % stateTrackerWriteToDiskFactor == 0:
                file = open(stateFilePath, "w")
                json.dump(stateTracker, file)
                file.close()

            # If we reach EoF and shouldLoop==True, then reset the stateTracker and start over.
            if int(stateTracker['currentLine']) == int(dataFileLength) and shouldLoop==True:
                print("Reached EoF - Starting Over ", stateTracker)
                r = session.post(splunkUrl, headers=splunkAuthHeader, data=eventJsonStorage, verify=False)
                eventJsonStorage = ""
                stateTracker['currentLine'] = 1
                lineData = linecache.getline(dataFilePath, int(stateTracker['currentLine']))
                currentLineJson = json.loads(lineData)
                stateTracker['timeOffset'] = time.time() - float(currentLineJson['time'])
                stateTracker['speedUpOffset'] = 0
                print("State Reset Completed", stateTracker)

            # If we reach EoF and shouldLoop==False, then delete the state file and exit.
            if int(stateTracker['currentLine']) == int(dataFileLength) and shouldLoop==False:
                r = session.post(splunkUrl, headers=splunkAuthHeader, data=eventJsonStorage, verify=False)
                eventJsonStorage = ""
                os.remove(stateFilePath)
                print("Reached EoF - Deleted State File")
                print("Reached EoF - Exiting")
                exit()    
        
            # Advance to the next line
            stateTracker['currentLine'] += 1

        else:
            # If we don't have any data available for the given second then sleep
            # and also fast forward by speedUpFactorWhileSleeping 
            # so we don't have to sleep to long
            time.sleep(.48)


# If we get interrupted at the keyboard (Ctrl^C)
except KeyboardInterrupt:
    # Dump current state
    file = open(stateFilePath, "w")
    json.dump(stateTracker, file)
    file.close()

    # Close our HEC session
    session.close()

    # Final logs
    print("Caught Keyboard Interrupt - Quitting")
    print("State Tracker:", stateTracker)
        