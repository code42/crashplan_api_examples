# By downloading and executing this software, you acknowledge and agree that Code42 is providing you this software at no cost separately from Code42's commercial offerings.
# This software is not provided under Code42's master services agreement.
# It is provided AS-IS, without support, and subject to the license below.
# Any support and documentation for this software are available at the Code42 community site.

# The MIT License (MIT)
# Copyright (c) 2019 Code42

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
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
print "totalDeviceData: ", '%f' % totalDeviceData, c42Lib.sizeof_fmt_si(totalDeviceData)
print "totalDestinationData: ", '%f' % totalDestinationData, c42Lib.sizeof_fmt_si(totalDestinationData)
print "total device to destination ratio %: ", finalRatio
