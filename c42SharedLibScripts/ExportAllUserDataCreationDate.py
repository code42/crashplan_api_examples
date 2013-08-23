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
# 1) Export user data with no date range
# 	python ExportAllUserDataCreationDate.py null null 
#
# 2) Export user data based on date range with debug log level
#	python ExportAllUserDataCreationDate.py 8/1/2013 9/1/2013 DEBUG
# 
# from datetime import datetime
# 
# date_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
# 
# http://docs.python.org/library/datetime.html#datetime.datetime.strptime
# http://docs.python.org/library/datetime.html#strftime-and-strptime-behavior

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


# Set to your environments values
#cp_host = "<HOST OR IP ADDRESS>" ex: http://localhost or https://localhost
#cp_port = "<PORT>" ex: 4280 or 4285
#cp_username = "<username>"
#cp_password = "<pw>"

# Test values
cp_host = "http://aj-proappliance"
cp_port = "4280"
cp_username = "admin"
cp_password = "admin"

# REST API Calls
# cp_api_userRole = "/api/UserRole"
cp_api_user = "/api/User"

# This number is set to the maximum limit (current ver. 3.5.4) the REST API allows a resultset size to be.
MAX_PAGE_NUM = 250

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

#
# Sets logger to file and console
#
def setLoggingLevel():
    # set up logging to file
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='ExportAllUserDataCreationDate.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    
    if(cp_logLevel=="DEBUG"):
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
    
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


#
# Compute base64 representation of the authentication token.
#
def getAuthHeader(u,p):

    token = base64.b64encode('%s:%s' % (u,p))

    return "Basic %s" % token


def getUsers(pgNum):
	headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
	url = cp_host + ":" + cp_port + cp_api_user
	# need to get query range in here
	payload = {'incAll': "true"}
	# 'pgNum': str(pgNum), 'pgSize': str(MAX_PAGE_NUM)}

	r = requests.get(url, params=payload, headers=headers)
	logging.debug(r.text)

	content = r.content
	binary = json.loads(content)
	logging.debug(binary)

	users = binary['data']
	return users

#
# Gets the number of page requests needed to return all users.
# Note: This is used because of the current REST API resultset limit of 250 results.
#
def getUsersPageCount():
    logging.debug("getUsersPageCount")

    headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
    url = cp_host + ":" + cp_port + cp_api_user
    payload = {}
    # {'orgId': orgId}
    
    r = requests.get(url, params=payload, headers=headers)
    logging.debug(r.text)

    content = r.content
    binary = json.loads(content)
    logging.debug(binary)

    users = binary['data']
    totalCount = users['totalCount']

    logging.debug("getUsersPageCount:totalCount= " + str(totalCount))

    # num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
    numOfRequests = int(math.ceil(totalCount/MAX_PAGE_NUM)+1)

    logging.debug("getUsersPageCount:numOfRequests= " + str(numOfRequests))
   
    return numOfRequests


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

	csvFile = csv.writer(open("export.csv", "wb+"))

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
							else:
								writeTocsv = "false"
						currValues.extend([value])
					if writeTocsv == "true":
						# print writeTocsv
						csvFile.writerow(currValues)



setLoggingLevel()
performUserExportAction()


