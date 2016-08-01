# The MIT License (MIT)
# Copyright (c) 2015,2016 Code 42

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
# File: licenseAvailabilityReport.py
# Author: P. Hirst, Code 42 Software
# Last Modified: 06-06-2016
#
# Creates a list of users whos license useage will expire at a future date

"""licenseAvailabilityReport Script

	Usage:
		licenseAvailabilityReport.py [(u <username>) | (c <credentialfile>)] [(s <serverinfofile>) | m (<serverURL> <serverPort>)] [--filePath=<savefilepath>] [--orgId=<limitToOrgs>] 

	Arguments:
		<username>		Add your username - you will be prompted for your password
		<credentialfile>		Enter a base64 encoded creditials file location
		<serverinfofile>		File to grab the host name & port
		<serverURL>			Server URL
		<serverPort>		Server Port
		<savefilepath>		File Path for log and CSV files.  Must exist before running script.
		u 		flag to enter username then be prompted for password
		c 		flag to enter the name of a credentials file.
		s 		flag to read server info from a file
		m 		flag to manually enter server URL and Port


	Options:

		-f, --filePath=<savefilepath>		File Path for log and CSV files - optional. [default: '']
		-o, --orgId=<limitToOrgs>	Limit list to this comma separated list of orgs (no spaces)
		-e 		Execute mode - otherwise defaults to test mode.
		-q		Quit processing after the days connected has been reached
		-h, --help	Show this screen.
		--version	Show version.

"""

from docopt import docopt
import sys
import requests
import json
import csv
import logging
import getpass
import time
import base64
import operator
from datetime import date
from datetime import datetime
from c42SharedLibrary import c42Lib

# Force UTF-8
reload(sys)
sys.setdefaultencoding('utf-8')

# Turn off warnings and other annoyances
requests.packages.urllib3.disable_warnings()
logging.getLogger("urllib3").setLevel(logging.WARNING)

#  EDIT THE SECTION BELOW WITH YOUR INFORMATION

c42Lib.cp_host = "https://server.com"
c42Lib.cp_port = "4285"
# update username with correct service account names
c42Lib.cp_username = "admin"	# Can be entered, but not required if manually entering password or using a credential file
c42Lib.cp_password = "admin"	# Can be entered, but not required if manually entering password or using a credential file


if __name__ == '__main__':
    arguments = docopt(__doc__, version='licenseAvailabilityReport.py 2.0')
    #schema = Schema({
    #	'--start=startDate':
    #     })
    # try:
    #     arguments = schmea.validate(arguments)
    # except SchmeaError as e:
    #     exit(e)

    logging.debug(arguments)
    #print(arguments)

cp_enterUserName       = arguments['u']						# Flag to manually enter username & password
cp_userName            = arguments['<username>']			# Manually entered username
cp_useCustomerCredFile = arguments['c']						# Flag to use a credentials file
cp_credentialFile      = arguments['<credentialfile>']		# This is a base64 encoded file with username & password, each on a separate line
cp_serverInfoFile      = arguments['s']						# Read CrashPlan server & port info from a file, each on a separate line
cp_serverInfoFileName  = arguments['<serverinfofile>']		# Server info file - url on one line, port on another line
cp_serverEntryFlag     = arguments['m']						# Manually enter server info
cp_serverHostURL       = arguments['<serverURL>']			# Server URL
cp_serverHostPort      = arguments['<serverPort>']			# Server Port
cp_onlyTheseOrgs       = arguments['--orgId']				# Exclude these orgs (by orgId).  Can use comma separated list (no spaces)
cp_filePath            = arguments['--filePath']			# File path for output files, including log


start_time = time.time()
elapsed_time = 0

todayis = time.strftime("%Y-%m-%d-%H-%M_%S")
todayisshort = time.strftime("%Y%m%d-%H-%M")
todayonly = time.strftime("%Y%m%d")


c42Lib.cp_logLevel = "INFO"
if not cp_filePath:
	c42Lib.cp_logFileName = "licenseAvailabilityReport-"+todayonly+".log"
else:
	c42Lib.cp_logFileName = cp_filePath+"licenseAvailabilityReport-"+todayonly+".log"
c42Lib.setLoggingLevel()

# print deviceGuids

totalcount = 0
totalAvailableCount = 0
devicesProcessed = 0

availableList = []

# All Orgs?

orgList = None

if cp_onlyTheseOrgs:
	orgList = map(int, cp_onlyTheseOrgs.split(',')) # split the orgIds into a list



def createCSVFiles():

	global todayonly
	global cp_filePath

# CSV File Names

filepath = ''
if cp_filePath:
	filepath = cp_filePath

