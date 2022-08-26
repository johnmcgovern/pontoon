# Configuration Variables
fileKey = "botsv4"
dataFilePath = "./data/" + fileKey + ".json"
stateFilePath = "./var/" + fileKey + ".state"

splunkUrl = 'https://example.splk.me:8088/services/collector/event'
splunkHecToken = "9802541d-394f-4053-b973-306757e15ed3"
splunkIndex = "test"   # Currently we always override the data files index specification (but this may change)

shouldLoop = False
debug = False

speedUpFactor = 2
speedUpInterval = 2000

stateTrackerReportingFactor = 2000
stateTrackerWriteToDiskFactor = 1000

eventsPerHecBatch = 5