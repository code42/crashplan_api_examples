#
# File: deviceStats.py
# Author: AJ LaVenture, Code 42 Software
# Last Modified: 10-21-2014
#
# Calculate total processed data by clients and compare to total storage numbers 
#
# Assumptions:
# all devices are pulling just the first destination
# storedBytesHistory is all desitnations
# therefore numbers assumed all devices only have 1 destination, therefore sum of devices bytes will be
# represented - percentage will drop due to increased versions and deleted files

# api/computer/xxxx?incBackupUsage=true
# data.backupUsage[0].selectedBytes 
# data.backupUsage[0].percentComplete

# api/storedBytesHistory


from c42SharedLibrary import c42Lib
import logging
import getpass
import json

c42Lib.cp_host = "http://aj-ubuntu"
c42Lib.cp_port = "4280"

c42Lib.cp_username = "admin"
c42Lib.cp_password = getpass.getpass()
c42Lib.cp_logLevel = "INFO"
c42Lib.cp_logFileName = "deviceStats.log"
c42Lib.setLoggingLevel()


def getStoredBytesHistory():
	params = {}
	payload = {}

	r = c42Lib.executeRequest("get", "/api/storedBytesHistory", params, payload)

	content = r.content
	binary = json.loads(content)

	latestStoredNumber = binary['data'][0][1]['archiveBytes']

	return latestStoredNumber



devices = c42Lib.getAllDevices()

totalDestinationData = getStoredBytesHistory()

totalDeviceData = 0

for index, device in enumerate(devices):
	cur_selectedBytes = 0
	cur_percentComplete = 0

	if device['backupUsage']:
		cur_selectedBytes = device['backupUsage'][0]['selectedBytes']
		# print str(cur_selectedBytes)
		cur_percentComplete = int(device['backupUsage'][0]['percentComplete'])
		# print str(cur_percentComplete)

	totalDeviceData = totalDeviceData + (cur_selectedBytes * (float(cur_percentComplete) / 100))

finalRatio = (1 - (float(totalDestinationData)/totalDeviceData)) * 100
print "totalDeviceData: ", c42Lib.sizeof_fmt_si(totalDeviceData)
print "totalDestinationData: ", c42Lib.sizeof_fmt_si(totalDestinationData)
print "total Compressions and dedup %: ", finalRatio