licensesAvailableFile    = filepath+'licensesAvailable-01-Users-'+todayisshort+'.csv'
licensesAvailableRawFile = filepath+'licensesAvailable-02-All-'+todayisshort+'.csv'

# Generate  CSV file headers
licensesAvailableHeader = ("UserID","UserUid","UserName","First Name","Last Name","Email","OrgId","Org","Archive Guid","Device Name","Archive Size","Expire Date")

# Write CSV File Headers

c42Lib.writeCSVappend (licensesAvailableHeader, licensesAvailableFile,'w') # Write the headers to the license available list file
c42Lib.writeCSVappend (licensesAvailableHeader, licensesAvailableRawFile,'w') # Write the headers to the license available list file


# Get the backup Usage Info for a device - return the archive size if only one destination,
# return the largest archive size if more than one.

def authenticateUser():

	global cp_enterUserName
	global cp_userName
	global cp_useCustomerCredFile
	global cp_credentialFile

	userAuthType = 'Hardcoded' 

	logging.debug ("=========== Authenticate User")

	if cp_useCustomerCredFile: # If using a credentials file
		
		with open(str(cp_credentialFile)) as f:
			c42Lib.cp_username = base64.b64decode(f.readline().strip())
			c42Lib.cp_password = base64.b64decode(f.readline().strip())

		userAuthType = 'Credentials File'

	if cp_enterUserName:

		print ""
		c42Lib.cp_password = getpass.getpass('=========== Please enter the password for user ' + str(cp_userName) + ' : ')
		c42Lib.cp_username = cp_userName

		userAuthType = 'Entered Password'

	if userAuthType == 'Hardcoded':

		if c42Lib.cp_username == 'admin':
			print ""
			print "Username is set to 'admin'!  If this is really your username you should change it."
			print ""
			raw_input("Please press 'Enter' to proceed.")
			print ""

		else:
			print "Username has been hardcoded to : " + c42Lib.cp_username

		if c42Lib.cp_password == 'admin':
			print ""
			print "Username is set to 'admin'!  If this is really your password you should change it."
			print ""
			raw_input("Please press 'Enter' to proceed.")
			print ""
		else:
			print "Password has been hardcoded.  Not shown."

	return userAuthType

def cpServerInfo():

	global cp_serverInfoFile
	global cp_serverInfoFileName
	global cp_serverEntryFlag
	global cp_serverHostURL
	global cp_serverHostPort

	serverInfoType = 'Hardcoded' 

	logging.debug ("=========== Set CP Server Info")

	if cp_serverInfoFile: # If using a credentials file
		
		with open(str(cp_serverInfoFileName)) as f:
			c42Lib.cp_host = f.readline().strip()
			c42Lib.cp_port = f.readline().strip()

		serverInfoType = 'Server Info File'

	if cp_serverEntryFlag:

		print ""
		c42Lib.cp_host = cp_serverHostURL
		c42Lib.cp_port = cp_serverHostPort

		serverInfoType = 'Manually Entered'

	return serverInfoType


# May not need this!	

def unicodeFixer(name):

	print "========== Unicode Check"
	# print "Unicode Fixer: " + name
	print "Variable Type: " + str(type(name))

	if type(name) == "unicode":

		try:
			print "Passed Unicode Check: " + name

		except (UnicodeError, UnicodeEncodeError,AttributeError):

			print "Failed Unicode Check: " + str(name)
			raw_input()

	return name

def getBackupUsageInfo (backupUsageInfo):

	deviceArchiveSize = 0
	deviceArchiveSizeList = []

	if len(backupUsageInfo) == 1:
		deviceArchiveSize = backupUsageInfo[0]['archiveBytes']
	else: #more than one archive
		deviceArchiveSizeList = max(backupUsageInfo, key=lambda x: x['archiveBytes'])  # Sorts the archives by smallest to largest
		deviceArchiveSize = deviceArchiveSizeList['archiveBytes'] #Grabs the smallest

	return deviceArchiveSize


def build_dict(seq, key):
    return dict((d['user'][key], dict(d, index=index)) for (index, d) in enumerate(seq))


