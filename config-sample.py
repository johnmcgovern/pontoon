#
# config.py - User modifiable variables.
#


# Splunk URL, HEC Token, and Index to use.
# splunk_index can be passed as the second command line argument (i.e. main.py indexname)
splunk_url = "https://example.splk.me:8088/"
splunk_hec_token = "9802541d-394f-4053-b973-306757e15ed3"
splunk_index = "test"


# Playout settings
time_playout_seconds = 43200  # default 12 hours

# Should the script restart at EoF
should_loop = False

# Per event logging
debug = False

# How often to log progress
state_tracker_reporting_factor = 2000
