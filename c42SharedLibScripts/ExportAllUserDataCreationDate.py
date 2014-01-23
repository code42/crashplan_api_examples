#
# File: ExportAllUserDataCreationDate.py
# Author: AJ LaVenture, Code 42 Software
# Last Modified: 08-20-2013
#
# Exports all user data with the ability to choose metadata object to query on
# only supports creation date as of right now with date range (start, end)
# will take json data and covert it to CSV file
#
# creationDate
#
# Log file: ExportAllUserDataCreationDate.py
#
# Python 2.7
# REQUIRED MODULE: Requests
# http://docs.python-requests.org/en/latest/user/install/
# 
# Uses relativedelta python module that can be downloaded from:
# http://labix.org/python-dateutil
# 
# API Call: GET api/User
#
# Arguments: startMonth, monthsForward(default 1), loggingLevel(optional)
#
# Example Usages:
# 1) Export user data with start date and how many months in the future
	# month 8, for 1 month
# 	python ExportAllUserDataCreationDate.py 8 1 
#
# 2) Export user data based on date range with debug log level
#	python ExportAllUserDataCreationDate.py 8/1/2013 1 DEBUG
# 
# from datetime import datetime
# 
# date_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
# 
# http://docs.python.org/library/datetime.html#datetime.datetime.strptime
# http://docs.python.org/library/datetime.html#strftime-and-strptime-behavior


from c42SharedLibrary import c42Lib
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

# Set to your environments values
#cp_host = "<HOST OR IP ADDRESS>" ex: http://localhost or https://localhost
#cp_port = "<PORT>" ex: 4280 or 4285
#cp_username = "<username>"
#cp_password = "<pw>"

# Test values
c42Lib.cp_host = "http://aj-proappliance"
c42Lib.cp_port = "4280"
c42Lib.cp_username = "admin"
c42Lib.cp_password = getpass.getpass('Enter your CrashPlan console password: ') # You will be prompted for your password


c42Lib.cp_logLevel = "INFO"
c42Lib.cp_logFileName = "ExportAllUserDataCreationDate.log"
c42Lib.setLoggingLevel()

csvUserHeaders = ['userId','username','email','orgId','orgName','computerCount','creationDate','UserArchive-oldestDate','UserArchive-oldestDateBytes','oldestHR','UserArchive-newestDate','UserArchive-newestDateBytes','newestHR','UserArchiveBytesDeltaMonth','deltaHR']

## ARGUMENTS ##
# ARG1 - start date for query (String)
cp_startDate = str(sys.argv[1])

# ARG2 - end date for query (String)
cp_deltaDate = 1
if len(sys.argv)==3:
	cp_deltaDate = str(sys.argv[2])

# ARG3 (optional)- logging level for console (default is INFO, add DEBUG for additional output to console)
cp_logLevel = "INFO"
if len(sys.argv)==4:
    cp_logLevel = str(sys.argv[3])


def getUserReport():
	logging.info("User Export Action: startDate:" + cp_startDate + " | deltaTime: " +
		str(cp_deltaDate) + " | loggingLevel: " + cp_logLevel)
	csvUserFile = csv.writer(open("ExportAllUserDataCreateDateReport.csv", "wb+"))
	csvUserFile.writerow(csvUserHeaders)

	start_date_object = ""
	# end_date_object = ""

	start_date_object = datetime.datetime.strptime(cp_startDate, '%m/%d/%Y')
	# end_date_object = datetime.datetime.strptime(cp_endDate, '%m/%d/%Y')
	# print end_date_object

	emptyBlock = ""

	users = c42Lib.getAllUsers()
	# users = c42Lib.getUsers(1)
	for index, user in enumerate(users):
		# user = c42Lib.getUserById('6031')
		# user = c42Lib.getUserById('7403')

		printRow = []

		creationDate = ""
		if 'creationDate' in user:
			creationDate = user['creationDate']

		currDateObj = ""
		deltaTime = ""

		if creationDate is not None:
			currDateObj = datetime.datetime.strptime(str(creationDate)[:10], "%Y-%m-%d")
			deltaTime = start_date_object+relativedelta(months=+int(cp_deltaDate))
		

		# logging.info(str(currDateObj) + " delta: " + str(deltaTime))
		if deltaTime > currDateObj > start_date_object:

			pUserId = user['userId']
			# logging.info(str(pUserId))
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

			if 'creationDate' in user:
				pUserCreationDate = user['creationDate']
				printRow.extend([pUserCreationDate])
			
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

							
			# 			else:
			# 				printUserEmptyBlock()
					
			# 		else:
			# 			printUserEmptyBlock()

			# else:
			# 	printUserEmptyBlock()

			logging.info(str(printRow))
			csvUserFile.writerow(printRow)
		else:
			logging.debug("nothing to report")
		# print printRow


def performUserExportAction():
	logging.info("User Export Action: startDate:" + cp_startDate + " | deltaTime: " +
		str(cp_deltaDate) + " | loggingLevel: " + cp_logLevel)
	

	# print cp_startDate + " " + cp_endDate + " " + cp_logLevel
	start_date_object = ""
	# end_date_object = ""

	start_date_object = datetime.datetime.strptime(cp_startDate, '%m/%d/%Y')
	# end_date_object = datetime.datetime.strptime(cp_endDate, '%m/%d/%Y')
	# print end_date_object


	count = 0
	numRequests = getUsersPageCount()
 	firstUsers = getUsers(1)

	csvFile = csv.writer(open("userCreateDate.csv", "wb+"))

	#write CSV Header
	totalCount = firstUsers['totalCount']
	columns = []
	# print totalCount
	if totalCount > 1:
		userListObject = firstUsers['users']
		for index, users in enumerate(userListObject):
			# print index, user
			# skip admin user
			# print users['userId']
			if index == 1 and users['userId'] != 1:
				# print index
				currUserObject = userListObject[index]
				for key, value in currUserObject.iteritems():
					# print key, value
					# columnName = key.replace("u'","")
					# print key
					columns.extend([key])
		#print users
		# print columns
		csvFile.writerow(columns)
		for x in xrange(1, numRequests+1):
			users = getUsers(str(x))
			userListObject = users['users']
			for index, users in enumerate(userListObject):
				currValues = []
				currUserObject = userListObject[index]
				# skip admin user
				if users['userId'] != 1:
					writeTocsv = "true"
					for key, value in currUserObject.iteritems():
						if value is None:
							value = "null"
						#custom reporting filter here
						if key == "creationDate":
							currDateObj = datetime.datetime.strptime(str(value)[:10], "%Y-%m-%d")
							deltaTime = start_date_object+relativedelta(months=+int(cp_deltaDate))
							if deltaTime > currDateObj:
								writeTocsv = "true"
								logging.info("index: "+ str(index) +" | creationDate - " + str(currDateObj))
							else:
								writeTocsv = "false"
						currValues.extend([value])
					if writeTocsv == "true":
						# print writeTocsv
						csvFile.writerow(currValues)
						logging.info(currValues)




getUserReport()