def licensesAvailableList ():

	global totalcount
	global totalAvailableCount
	global coldStorageArchivesProcessed
	global elapsed_time
	global todayonly
	global orgList

	totalcount = 0
	totalAvailableCount = 0


	usersInColdStorage = {}

	#Get Org List to use

	if not orgList:
		# Specific orgs not specified, gathering a list of all orgs.
		orgList = c42Lib.getAllOrgs()


	print ""
	print "========== " + str(len(orgList)) + " To Be Processed"
	print ""

	# Get Archives in Cold Storage by Org

	orgCount = 0

	for orgIndex, org in enumerate(orgList):

		orgName = org['orgName']
		orgUid  = org['orgUid']
		orgId   = org['orgId']

		orgCount += 1

		print ""
		print "========== " + str(orgCount) + " / " + str(len(orgList)) + " | Getting Cold Storage for Org : [ "+str(orgId)+" ] " + orgName
		print ""

		# Will loop just in case it's a really really long list
		currentPage = 1
		keepLooping = True


		coldStorageParams = {}
		coldStorageParams['orgId']  = orgId
		coldStorageParams['pgNum']  = currentPage
		coldStorageParams['pgSize'] = 250
		coldStorageParams['srtDir'] = 'desc'

		# Initial check to make sure there is data to be had

		coldStorageList = []
		coldStorageInfo = c42Lib.getColdStorage(coldStorageParams)

		coldStorageRowCount = len(coldStorageInfo['coldStorageRows'])

		if coldStorageInfo['totalCount'] < 1 or coldStorageRowCount < 1:
			keepLooping = False
			print ""
			print "========== Org Has No Data"
			print ""


		while keepLooping:

			coldStorageList = []
			coldStorageInfo = c42Lib.getColdStorage(coldStorageParams)

			if not coldStorageInfo['coldStorageRows'] or len(coldStorageInfo['coldStorageRows']) < 1:
				keepLooping = False

			if coldStorageInfo:

				coldStorageList = coldStorageInfo['coldStorageRows']

				#Loop Through List of Users - check if user has BackupUsage - if yes, discard.  If no, add to list.

				for deviceIndex, device in enumerate(coldStorageList):

					# print device

					# Get User Info

					userParams = {}
					userParams['userId']         = device['sourceUserId']
					userParams['idType']         = "id"
					userParams['incBackupUsage'] = "true"

					userInfo = c42Lib.getUser(userParams)

					userInfo = userInfo[0]

					totalcount += 1

					if not userInfo['backupUsage']: # User does not have any other archives!  Can be on the list!

						print "++++++++++ " + str(totalcount).zfill(6) + " | Device : " + device['sourceComputerName'] + " | " + userInfo['username'] + " has NO other active devices."

						#look up user to see if they're in the existing cold storage list.

						if usersInColdStorage and device['sourceUserId'] in usersInColdStorage: # If the user already exists in the cold storage lists we will compare archive expire dates

							print "           User already exists in cold storage.  Checking Dates."

							existingInList = usersInColdStorage[device['sourceUserId']]

							#print existingInList

							# Covert Date to Something useful
							listExpireDate = existingInList['archiveHoldExpireDate']
							# listExpireDate = datetime.strptime(listExpireDate, '%Y-%m-%d')

							thisExpireDate = device['archiveHoldExpireDate'][:-6].replace("T"," ")
							thisExpireDate = datetime.strptime(thisExpireDate, '%Y-%m-%d %H:%M:%S.%f')
							thisExpireDate = datetime.date(thisExpireDate)

							# Compare expire dates - if the current cold storage date is sooner, use it instead
							if thisExpireDate > listExpireDate:

								print "           This device has a later expire date.  Swapping it out."
								print "               In List : " + str(listExpireDate)
								print "           This Device : " + str(thisExpireDate)

								# Build dictionary value object
								replaceUserInCold = {}
								replaceUserInCold['userName']   	        = userInfo['username']
								replaceUserInCold['userUid']				= userInfo['userUid']
								replaceUserInCold['firstName']      	   	= device['sourceUserFirstName']
								replaceUserInCold['firstName']       		= device['sourceUserLastName']
								replaceUserInCold['email']          	    = device['sourceUserEmail']
								replaceUserInCold['orgId']					= device['orgId']
								replaceUserInCold['orgName']			 	= device['orgName']
								replaceUserInCold['archiveGuid']      	    = device['archiveGuid']
								replaceUserInCold['sourceComputerName']     = device['sourceComputerName']
								replaceUserInCold['archiveBytes']      		= device['archiveBytes']
								replaceUserInCold['archiveHoldExpireDate']  = thisExpireDate

								# Replace existing user with new values.
								usersInColdStorage[device['sourceUserId']]  = replaceUserInCold

								# Write this out to the raw file that will show every cold storage device

								replaceDeviceRow = (device['sourceUserId'],userInfo['userUid'],userInfo['username'],device['sourceUserFirstName'],device['sourceUserLastName'],device['sourceUserEmail'],device['orgId'],device['orgName'],device['archiveGuid'],device['sourceComputerName'],device['archiveBytes'],thisExpireDate)
								c42Lib.writeCSVappend (replaceDeviceRow, licensesAvailableRawFile,'a+')

								#print usersInColdStorage[device['sourceUserId']]
								#raw_input()
							else:
								print "           This device has an earlier expire date.  NOT Swapping it out."
								print "               In List : " + str(listExpireDate)
								print "           This Device : " + str(thisExpireDate)


						else:

							print "           Adding user/device as new to list."

							# Covert Date to Something useful
							listExpireDate = device['archiveHoldExpireDate'][:-6].replace("T"," ")
							listExpireDate = datetime.strptime(listExpireDate, '%Y-%m-%d %H:%M:%S.%f')
							listExpireDate = datetime.date(listExpireDate)

							# Build dictionary value object
							newUserInCold = {}
							newUserInCold['userName']      		    = userInfo['username']
							newUserInCold['userUid']       		    = userInfo['userUid']
							newUserInCold['firstName']     		    = device['sourceUserFirstName']
							newUserInCold['firstName']     		    = device['sourceUserLastName']
							newUserInCold['email']        		    = device['sourceUserEmail']
							newUserInCold['orgId']					= device['orgId']
							newUserInCold['orgName']				= device['orgName']
							newUserInCold['archiveGuid']        	= device['archiveGuid']
							newUserInCold['sourceComputerName'] 	= device['sourceComputerName']
							newUserInCold['archiveBytes']       	= device['archiveBytes']
							newUserInCold['archiveHoldExpireDate']  = listExpireDate

							# Insert into dictionary with userID as key
							usersInColdStorage[device['sourceUserId']] = newUserInCold
							totalAvailableCount += 1

							# Write this out to the raw file that will show every cold storage device

							newDeviceRow = (device['sourceUserId'],userInfo['userUid'],userInfo['username'],device['sourceUserFirstName'],device['sourceUserLastName'],device['sourceUserEmail'],device['orgId'],device['orgName'],device['archiveGuid'],device['sourceComputerName'],device['archiveBytes'],listExpireDate)
							c42Lib.writeCSVappend (newDeviceRow, licensesAvailableRawFile,'a+')

							#print usersInColdStorage[device['sourceUserId']]
							#raw_input()

					else:

						userDeviceCount = len(userInfo['backupUsage'])

						print "---------- " + str(totalcount).zfill(6) + " | Device : " + device['sourceComputerName'] + " | " + userInfo['username'] + " has "  + str(userDeviceCount).zfill(2) + " other active devices."

			
					if totalcount%10 == 0:
					
						elapsed_time = time.time() - start_time
					
						print ""
						print "====================================================================================="
						print ""
						print "                     Processing Org : [ "+str(orgId)+" ] " + orgName
						print ""
						print "                    Total Processed : " + str(totalcount) 
						print "Users With Licenses to Be Available : " + str(totalAvailableCount)
						print ""
						print "                       Elapsed Time : " + str(time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))
						print "                         Start TIme : " + str(time.strftime('%H:%M:%S', time.gmtime(start_time)))
						print "                 Current Time Stamp : " + str(time.strftime('%H:%M:%S', time.gmtime(time.time())))
						print "====================================================================================="			
						print ""		


				elapsed_time = time.time() - start_time
				
				print ""
				print "====================================================================================="
				print "                    Total Processed : " + str(totalcount) 
				print "Users With Licenses to Be Available : " + str(totalAvailableCount)
				print ""
				print "                       Elapsed Time : " + str(time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))
				print "                         Start TIme : " + str(time.strftime('%H:%M:%S', time.gmtime(start_time)))
				print "                 Current Time Stamp : " + str(time.strftime('%H:%M:%S', time.gmtime(time.time())))
				print "====================================================================================="			
				print ""

			else:

				keepLooping = False

			currentPage += 1
			coldStorageParams['pgNum'] = currentPage



print "========== User Inputs =========="
print ""
print arguments
print ""
print "================================="

userAuth = authenticateUser()  # Sets the variables to authenticate the user.
print ""
print "User Authentication Type: " + str(userAuth)
print ""
print "================================="

if not c42Lib.validateUserCredentials():
	print ""
	print "========== Invalid Credentials =========="
	print ""
	print "Please check the credentials and try again."
	print ""
	sys.exit(0)


cpServerInfo()
createCSVFiles()
licensesAvailableList()


logging.info("===============================================================================================")
logging.info("")
logging.info("        Total Devices processed : " + str(totalcount))
logging.info("Total licensesAvailable Devices : " + str(totalAvailableCount))
logging.info("")
logging.info("===============================================================================================")