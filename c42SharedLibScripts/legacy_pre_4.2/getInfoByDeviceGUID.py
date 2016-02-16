# Copyright (c) 2016 Code42, Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.
#
# File: getInfoByDeviceGUID.py
# Author: AJ LaVenture, Code 42 Software
# Last Modified: 08-23-2013
#
# From a list of Device GUIDS, pull device and user information into CSV Format
# 

from c42SharedLibrary import c42Lib
import math
import sys
import json
import csv
import base64
import logging
import requests
import math
from dateutil.relativedelta import *
import datetime
import calendar
import getpass


#Test values
c42Lib.cp_host = "http://aj-proappliance"
c42Lib.cp_port = "4280"
c42Lib.cp_username = "admin"
c42Lib.cp_password = getpass.getpass('Enter your CrashPlan console password: ') # You will be prompted for your password


c42Lib.cp_logLevel = "INFO"
c42Lib.cp_logFileName = "getInfoByDeviceGUID.log"
c42Lib.setLoggingLevel()


AJ_TEST_DEVICE_GUID_LIST = [597897713966645505,597724554922036354,597893957280654977,597153934331668098]
# AJ_TEST_DEVICE_GUID_LIST = [597897713966645505]
# AJ_TEST_DEVICE_GUID_LIST = [597724554922036354]
# AJ_TEST_DEVICE_GUID_LIST = [597893957280654977]
# AJ_TEST_DEVICE_GUID_LIST = [597153934331668098]


GUID_LIST = AJ_TEST_DEVICE_GUID_LIST


csvFile = csv.writer(open("deviceReport.csv", "wb+"))
csvHeaders = ['guid','deviceName','osName','lastCompletedBackup','percentComplete','archiveBytes','selectedBytes','userId','userName','email',
			'firstName','lastName']

csvFile.writerow(csvHeaders)
print csvHeaders

for index, guid in enumerate(GUID_LIST):
	printValues = []
	printValues.extend([str(guid)])

	deviceList = c42Lib.getDeviceByGuid(guid)
	deviceObject = deviceList['computers']
	# print deviceObject
	
	deviceName = deviceObject[0]['name']
	printValues.extend([deviceName.encode('utf-8')])

	deviceOsName = deviceObject[0]['osName']
	printValues.extend([deviceOsName.encode('utf-8')])

	if deviceObject[0]['backupUsage']:

		deviceObjectBackupUsage = deviceObject[0]['backupUsage']

		lastCompletedBackup = deviceObjectBackupUsage[0]['lastCompletedBackup']
		# print str(lastCompletedBackup)
		printValues.extend([str(lastCompletedBackup)])

		percentComplete = deviceObjectBackupUsage[0]['percentComplete']
		printValues.extend([str(percentComplete)])

		archiveBytes = deviceObjectBackupUsage[0]['archiveBytes']
		printValues.extend([str(archiveBytes)])

		selectedBytes = deviceObjectBackupUsage[0]['selectedBytes']
		printValues.extend([str(selectedBytes)])

	else:
		emptyBlock = ""
		printValues.extend([emptyBlock])
		printValues.extend([emptyBlock])
		printValues.extend([emptyBlock])
		printValues.extend([emptyBlock])

	userId = deviceObject[0]['userId']
	printValues.extend([str(userId)])

	userList = c42Lib.getUserById(userId)
	# userObject = userList['users']

	username = userList['username']
	printValues.extend([username.encode('utf-8')])

	email = userList['email']
	printValues.extend([email.encode('utf-8')])

	firstName = userList['firstName']
	printValues.extend([firstName.encode('utf-8')])

	lastName = userList['lastName']
	printValues.extend([lastName.encode('utf-8')])
	
	logging.info(printValues)
	csvFile.writerow(printValues)
	print printValues




# script request for fahad:

# list of device guids


# lastCompletedBackup
# percentComplete
# archiveBytes (bytes already backed up)
# selectedBytes

# userId


# get user id and this info
# username
# email
# firstName
# lastName



# list object = 

# add csv
