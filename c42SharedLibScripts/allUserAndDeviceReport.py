#
# File: allUserAndDeviceReport.py
# Author: AJ LaVenture, Code 42 Software
# Last Modified: 09-04-2013
#
# Specify source and destination organizaions and move all users
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


c42Lib.cp_host = "http://aj-proappliance"
c42Lib.cp_port = "4280"
c42Lib.cp_username = "admin"
c42Lib.cp_password = "admin"

c42Lib.cp_logLevel = "INFO"
c42Lib.cp_logFileName = "allUserAndDeviceReport.log"
c42Lib.setLoggingLevel()

# c42Lib.MAX_PAGE_NUM = 5

# cp_api_storedBytesHistory = "/api/storedBytesHistory"



csvUserHeaders = ['userId','username','email','orgId','orgName','computerCount','UserArchive-oldestDate','UserArchive-oldestDateBytes','oldestHR','UserArchive-newestDate','UserArchive-newestDateBytes','newestHR','UserArchiveBytesDeltaMonth','deltaHR']

emptyBlock = ""

csvDeviceHeader = ['userId','computerId','computerName','computerType','osName','computerStatus','storePointId','storePointName','serverId','serverName',
	'selectedFiles','selectedBytes','selectedBytesHR','archiveBytes','archiveBytesHR','percentComplete','lastCompletedBackup',
'CompArchive-oldestDate','CompArchive-oldestDateBytes','oldestHR','CompArchive-newestDate','CompArchive-newestDateBytes','newsetHR','CompArchive-Delta','deltaHR']
printValues = []
printRow = []


def getDeviceReport():
	csvDeviceFile = csv.writer(open("allDeviceReport.csv", "wb+"))
	csvDeviceFile.writerow(csvDeviceHeader)

	devices = c42Lib.getAllDevices()
	# devices = c42Lib.getDevices(1)

	for index, device in enumerate(devices):
		# device = c42Lib.getDeviceById(8637)
		printValues = []
		
		# computerId = loopDevice['computerId']

		# device = c42Lib.getDeviceById(computerId)

		userId = device['userId']
		printValues.extend([str(userId)])

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

				#only if SOM-backup
				if backupUsage['targetComputerId'] == 2:

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

def printUserEmptyBlock():
	printRow.extend([emptyBlock])
	printRow.extend([emptyBlock])
	printRow.extend([emptyBlock])
	printRow.extend([emptyBlock])
	# printRow.extend([emptyBlock])
	# printRow.extend([emptyBlock])



def getUserReport():
	csvUserFile = csv.writer(open("allUserReport.csv", "wb+"))
	csvUserFile.writerow(csvUserHeaders)

	users = c42Lib.getAllUsers()
	for index, user in enumerate(users):
		# user = c42Lib.getUserById('6031')
		# user = c42Lib.getUserById('7403')

		printRow = []

		pUserId = user['userId']
		printRow.extend([str(pUserId)])

		pUserName = user['username']
		printRow.extend([pUserName.encode('utf-8')])

		pUserEmail = user['email']
		if pUserEmail is not None:
			printRow.extend([pUserEmail.encode('utf-8')])
		else:
			printRow.extend([emptyBlock])

		pUserOrgId = user['orgId']
		printRow.extend([str(pUserOrgId)])

		pUserOrgName = user['orgName']
		printRow.extend([pUserOrgName.encode('utf-8')])

		if 'computerCount' in user:
			pUserComputerCount = user['computerCount']
			printRow.extend([str(pUserComputerCount)])
		else:
			printRow.extend([emptyBlock])


		if 'backupUsage' in user:

			userBackupUsage = user['backupUsage']

			if userBackupUsage:

				if 'archiveHistory' in userBackupUsage[0]:

					userBackupUsageArchiveHistory = userBackupUsage[0]['archiveHistory']

					if userBackupUsageArchiveHistory:

						oldestDate = 9999999999999999999
						# "20130801": 1909986568291,
						oldestDateBytes = 0
						newestDate = 0
					    # "20130830": 1932985363857
						newestDateBytes = 0

						for key, value in userBackupUsageArchiveHistory.items():
							# print key, value
							# print oldestDate, int(key)
							if (oldestDate > int(key)):
								oldestDate = int(key)
								oldestDateBytes = value
							
							# print newestDate, int(key)
							if (newestDate <= int(key)):
								newestDate = int(key)
								newestDateBytes = value

						printRow.extend([str(oldestDate)])
						printRow.extend([str(oldestDateBytes)])
						printRow.extend([c42Lib.sizeof_fmt(oldestDateBytes)])

						printRow.extend([str(newestDate)])
						printRow.extend([str(newestDateBytes)])
						printRow.extend([c42Lib.sizeof_fmt(newestDateBytes)])


						pArchiveBytesDeltaMonth = userBackupUsage[0]['archiveBytesDeltaMonth']
						printRow.extend([str(pArchiveBytesDeltaMonth)])
						printRow.extend([c42Lib.sizeof_fmt(pArchiveBytesDeltaMonth)])


						# pArchiveBytesDeltaMonthSanityCheck = newestDateBytes - oldestDateBytes
						# printRow.extend([str(pArchiveBytesDeltaMonthSanityCheck)])
						# printRow.extend([c42Lib.sizeof_fmt(pArchiveBytesDeltaMonthSanityCheck)])

						
					else:
						printUserEmptyBlock()
				
				else:
					printUserEmptyBlock()

		else:
			printUserEmptyBlock()

		logging.info(str(printRow))
		csvUserFile.writerow(printRow)
		# print printRow


def printUserEmptyBlock():
	printRow.extend([emptyBlock])
	printRow.extend([emptyBlock])
	printRow.extend([emptyBlock])
	printRow.extend([emptyBlock])
	# printRow.extend([emptyBlock])
	# printRow.extend([emptyBlock])



getUserReport()
getDeviceReport()
# print str(c42Lib.getDevicesPageCount())
















