#
# cleaner.py - Functions to clean/reconstruct/modify event lines.
#

# Event JSON structure for reference:
#
# event = cleaner({"time": time.time(), 
#                 "index": splunk_index, 
#                 "host":current_line_json['host'], 
#                 "source":current_line_json['source'], 
#                 "sourcetype":current_line_json['sourcetype'],  
#                 "event": current_line_json['event'] })


# Function intended to encapsulate all data clean up checks
# and remove this specialized / use cases specific code
# from the main logical flow.
def cleaner(event):
    if event['host'] == "" and "pan:" in event['sourcetype']:
        event['host'] = "pan-fw-1"

    return event