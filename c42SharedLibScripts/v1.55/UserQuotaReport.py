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
# File: allUserAndDeviceReport.py
# Author: Jack Phinney, Code 42 Software
# Last Modified: 03-24-2016
#
# Generates a list of all active users, showing total storage, quota, and whether the user is over quota 
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

c42Lib.cp_host = "https://10.10.44.135"
c42Lib.cp_port = "4285"
c42Lib.cp_username = "admin"
c42Lib.cp_password = getpass.getpass('Enter your CrashPlan console password: ') # You will be prompted for your password

c42Lib.cp_logLevel = "INFO"
c42Lib.cp_logFileName = "UserQuotaReport.log"
c42Lib.setLoggingLevel()

# c42Lib.MAX_PAGE_NUM = 5

# cp_api_storedBytesHistory = "/api/storedBytesHistory"



csvUserHeaders = ['userId','username','orgId','orgName','archiveBytes','quotaInBytes','overQuota']

emptyBlock = ""

printValues = []
printRow = []

def printUserEmptyBlock():
	printRow.extend([emptyBlock])
	# printRow.extend([emptyBlock])
	# printRow.extend([emptyBlock])

def getUserReport():
	csvUserFile = csv.writer(open("UserQuotaReport.csv", "wb+"))
	csvUserFile.writerow(csvUserHeaders)

	users = c42Lib.getAllUsersActiveBackup()
	for index, user in enumerate(users):

		printRow = []

		pUserId = user['userId']
		printRow.extend([str(pUserId)])

		pUserName = user['username']
		printRow.extend([pUserName.encode('utf-8')])

		pUserOrgId = user['orgId']
		printRow.extend([str(pUserOrgId)])

		pUserOrgName = user['orgName']
		printRow.extend([pUserOrgName.encode('utf-8')])

		userBackupArchiveBytes = 0

		overQuota = False

		if 'backupUsage' in user:

			userBackupUsage = user['backupUsage']

#			print userBackupUsage
#			raw_input()

			if userBackupUsage:

				if 'archiveBytes' in userBackupUsage[0]:

					userBackupArchiveBytes = userBackupUsage[0]['archiveBytes']
					logging.info(str(userBackupArchiveBytes))
			
			printRow.extend([str(userBackupArchiveBytes)])								
#				else:
#					printUserEmptyBlock()

		else:
			printUserEmptyBlock()
		
		pUserQuotaInBytes = user['quotaInBytes']
		printRow.extend([str(pUserQuotaInBytes)])

		if int(userBackupArchiveBytes) > int(pUserQuotaInBytes) and int(pUserQuotaInBytes) != -1:
			overQuota = True
		printRow.extend([str(overQuota)])

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
# print str(c42Lib.getDevicesPageCount())
















