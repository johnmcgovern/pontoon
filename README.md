# Pontoon

Scalable log replay with time travel and time compression.

Features:

- Time Travel: Replays data within a relative second of when it was recorded in proper sequence.
- Time Compression: Speeds the replay up by a configurable amount.
- State Tracking: Saves state before script exit so by default a restart continues off at the same line location and catches up.

Modes:

- "realtime" time mode was implemented first to play out events more or less second by second with some acceleration. I.e we should see ups and down in EPS mirroring how the data was originally recorded.
- "linear" mode was built second and is a simpler mode. It takes the amount of time desired and plays out the same number of events each second to hit its time duration target.

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
- Currently, we ignore the source index specification for convenience, but this may be togglable in the future.
- Debug logging turns on per-line output. Use only with small datasets.
- This project has been tested, running locally on a Splunk server, to approximately 5,000+ events per second (EPS). Latency decreased aggregate throughput. 
- Other in-memory projects are orders of magnitude faster on the EPS. However, this project is built for large datasets / low resource consumption more than speed.
- HEC is used (JSON event endpoint) for data ingestion.
- Most safeties and exception handling in general are missing right now in the early stages.
