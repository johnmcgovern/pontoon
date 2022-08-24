# Pontoon

Scalable log replay with time travel and time compression.

Features:

- Time Travel: Replays data within a relative second of when it was recorded in proper sequence.
- Time Compression: Speeds the replay up by a configurable amount.
- State Tracking: Saves state before script exit so by default a restart continues off at the same line location and catches up.

Project Notes:

- This is not intended to be a data preperation framework. We use Splunk and the splunk-json-cleaner.py script for that piece.
- Append the following to the Splunk search containing the data you want to export: 
```
| sort 0 _time 
| eval time = _time 
| eval event = _raw 
| table time index host source sourcetype event
```
- This project expects the _time, index, host, source, sourcetype, and event fields to be present in each line of JSON. 
- Currently we ignore the source index specification for convenience, but this may be togglable in the future.
- Debug logging turns on per-line output. Use only with small datasets.
- This project has been tested running locally on the Splunk system to approximately 200 events per second.
- Other in-memory projects are orders of magniture faster on the EPS. However, this project is built for large datasets more than speed.
- HEC is used (JSON endpoint) to data ingestion.
- Most safeties and exception handling in general are missing right now in the early stages.
