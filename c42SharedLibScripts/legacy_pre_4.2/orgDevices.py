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


#Test values
c42Lib.cp_host = "http://localhost"
c42Lib.cp_port = "4280"
c42Lib.cp_username = "admin"
c42Lib.cp_password = "admin"


c42Lib.cp_logLevel = "INFO"
c42Lib.cp_logFileName = "getInfoByDeviceGUID.log"
c42Lib.setLoggingLevel()

csvFile = csv.writer(open("orgDevices.csv", "wb+"))
csvHeaders = ['computerId','computerName', 'userId', 'username', 'email', 'firstName', 'lastName']

csvFile.writerow(csvHeaders)
print csvHeaders

orgId = 3
computers = c42Lib.getAllDevicesByOrg(orgId)


for index, computer in enumerate(computers):
	printRow = []
	
	computerId = computer['computerId']
	printRow.extend([str(computerId)])

	computerName = computer['name']
	printRow.extend([computerName.encode('utf-8')])

	userId = computer['userId']
	printRow.extend([str(userId)])

	userObject = c42Lib.getUserById(userId)
	username = userObject['username']
	printRow.extend([username.encode('utf-8')])


	email = userObject['email']
	if email is None:
		printRow.extend([""])
	else:
		printRow.extend([email.encode('utf-8')])	

	firstName = userObject['firstName']
	if firstName is None:
		printRow.extend([""])
	else:
		printRow.extend([firstName.encode('utf-8')])

	lastName = userObject['lastName']
	if lastName is None:
		printRow.extend([""])
	else:
		printRow.extend([lastName.encode('utf-8')])


	csvFile.writerow(printRow)
	print printRow


