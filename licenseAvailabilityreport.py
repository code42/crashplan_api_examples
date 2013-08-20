#
# File: licenseAvailabilityreport.py
# Author: Paul Hirst, Nick Olmsted, Code 42 Software
# Last Modified: 07-18-2013
#
# This script lists the "free up" date licenses based on their cold storage expiration date.
# Only users with all of their devices in cold storage are eligible to release a license.
#
# Uses relativedelta python module that can be downloaded from:
# http://labix.org/python-dateutil
#
# Deactivates users based on the number of months since they have last connected to a master server
# Params:
# 1 arg - type of logging (values: verbose, nonverbose)
#
# Example usages: 
# python licenseAvailabilityreport.py verbose 1 
# The above example will show a verbose log and write the results to a file.
#
# python licenseAvailabilityreport.py noverbose 0
# The above exmaple will show terse logging and produce an on screen summary of license availability
#
# NOTE: Make sure to set cpc_host, cpc_port, cpc_username, cpc_password to your environments values.
#

import sys

import json

import httplib

import base64

import math

import calendar

import logging

import array

from collections import Counter

from operator import itemgetter, attrgetter

from dateutil.relativedelta import *

from datetime import *

# verbose logging (set to DEBUG for additional console output)
cp_logLevel = "INFO"
if len(sys.argv)==1:
    cp_logLevel = str(sys.argv[1])

# Deactivate devices (should be text that equals "deactivate")
SAVE_USER_LIST = str(sys.argv[2])

MAX_PAGE_NUM = 250
NOW = datetime.now()

TOTAL_ACTIVE_USERS = 0

# Set to your environments vlaues
cpc_host = "10.10.44.58"
cpc_port = "4285"
cpc_username = "admin"
cpc_password = "admin"

#
# Compute base64 representation of the authentication token.
#
def getAuthHeader(u,p):

    # 

    token = base64.b64encode('%s:%s' % (u,p))

    return "Basic %s" % token
    
#
# Get the total number of store points that will need to be iterated through by Archive
#
def getStorePoints():
	logging.debug("BEGIN - getStorePoints")

	headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json"}
	
	try:
		conn = httplib.HTTPSConnection(cpc_host,cpc_port)
		conn.request("GET","/api/StorePoint?srtDir=desc",None,headers)
		data = conn.getresponse().read()
		conn.close()

		storepoints = json.loads(data)['data']
		storepointCount = storepoints['totalCount']
		# NOTE: storepoints and mountpoints are the different names for the same thing but are not interchangable

		logging.info("Number of Store Points (storepointCount): " + str(storepointCount))

		dCount = 0

		# Define the storepoint list - this works because it is unlikely the storepoint list will be very long
		storepointList = []

		for d in storepoints['storepoints']:
        	
        	# Get storepoint name and ID to use for iterating through ColdStorage.
        	# ColdStorage is the location where the archive expiration field is set.
        	# First check that the store point has archives in cold storage
        	
			storepointID = d['storePointId']
			storepointName = d['storePointName']
			coldbytes = d['coldBytes']

			# If Store Point has no cold storage, then skip it, otherwise, save it.

			if coldbytes > 0:
				storepointObjs = [storepointID, str(storepointName)]
				storepointList.append(storepointObjs)
				logging.debug(str(dCount) + " | Saving " + str(storepointID) + " : " + str(storepointName))
			else:
				logging.debug(str(dCount) + " | Skipping " + str(storepointID) + " : " + str(storepointName))
				
			dCount = dCount + 1
				
		logging.debug("END - getStorePoints")
		logging.info('Total Storepoints with Cold Storage Archives: ' + str(len(storepointList)))
		return storepointList

	except httplib.HTTPException as inst:

		logging.error("Exception: %s" % inst)

		return None

	except ValueError as inst:

		logging.error("Exception decoding JSON: %s" % inst)

		return None 

