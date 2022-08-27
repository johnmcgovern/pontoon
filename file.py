#
# file.py - Filesystem type operations.
#

import json
import linecache
import time

from config import *
from const import *

def load_state_file():
    stateFile = open(stateFilePath, "r")
    stateTracker = json.loads(stateFile.read())
    stateFile.close()
    print("Loaded State File: ", stateTracker)

def create_state_file():
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

def get_data_file_length():
    dataFile = open(dataFilePath, "r")
    for dataFileLength, line in enumerate(dataFile):
        pass
    dataFileLength += 1
    dataFile.close()
    print("Data File Length:", dataFileLength)