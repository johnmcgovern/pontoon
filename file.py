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
    state_file = open(state_file_path, "r")
    state_tracker = json.loads(state_file.read())
    state_file.close()
    print("Loaded State File: ", state_tracker)
    return state_tracker

def create_state_file(state_file_path):
    # Instantiate a default state_tracker JSON object
    state_tracker = {
        "current_line": 1, 
        "time_offset": 0.0,
        "time_delta": 0.0, 
        "speed_up_offset": 0,
        "eps": 0 
        }

    print("Creating New State File: ", state_file_path)

    # Open the first line of the data file
    current_line_json = get_line(1)
    
    # Calculate the difference between current time and the first line epoch time
    state_tracker['time_offset'] = time.time() - float(current_line_json['time'])

    if time_mode == "linear":
        print("State File - First Timestamp", current_line_json["time"])
        print("State File - Current Timestamp:", time.time())
        print("State File - Calculated Offset: ", state_tracker['time_offset'])

    # Write the new state file to disk (with current_line=1 and calculated time_offset)
    write_state_to_disk(state_tracker)
    print("Created New State File", state_file_path)

    return state_tracker    


def get_data_file_length():
    data_file = open(data_file_path, "r")
    for data_file_length, line in enumerate(data_file):
        pass
    data_file_length += 1
    data_file.close()
    print("Data File Length:", data_file_length)
    return data_file_length


def get_line(line_number):
    lineData = linecache.getline(data_file_path, line_number)
    return json.loads(lineData)


def write_state_to_disk(state_tracker):
    file = open(state_file_path, "w")
    json.dump(state_tracker, file)
    file.close()       

def delete_state_file():
    os.remove(state_file_path)
    print("Deleted State File")