#
# Get archives in cold storage with their expiration dates.
#
def getColdStorageArchives(storePoints):
	logging.debug("BEGIN - ColdStorageArchives")
	
	# First, create a list of computers with active archives to compare against
	
	logging.info('Get a count of devices for the list of users with active devices.')
	countstringURL = 'Computer?pgNum=1&pgSize=1&incCounts=true&active=true'
	countDevices = getDevicesPageCount(countstringURL)
	activeList = getActiveDevices(countDevices) # Returns a list of users with active devices
	
	# print activeList
	
	activeUsercount = list(set(activeList))
	
	logging.info('There are ' + str(len(activeUsercount)) + ' users with at least one active device.')
	global TOTAL_ACTIVE_USERS
	TOTAL_ACTIVE_USERS = len(activeUsercount) # Save the total active user count to be used later. 

	headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json"}
	
	mCount = 0
	
	deviceList = []
	
	for m in storePoints:
		mountpointID = m[0]
		mountpointName = m[1]
		
		logging.info("Mount Point: " + str(mountpointID) + " | " + mountpointName)
		
		numOfRequests = getDevicesPageCount("coldStorage?mountPointId=" + str(mountpointID) + "&pgNum=1")
				
		# num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0

		currentRequestCount=0

		while (currentRequestCount <= numOfRequests):
		
			try:
				currentRequestCount = currentRequestCount + 1
				conn = httplib.HTTPSConnection(cpc_host,cpc_port)
				conn.request("GET","/api/coldStorage?mountPointId=" + str(mountpointID) + "&pgNum=" + str(currentRequestCount) + "&pgSize=250&srtKey=sourceUserId,archiveHoldExpireDate",None,headers)
				data = conn.getresponse().read()
				conn.close()

				coldStoragedevices = json.loads(data)['data']
				coldStoragedeviceCount = coldStoragedevices['totalCount']
				# NOTE: storepoints and mountpoints are the different names for the same thing but are not necessarily interchangable

				logging.debug("Number of Devices in MountPoint " + str(mountpointID) + " - " + mountpointName + " (coldStoragedeviceCount): " + str(coldStoragedeviceCount))

				dCount = 0
			
				for d in coldStoragedevices['coldStorageRows']:
        	
	        		# Get archive information
        	
					archiveExpireDate = d["archiveHoldExpireDate"]
					computerID = d["sourceComputerId"]
					computerName = d["sourceComputerName"]
					userName = d["sourceUserEmail"]
					userID = d["sourceUserId"]
					archiveBytes = d["archiveBytes"]
					
					# Check to see if device belongs to a user that has an active or deauthorized device with storage
					
					if not ( userID in activeList ):
						# Encode computer names to protect against throwing decoding errors
						computerNamedecoded = computerName.encode('utf-8')		
						deviceObjs = (userID, str(archiveExpireDate), computerID, str(computerNamedecoded), str(userName), str(mountpointName))
						deviceList.append(deviceObjs)
						logging.debug("     " + str(dCount) + " | Saving UserID: " + str(userID) + " computerID:  " + str(computerID) + " Expire Date: " + str(archiveExpireDate))
					else: 
						logging.debug("     " + str(dCount) + " | Tossing UserID: " + str(userID) + " computerID:  " + str(computerID) + " Expire Date: " + str(archiveExpireDate))
				
					dCount = dCount + 1	
				
			except httplib.HTTPException as inst:

				logging.error("Exception: %s" % inst)
	
				return None

			except ValueError as inst:

				logging.error("Exception decoding JSON: %s" % inst)
	
				return None
					
		mCount = mCount + 1
			
	logging.info ("Total Devices with Cold Storage Archives: " + str(len(deviceList)))
	return deviceList 

#
# Get the total page count that is used to determine the number of GET requests needed to return all
# all of the devices since the API currently limits this call to return 250 devices. 
# Returns: total number of requests needed
#
def getDevicesPageCount(countstringURL):
    logging.debug("BEGIN - getDevicesPageCount")
    logging.debug("Count String : " + countstringURL)

    headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json"}

    # print 'Counting Devices Here: ' + countstringURL

    try:
        conn = httplib.HTTPSConnection(cpc_host,cpc_port)
        conn.request("GET","/api/" + countstringURL,None,headers)
        #Computer?pgNum=1&pgSize=1&incCounts=true&active=true
        
        logging.debug ('Getting Device Count for ' + countstringURL)
        
        data = conn.getresponse().read()
        conn.close()

        devices = json.loads(data)['data']
        totalCount = devices['totalCount']

        # num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
        numOfRequests = math.ceil(totalCount/MAX_PAGE_NUM)+1

        logging.debug("numOfRequests: " + str(numOfRequests))
        logging.debug("END - getDevicesPageCount")
        logging.info('\n')
        logging.info('Found ' + str(totalCount) + ' Devices')
        logging.info('Will need ' + str(int(numOfRequests)) + ' group(s) of API calls.')
        logging.info('--------------------------------------------------------------------------')
        return numOfRequests

    except httplib.HTTPException as inst:

        logging.error("Exception: %s" % inst)

        return None

    except ValueError as inst:

        logging.error("Exception decoding JSON: %s" % inst)

        return None

