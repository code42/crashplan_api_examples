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
# File: allDeviceReport.py
# Author: P. Hirst & AJ LaVenture, Code 42 Software
# Last Modified: 01-24-2014
#
# get report data on all users and devices
# need to set the "destId" to ensure 
# 
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

c42Lib.cp_host = "https://aj-ubuntu"
c42Lib.cp_port = "4285"
c42Lib.cp_username = "admin"
c42Lib.cp_password = getpass.getpass('Enter your CrashPlan console password: ')

# Set id of primary destination to get information and stats about
destId = 15

c42Lib.cp_logLevel = "DEGUG"
c42Lib.cp_logFileName = "allDeviceReport.log"
c42Lib.setLoggingLevel()


# c42Lib.MAX_PAGE_NUM = 5

# cp_api_storedBytesHistory = "/api/storedBytesHistory"


emptyBlock = ""

csvDeviceHeader = ['userId', 'username', 'computerId','computerName','computerType','osName','computerStatus','storePointId','storePointName','serverId','serverName',
	'selectedFiles','selectedBytes','selectedBytesHR','archiveBytes','archiveBytesHR','percentComplete','lastCompletedBackup',
'CompArchive-oldestDate','CompArchive-oldestDateBytes','oldestHR','CompArchive-newestDate','CompArchive-newestDateBytes','newsetHR','CompArchive-Delta','deltaHR']
printValues = []
printRow = []

def findRecord(key,records):
    for r in records:
        if r['userId'] == key: 
            return r


def getDeviceReport():
	csvDeviceFile = csv.writer(open("allDeviceReport.csv", "wb+"))
	csvDeviceFile.writerow(csvDeviceHeader)

	users = c42Lib.getAllUsers()
	# get all the users to have in memory

	devices = c42Lib.getAllDevices()
	# devices = c42Lib.getDevices(1)

	for index, device in enumerate(devices):
		# device = c42Lib.getDeviceById(8637)
		printValues = []
		
		# computerId = loopDevice['computerId']

		# device = c42Lib.getDeviceById(computerId)

		userId = device['userId']
		printValues.extend([str(userId)])

		# Lookup User Info
		userInfo = findRecord(userId,users)

		logging.debug(userInfo)

		#Get User Name
		if userInfo:
			userName = userInfo['username']
		else:
			username = 'null'
		printValues.extend([userName.encode('utf-8')])
		
		# print deviceObject
		computerId = device['computerId']
		printValues.extend([str(computerId)])

		computerName = device['name']
		printValues.extend([computerName.encode('utf-8')])

		computerType = device['type']
		printValues.extend([computerType.encode('utf-8')])

		osName = device['osName']
		printValues.extend([osName.encode('utf-8')])

		computerStatus = device['status']
		printValues.extend([computerStatus.encode('utf-8')])


		if 'backupUsage' in device:

			deviceObjectBackupUsage = device['backupUsage']

			for backupUsage in deviceObjectBackupUsage:

				if backupUsage['targetComputerId'] == destId:

					storePointId = backupUsage['storePointId']
					printValues.extend([str(storePointId)])

					storePointName = backupUsage['storePointName']
					printValues.extend([storePointName.encode('utf-8')])

					serverId = backupUsage['serverId']
					printValues.extend([str(serverId)])

					serverName = backupUsage['serverName']
					printValues.extend([serverName.encode('utf-8')])

					selectedFiles = backupUsage['selectedFiles']
					printValues.extend([str(selectedFiles)])

					selectedBytes = backupUsage['selectedBytes']
					printValues.extend([str(selectedBytes)])

					printValues.extend([c42Lib.sizeof_fmt(selectedBytes)])

					archiveBytes = backupUsage['archiveBytes']
					printValues.extend([str(archiveBytes)])

					printValues.extend([c42Lib.sizeof_fmt(archiveBytes)])

					percentComplete = backupUsage['percentComplete']
					printValues.extend([str(percentComplete)])

					lastCompletedBackup = backupUsage['lastCompletedBackup']
					printValues.extend([str(lastCompletedBackup)])


					if 'history' in backupUsage:
						
						backupHistory = backupUsage['history']

						if backupHistory:

							oldestDate = 9999999999999999999
							# "20130801": 1909986568291,
							oldestDateBytes = 0
							newestDate = 0
						    # "20130830": 1932985363857
							newestDateBytes = 0

							for singleHistory in backupHistory:
								# print key, value
								# print oldestDate, int(key)
								currDate = singleHistory['date'].replace('-','')

								currarchiveBytes = singleHistory['archiveBytes']

								if (oldestDate > int(currDate)):
									oldestDate = int(currDate)
									oldestDateBytes = currarchiveBytes
								
								# print newestDate, int(key)
								if (newestDate <= int(currDate)):
									newestDate = int(currDate)
									newestDateBytes = currarchiveBytes

							printValues.extend([str(oldestDate)])
							printValues.extend([str(oldestDateBytes)])
							printValues.extend([c42Lib.sizeof_fmt(oldestDateBytes)])

							printValues.extend([str(newestDate)])
							printValues.extend([str(newestDateBytes)])
							printValues.extend([c42Lib.sizeof_fmt(newestDateBytes)])

							pArchiveBytesDeltaMonth = newestDateBytes - oldestDateBytes
							printValues.extend([str(pArchiveBytesDeltaMonth)])
							printValues.extend([c42Lib.sizeof_fmt(pArchiveBytesDeltaMonth)])
						# else:
							# printDeviceEmptyBlock(8)
					# else:
						# printDeviceEmptyBlock(8)
				# else:
				# 	print("hi")
					# printDeviceEmptyBlock(19)

		# else:
			# print("bye")
			# printDeviceEmptyBlock(19)
	
		# print ', '.join(printValues)
		logging.info(str(printValues))
		csvDeviceFile.writerow(printValues)



def printDeviceEmptyBlock(max):
	for x in range(int(max)):
		printValues.extend([emptyBlock])



getDeviceReport()
# print str(c42Lib.getDevicesPageCount())
















