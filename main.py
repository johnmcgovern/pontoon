#!/usr/bin/env python3

# Imports
import json
import linecache
import os
import requests
import time
import urllib3


# Setup Variables
dataFilePath = "./data/botsv4.json"

splunkUrl = 'https://wf.splk.me:8088/services/collector/event'
splunkHecToken = "9802541d-394f-4053-b973-306757e15ed3"
splunkIndex = "test"   # Currently we always override the data files index specification (but this may change)
splunkAuthHeader = {'Authorization': 'Splunk {}'.format(splunkHecToken)}

speedUpFactor = 2
speedUpInterval = 2000

shouldLoop = False

debug = False

stateTracker = {"currentLine": 1, 
                "timeOffset": 0.0,
                "timeDelta": 0.0, 
                "speedUpOffset": 0 }
stateFilePath = "./var/pontoon.state"
stateTrackerReportingFactor = 2000
stateTrackerModFactor = 100


print("Data File Location: ", dataFilePath)
print("State File Location: ", stateFilePath)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Check if the state file exists and load if so
if os.path.exists(stateFilePath): 
    stateFile = open(stateFilePath, "r")
    stateTracker = json.loads(stateFile.read())
    print("Loaded State File: ", stateTracker)
    stateFile.close()

# If state file doesn't exit, write one
if not os.path.exists(stateFilePath):
    print("Creating State File: ", stateFilePath)

    lineData = linecache.getline(dataFilePath, 1)
    currentLineJson = json.loads(lineData)
    firstEpochTime = currentLineJson["time"]
    print("State File - First Timestamp", firstEpochTime)

    lineData = linecache.getline(dataFilePath, 1)
    currentLineJson = json.loads(lineData)
    stateTracker['timeOffset'] = time.time() - float(currentLineJson['time'])
    print("State File - Current Timestamp:", time.time())
    print("State File - Calculated Offset: ", stateTracker['timeOffset'])

    print("Writing State File: ", stateTracker)
    file = open(stateFilePath, "w")
    json.dump(stateTracker, file)
    file.close()
    print("Created State File", stateFilePath)


# Check for data file existence and length
if os.path.exists(dataFilePath):
    dataFile = open(dataFilePath, "r")
    for dataFileLength, line in enumerate(dataFile):
        pass
    dataFileLength += 1
    dataFile.close()
    print("Data File Length: ", dataFileLength)


# Main loop
print("Begin Main Loop")

try:
    while 1==1:
        # Get one line at a time from the data file
        lineData = linecache.getline(dataFilePath, int(stateTracker['currentLine']))
        currentLineJson = json.loads(lineData)

        if stateTracker['currentLine'] % speedUpInterval == 0:
            stateTracker['speedUpOffset'] += speedUpFactor

        stateTracker['timeDelta'] = (time.time() + float(stateTracker['speedUpOffset'])) - (float(currentLineJson['time']) + float(stateTracker['timeOffset']))

        if debug:
            print("Line", int(stateTracker['currentLine']), "Time Delta:", stateTracker['timeDelta'])

        if stateTracker['timeDelta'] >= 0:
            eventJson = {"time": time.time(), 
                        "index": splunkIndex, 
                        "host":currentLineJson['host'], 
                        "source":currentLineJson['source'], 
                        "sourcetype":currentLineJson['sourcetype'],  
                        "event": currentLineJson['event'] }
            r = requests.post(splunkUrl, headers=splunkAuthHeader, json=eventJson, verify=False)
            if debug:
                print("Sent Line: ", stateTracker['currentLine'])


            if stateTracker['currentLine'] % stateTrackerReportingFactor == 0:
                print("State Tracker:", stateTracker)

            if stateTracker['currentLine'] % stateTrackerModFactor == 0:
                file = open(stateFilePath, "w")
                json.dump(stateTracker, file)
                file.close()

            # If we reach EoF and shouldLoop==True, then reset the stateTracker and start over.
            if int(stateTracker['currentLine']) == int(dataFileLength) and shouldLoop==True:
                print("Reached EoF - Starting Over ", stateTracker)
                stateTracker['currentLine'] = 1
                lineData = linecache.getline(dataFilePath, int(stateTracker['currentLine']))
                currentLineJson = json.loads(lineData)
                stateTracker['timeOffset'] = time.time() - float(currentLineJson['time'])
                stateTracker['speedUpOffset'] = 0
                print("State Reset Completed", stateTracker)

            # If we reach EoF and shouldLoop==False, then delete the state file and exit.
            if int(stateTracker['currentLine']) == int(dataFileLength) and shouldLoop==False:
                print("Reached EoF - Deleting State File")
                os.remove(stateFilePath)
                print("Reached EoF - Quitting")
                exit()    
        

            stateTracker['currentLine'] += 1

        else:
            time.sleep(.25)

except KeyboardInterrupt:
    file = open(stateFilePath, "w")
    json.dump(stateTracker, file)
    file.close()

    print("Caught Keyboard Interrupt - Quitting")
    print("State Tracker:", stateTracker)
        