#
# Calls the API to get a list of active devices. Calls the API multiple times because the API limits the results to 250. 
# Loops through the devices and adds devices that are older than the month threshold (i.e. devices older than 3 months)
# Parameter: totalNumOfRequest - integrer that is used to determine the number of times the API needs to be called. 
# Returns: list of devices to be deactivated
# API: /api/Computer/
# API Params:
#   pgNum - pages through the results.
#   psSize - number of results to return per page. Current API max is 250 results.
#   incCounts - includes the total count in the result
#   active - return only active devices
#
def getActiveDevices(totalNumOfRequests):

    logging.debug("BEGIN - getDevices")

    headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json"}

    currentRequestCount=0
    activeCount = 0
    activeList = []

    while (currentRequestCount <= totalNumOfRequests):

        logging.debug("BEGIN - getDevices - Building devices list request count: " + str(currentRequestCount))

        try:
            currentRequestCount = currentRequestCount + 1
            conn = httplib.HTTPSConnection(cpc_host,cpc_port)
            conn.request("GET","/api/Computer?pgNum=" + str(currentRequestCount) + "&pgSize=250&incCounts=true&active=true",None,headers)
            data = conn.getresponse().read()
            conn.close()
        except httplib.HTTPException as inst:

            logging.error("Exception: %s" % inst)

            return None

        except ValueError as inst:

            logging.error("Exception decoding JSON: %s" % inst)

            return None

        devices = json.loads(data)['data']
        logging.debug("Total Device Count: " + str(devices['totalCount']))
        for d in devices['computers']:
            # Get fields to compare
            computerId = d['computerId']
            lastConnected = d['lastConnected']
            deviceName = d['name']
            status = d['status']
            userID = d['userId']
            
            # Encode device name to make sure it doesn't throw an error
            deviceNameecoded = deviceName.encode('utf8')
            
            # If user has a status that indicates an in-use archive, add them to the list for future use.
            if (status == 'Active' or status == 'Active, Deauthorized'):
                try:
                    logging.debug("Active : " + status + " - UserID: " + str(userID) + " - Computer ID: " + str(computerId) + " with last connected date of: " + str(lastConnected))
                except:
                    #ignore name errors
                    pass
                activeCount = activeCount + 1
                activeList.append(userID)
            else:
                logging.debug("IGNORE - device id: " + status + " - "  + str(computerId) + " with last connected date of: " + str(lastConnected))
        
        logging.info("Building active device list... request count:  " + str(currentRequestCount))

        logging.debug("TOTAL Devices that are have active archives: " + str(activeCount))
        logging.debug("END - getDevices")

    return activeList
    
    
# Find the archive for each user that will expire last, save it
# First, count the number of archives for that user
# Iterate that many times
# Get the latest expiration date and add that to the table of licenses that will be available on date y
def getLastarchive(archiveList):

	logging.debug("START - getLastarchive")
	
	archiveCount = len(archiveList)
	dateList = []
	
	if (archiveCount > 1):
		dCount = 1
		for d in archiveList:
			dCount = dCount + 1
			dateList.append(d)

		latestDate = max(dateList,key=itemgetter(1))
		# print 'MAX Date: ' + str(latestDate)
	else:
		latestDate = archiveList[0]
		
	return latestDate
	
	logging.debug("END - getLastarchive")

# Iterate through the users that have archives that will expire (these users have no active devices or archives - only archives in cold storage)
def userExpirelist(archiveList):
	
	logging.debug("START - userExpirelist")
	
	userList = []
	for d in archiveList:
		userList.append(d[0])
	
	userCount = list(set(userList))
	
	return userCount
	
	logging.debug("START - userExpirelist")	

# Build the list of expired archives that will result in freeing up licenses.
def expireList(archiveList):

	logging.debug("START - expireList")
	
	userList = userExpirelist(archiveList) # Gets the unique users from the archive list
	
	archiveExpirelist = []

	for uL in userList:
		currentUserArchives = []
		for aL in archiveList:
			if (aL[0] == uL):
				currentUserArchives.append(aL)	
		archiveExpirelist.append(getLastarchive(currentUserArchives))
						
	return archiveExpirelist

	logging.debug("END - expireList")
	
	
# Sort and Group Expiration Dates into a list

def sortExpiredates(archiveList):
	
	logging.debug("START - sortExpiredates")
	
	justMonthslist = []
	
	#Sort the list by date
	archiveList.sort(key=lambda tup: tup[1])
	
	todayis = str(NOW)[:10]
	
	if (SAVE_USER_LIST == "1"):
		logging.info ('Saving Users to File')
		output = open("CrashPlanPROe_License_Available_List_" + todayis +".txt", "w") # Open the file
		output.write ("CrashPlanePROe License Availablity List - " +  todayis + "\n")
		output.write ("=====================================================================================================================================\n")
		output.write ("UserID      UserName                       DeviceID   Device Name                       Expire Date          MountPointID\n")
		output.write ("-------------------------------------------------------------------------------------------------------------------------------------\n")
		
	
	for d in archiveList:
		justThedate = datetime.strptime(str(d[1])[:10], "%Y-%m-%d")
		archiveExpiremonth = justThedate.strftime('%m')
		archiveExpireyear = justThedate.strftime('%Y')
		archiveExpireclean = archiveExpireyear + '-' + archiveExpiremonth
		justMonthslist.append(archiveExpireclean)
		if (SAVE_USER_LIST == "1"):
			output.write (str(d[0]).rjust(6)+"     "+str(d[4]).ljust(32)+str(d[2]).ljust(10)+str(d[3]).ljust(35)+str(justThedate)[:10]+"     "+str(d[5]).rjust(30)+"\n")
	
	if (SAVE_USER_LIST == 1):
		output.close
		
	groupedMonths = Counter(justMonthslist)	
			
	return groupedMonths
	
	logging.debug("END - sortExpiredates")
		

