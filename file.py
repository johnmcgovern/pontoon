#
# file.py - Filesystem type operations.
#

import json
import linecache
import os
import time

from config import *
from const import *


def load_state_file():
    stateFile = open(stateFilePath, "r")
    stateTracker = json.loads(stateFile.read())
    stateFile.close()
    print("Loaded State File: ", stateTracker)
    return stateTracker

def create_state_file():

    # Instantiate a stateTracker JSON object
    stateTracker = {"currentLine": 1, 
                    "timeOffset": 0.0,
                    "timeDelta": 0.0, 
                    "speedUpOffset": 0 }

    print("Creating New State File: ", stateFilePath)

    # Open the first line of the data file
    currentLineJson = load_line(1)
    
    # Calculate the difference between current time and the first line epoch time
    stateTracker['timeOffset'] = time.time() - float(currentLineJson['time'])

    print("State File - First Timestamp", currentLineJson["time"])
    print("State File - Current Timestamp:", time.time())
    print("State File - Calculated Offset: ", stateTracker['timeOffset'])

    # Write the new state file to disk (with currentLine=1 and calculated timeOffset)
    write_state_to_disk(stateTracker)
    print("Created New State File", stateFilePath)

    return stateTracker    


def get_data_file_length():
    dataFile = open(dataFilePath, "r")
    for dataFileLength, line in enumerate(dataFile):
        pass
    dataFileLength += 1
    dataFile.close()
    print("Data File Length:", dataFileLength)
    return dataFileLength


def load_line(lineNumber):
    lineData = linecache.getline(dataFilePath, lineNumber)
    return json.loads(lineData)


def write_state_to_disk(stateTracker):
    file = open(stateFilePath, "w")
    json.dump(stateTracker, file)
    file.close()       

def delete_state_file():
    os.remove(stateFilePath)
    print("Deleted State File")