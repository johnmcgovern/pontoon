#
# file.py - Filesystem type operations.
#

import json
import linecache
import os

from config import *
from const import *


def load_state_file(state_file_path):
    state_file = open(state_file_path, "r")
    state_tracker = json.loads(state_file.read())
    state_file.close()
    print("Loaded State File: ", state_tracker)
    return state_tracker

def create_state_file(state_file_path):
    # Instantiate a default state_tracker JSON object
    state_tracker = {
        "current_line": 1, 
        "eps": 0, 
        "time_window": 0.0,
        }

    print("Creating New State File: ", state_file_path)

    # Write the new state file to disk (with current_line=1 and calculated time_offset)
    write_state_to_disk(state_file_path, state_tracker)
    print("Created New State File", state_file_path)

    return state_tracker    


def get_data_file_length(data_file_path):
    data_file = open(data_file_path, "r")
    for data_file_length, line in enumerate(data_file):
        pass
    data_file_length += 1
    data_file.close()
    print("Data File Length:", data_file_length)
    return data_file_length


def get_line(data_file_path, line_number):
    lineData = linecache.getline(data_file_path, line_number)
    return json.loads(lineData)


def write_state_to_disk(state_file_path, state_tracker):
    file = open(state_file_path, "w")
    json.dump(state_tracker, file)
    file.close()       

def delete_state_file(state_file_path):
    os.remove(state_file_path)
    print("Deleted State File")