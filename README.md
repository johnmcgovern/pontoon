# Pontoon

Scalable log replay with time travel and state tracking.


Features:

- Time Travel: Replays data in sequence based on the desired playout time (set in config.py).
- State Tracking: Saves state before script exit so by default a restart continues off at the same line.


Project Notes:

- This is not intended to be a data preparation framework. We use Splunk and the splunk-json-cleaner.py script for that piece.
- Append the following to the Splunk search containing the data you want to export: 
```
| sort 0 _time 
| eval time = _time 
| eval event = _raw 
| table time index host source sourcetype event
```
- This project expects the time, index, host, source, sourcetype, and event fields (not _time or _raw) to be present in each line of JSON. 
- Debug logging turns on per-line output. Use only with small datasets.
- This project has been tested, running locally on a Splunk server, to approximately 5,000+ events per second (EPS). Latency decreased aggregate throughput. 
- Other in-memory projects are orders of magnitude faster on the EPS. However, this project is built for large datasets / low resource consumption more than speed.
- HEC is used (JSON event endpoint) for data ingestion.
- Most safeties and exception handling in general are missing right now in the early stages.