# Pretty display of final results
# Display & write final results		

def prettyResultsprinted(expireDates):

	logging.debug("START - prettyResultsprinted")
	
	totalLicenses = 0
	
	todayis = str(NOW)[:10] # Convert today's date/time string to just the date
	
	logging.info( "CrashPlanPROe License Availablity Summary "+todayis+"\n")
	logging.info( "========================================================")
	
	# Save to Text File - CrashPlanPROe_License_Available.txt
	
	if (SAVE_USER_LIST == "1"):
		writetype = "a"
		output = open("CrashPlanPROe_License_Available_List_"+todayis+".txt", writetype) # Open the file
		output.write ("\n\n")
	else:
		writetype = "w"
		output = open("CrashPlanPROe_License_Available_"+todayis+".txt", writetype) # Open the file
	
	try:	
		output.write ("CrashPlanPROe License Availablity Summary "+todayis+"\n")
		output.write ("========================================================\n")

		for d in expireDates:
			totalLicenses = totalLicenses+d[1]
			if (d[1] == 1):
				logging.info((str(d[1]).rjust(6)) + " license will be available   " + d[0])
				output.write ((str(d[1]).rjust(6)) + " license will be available   " + d[0]+"\n")
			else:
				logging.info((str(d[1]).rjust(6)) + " licenses will be available  " + d[0])
				output.write ((str(d[1]).rjust(6)) + " licenses will be available  " + d[0]+"\n")
		
		totalInUselicenses = totalLicenses + TOTAL_ACTIVE_USERS #calculate the total number of licenses actually being used
		
		output.write ("========================================================\n")
		output.write ((str(totalLicenses).rjust(6)) + " total licenses to be made available.\n")
		output.write ((str(TOTAL_ACTIVE_USERS).rjust(6)) + " total licenses used with by users with active archives.\n")
		output.write ((str(totalInUselicenses).rjust(6)) + " total licenses currently being used.\n")
		output.write ("\n\nNOTE:  Licenses will become available when the cold storage archives expire or are removed.\n")
		
		logging.info ("========================================================")
		logging.info ((str(totalLicenses).rjust(6)) + " total licenses to be made available.")
		logging.info ((str(TOTAL_ACTIVE_USERS).rjust(6)) + " total licenses used with by users with active archives.")
		logging.info ((str(totalInUselicenses).rjust(6)) + " total licenses currently being used.")
		logging.info ("\n\nNOTE:  Licenses will become available when the cold storage archives expire or are removed.")
	
	finally:
		output.close
	
	logging.debug("END - prettyResultsprint")


# Main Function

def figureOutExpirelist():
	
	logging.debug("START - figureOutExpirelist")

	# Get the store points with cold storage
	print '\n'
	print 'Getting Store Points with Cold Storage'
	print '\n'
	coldStoragestorepoints = getStorePoints()
	# Get the device list
	print '\n'
	print '***********************************************************************'
	print 'Getting Devices with Cold Storage'
	print '\n'
	coldStoragedevices = getColdStorageArchives(coldStoragestorepoints)
	print '\n'
	# Sort list of cold storage devices by Users and by Archive Date
	coldStoragebyUser = sorted(coldStoragedevices, key=itemgetter(0,1))
	# Get the archive expiration dates
	print '***********************************************************************'
	print 'Getting the expiration date of the last expiring archive for each user.'
	print '\n'
	archiveExpirelist = expireList(coldStoragebyUser)
	# Get just the months of expiration dates
	print '***********************************************************************'
	print 'Sorting and prepping for output.'
	print '\n'
	expiringMonthslist = sortExpiredates(archiveExpirelist)
	prettyResultsprinted(expiringMonthslist.items())
	if (SAVE_USER_LIST == "1"):
		print '\n'
		print 'Results written to CrashPlanPROe_License_Available_'+str(NOW)[:10]+'.txt\n'
		print '\n'	
	
	
	logging.debug("END - figureOutExpirelist")	
		
#
# Sets logger to file and console
#
def setLoggingLevel():
    # set up logging to file
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='licenseAvailabilityreport.log',
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


setLoggingLevel()
figureOutExpirelist()