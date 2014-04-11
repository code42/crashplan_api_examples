#
# File: c42SharedLibary.py
# Author: AJ LaVenture, Code 42 Software
# Last Modified: 09-04-2013
#
# Common and reused functions to allow for rapid script creation
# 

# sudo pip install requests
# sudo pip install python-dateutil [-update]
# sudo pip install simplejson



import math
import sys
import simplejson as json
import csv
import base64
import logging
import requests
import math
from dateutil.relativedelta import *
import datetime
import calendar
import re




class c42Lib(object):

	# Set to your environments values
	#cp_host = "<HOST OR IP ADDRESS>" ex: http://localhost or https://localhost
	#cp_port = "<PORT>" ex: 4280 or 4285
	#cp_username = "<username>"
	#cp_password = "<pw>"

	# Test values
	cp_host = "http://localhost"
	# cp_host = "http://aj-proappliance"
	cp_port = "4280"
	cp_username = "admin"
	cp_password = "admin"

	# REST API Calls
	cp_api_userRole = "/api/UserRole"
	cp_api_user = "/api/User"
	cp_api_org = "/api/Org"
	cp_api_archive = "/api/Archive"
	cp_api_deviceUpgrade = "/api/DeviceUpgrade"
	cp_api_computer = "/api/Computer"
	cp_api_userMoveProcess = "/api/UserMoveProcess"
	cp_api_cli = "/api/cli"
	cp_api_restoreHistory = "/api/restoreHistory"
	#?pgNum=1&pgSize=50&srtKey=startDate&srtDir=desc&days=9999&orgId=35
	cp_api_archiveMetadata = "/api/ArchiveMetadata"
	cp_api_server = "/api/Server"

	cp_logLevel = "INFO"
	cp_logFileName = "c42SharedLibrary.log"
	# This number is set to the maximum limit (current ver. 3.5.4) the REST API allows a resultset size to be.
	MAX_PAGE_NUM = 250


	#
	# getRequestHeaders:
	# Returns the dictionary object containing headers to pass along with all requests to the API, 
	# Params: None
	# Uses global / class variables for username and password authentication
	#
	@staticmethod
	def getRequestHeaders():
		header = {"Authorization":c42Lib.getAuthHeader(c42Lib.cp_username,c42Lib.cp_password), "Content-Type": "application/json"}
		# print header
		return header

	#
	# getRequestUrl(cp_api):
	# Returns the full URL to execute an API call,
	# Params:
	# cp_api: what the context root will be following the host and port (global / class variables)
	#

	@staticmethod
	def getRequestUrl(cp_api):
		url = c42Lib.cp_host + ":" + c42Lib.cp_port + cp_api
		return url

	#
	# executeRequest(type, cp_api, params, payload):
	# Executes the request to the server based on type of request
	# Params:
	# type: type of rest call: valid inputs: "get|delete|post|put" - returns None if not specified
	# cp_api: the context root to be appended after server:port when generating the URL
	# params: URL parameters to be passed along with the request
	# payload: json object to be sent in the body of the request
	# Returns: the response object directly from the call to be parsed by other methods
	# 

	@staticmethod
	def executeRequest(type, cp_api, params, payload):
		# logging.debug
		header = c42Lib.getRequestHeaders()
		# print header
		url = c42Lib.getRequestUrl(cp_api)
		# url = cp_host + ":" + cp_port + cp_api
		# payload = cp_payload

		if type == "get":
			logging.info(str(payload))
			r = requests.get(url, params=params, data=json.dumps(payload), headers=header, verify=False)
			logging.debug(r.text)
			return r
		elif type == "delete":
			r = requests.delete(url, params=params, data=json.dumps(payload), headers=header, verify=False)
			logging.debug(r.text)
			return r
		elif type == "post":
			r = requests.post(url, params=params, data=json.dumps(payload), headers=header, verify=False)
			logging.debug(r.text)
			return r
		elif type == "put":
			# logging.debug(str(json.dumps(payload)))
			r = requests.put(url, params=params, data=json.dumps(payload), headers=header, verify=False)
			logging.debug(r.text)
			return r
		else:
			return None	

		# content = r.content
		# binary = json.loads(content)
		# logging.debug(binary)

	# 
	# getUserPageCount():
	# Returns how many pages it will take to get all of the users in the system 
	# using MAX_PAGE_NUM global / class variable.
	# params:
	# returns: integer
	# 
	@staticmethod
	def getUsersPageCount():
	    logging.info("getUsersPageCount")

	    # headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
	    # url = cp_host + ":" + cp_port + cp_api_user
	    params = {'active': 'true', 'pgSize': '1', 'pgNum': '1'}
	    payload = {}
	    # r = requests.get(url, params=payload, headers=headers)
	    # logging.debug(r.text)

	    r = c42Lib.executeRequest("get", c42Lib.cp_api_user, params, payload)

	    content = r.content
	    binary = json.loads(content)
	    logging.debug(binary)


	    users = binary['data']
	    totalCount = users['totalCount']

	    logging.info("getUsersPageCount:totalCount= " + str(totalCount))

	    # num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
	    numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)

	    logging.info("getUsersPageCount:numOfRequests= " + str(numOfRequests))
	   
	    return numOfRequests





	# def getUsersPageCountByOrg(orgId):

	# 	c42Lib.getUsersPageCountByOrg(orgId, None)
	# 
	# getUsersPageCountByOrg(orgId):
	# Gets the number of page requests needed to return all users within an org.
	# Uses the MAX_PAGE_NUM global / class variable.
	# Note: This is used because of the current REST API resultset limit of 250 results.
	#
	@staticmethod
	def getUsersPageCountByOrg(orgId):
	    logging.info("getUsersPageCountByOrg-params: orgId[" + str(orgId) + "]")

	    # headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
	    # url = cp_host + ":" + cp_port + cp_api_user
	    # if incSubOrgs != None
	    params = {'orgId': orgId, 'active': 'true', 'pgSize': '1', 'pgNum': '1'}
	    payload = {}
	    # r = requests.get(url, params=payload, headers=headers)
	    # logging.debug(r.text)

	    r = c42Lib.executeRequest("get", c42Lib.cp_api_user, params, payload)

	    content = r.content
	    binary = json.loads(content)
	    logging.debug(binary)


	    users = binary['data']
	    totalCount = users['totalCount']

	    logging.info("getUsersPageCountByOrg:totalCount= " + str(totalCount))

	    # num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
	    numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)

	    logging.info("getUsersPageCountByOrg:numOfRequests= " + str(numOfRequests))
	   
	    return numOfRequests

	# 
	# getUserById(userId):
	# returns the user json object of the requested userId
	# params:
	# userId: the id of the user within the system's database
	# 
	@staticmethod
	def getUserById(userId):
		logging.info("getUser-params:userId[" + str(userId) + "]")

		params = {'incAll': 'true'}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_user + "/" + str(userId), params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		user = binary['data']
		return user

	#
	# getUsersByOrgPaged
	# Returns a list of active users within an orgization by page, 
	# Params:
	# orgId - integer, that is used to limit the users to an org. Can be set to 0 to return all users.
	# pgNum - page request for user list (starting with 1)
	#
	@staticmethod
	def getUsersByOrgPaged(orgId, pgNum):
	    logging.info("getUsersByOrgPaged-params:orgId[" + str(orgId) + "]:pgNum[" + str(pgNum) + "]")

	    # headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
	    # url = cp_host + ":" + cp_port + cp_api_user
	    params = {'orgId': orgId, 'pgNum': str(pgNum), 'pgSize': str(c42Lib.MAX_PAGE_NUM), 'active': 'true'}
	    payload = {}
	    logging.info(str(payload))
	    # r = requests.get(url, params=payload, headers=headers)
	    r = c42Lib.executeRequest("get", c42Lib.cp_api_user, params, payload)

	    logging.debug(r.text)
	    
	    content = r.content
	    binary = json.loads(content)
	    logging.debug(binary)


	    users = binary['data']['users']
	    return users

	# 
	# getUsersPaged(pageNum):
	# Returns list of active users within the system based on page number
	# params:
	# pgNum - page request for user list (starting with 1)
	# 
	@staticmethod
	def getUsersPaged(pgNum):
	    logging.info("getUsersPaged-params:pgNum[" + str(pgNum) + "]")

	    # headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
	    # url = cp_host + ":" + cp_port + cp_api_user
	    params = {'incAll': 'true', 'pgNum': str(pgNum), 'pgSize': str(c42Lib.MAX_PAGE_NUM), 'active': 'true'}
	    payload = {}

	    # r = requests.get(url, params=payload, headers=headers)
	    r = c42Lib.executeRequest("get", c42Lib.cp_api_user, params, payload)

	    logging.debug(r.text)
	    
	    content = r.content
	    binary = json.loads(content)
	    logging.debug(binary)

	    users = binary['data']['users']
	    return users


	# 
	# getAllUsers():
	# Returns json users in single list
	# no limit or batching, will return all users within the system
	# 
	@staticmethod
	def getAllUsers_old():
		logging.info("getAllUsers")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getUsersPageCount()
		fullUserList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			pagedUserList = c42Lib.getUsersPaged(currentRequestCount)
			fullUserList.extend(pagedUserList)
		return fullUserList


	@staticmethod
	def getAllUsers():
		logging.info("getAllUsers")
		currentPage = 1
		keepLooping = True
		fullList = []
		while keepLooping:
			pagedList = c42Lib.getUsersPaged(currentPage)
			if pagedList:
				fullList.extend(pagedList)
			else:
				keepLooping = False
			currentPage += 1
		return fullList

	@staticmethod
	def generaticLoopUntilEmpty():
		currentPage = 1
		keepLooping = True
		fullList = []
		while keepLooping:
			# pagedList = c42Lib.getUsersPaged(currentPage)
			pagedList = c42Lib.getDevices(currentPage)
			if pagedList:
				fullList.extend(pagedList)
			else:
				keepLooping = False
			currentPage += 1
		return fullList

	# 
	# getAllUsersByOrg(orgId):
	# Returns json users in single list limited by organization
	# no limit or batching, will return all users within the organization
	# Params:
	# orgId - ID of the organization to query for users
	# 

	@staticmethod
	def getAllUsersByOrg_old(orgId):
		logging.info("getAllUsersByOrg-params:orgId[" + str(orgId) + "]")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getUsersPageCountByOrg(orgId)
		fullUserList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			pagedUserList = c42Lib.getUsersByOrgPaged(orgId, currentRequestCount)
			fullUserList.extend(pagedUserList)
		return fullUserList


	@staticmethod
	def getAllUsersByOrg(orgId):
		logging.info("getAllUsersByOrg-params:orgId[" + str(orgId) + "]")
		currentPage = 1
		keepLooping = True
		fullList = []
		while keepLooping:
			pagedList = c42Lib.getUsersByOrgPaged(orgId, currentPage)
			if pagedList:
				fullList.extend(pagedList)
			else:
				keepLooping = False
			currentPage += 1
		return fullList

	# 
	# putUserUpdate(userId, payload):
	# updates a users information based on the payload passed
	# params:
	# userId - id for the user to update
	# payload - json object containing name / value pairs for values to update
	# returns: user object after the update
	# 

	@staticmethod
	def putUserUpdate(userId, payload):
		logging.info("putUserUpdate-params:userId[" + str(userId) + "],payload[" + str(payload) + "]")

		if (payload is not None and payload != ""):
			params = {}
			r = c42Lib.executeRequest("put", c42Lib.cp_api_user + "/" + str(userId), params, payload)
			logging.debug(str(r.status_code))
			content = r.content
			binary = json.loads(content)
			logging.debug(binary)
			user = binary['data']
			return user
			# if (r.status_code == 200):
				# return True
			# else:
				# return False
		else:
			logging.error("putUserUpdate param payload is null or empty")


	# 
	# postUserMoveProcess(userId, orgId):
	# posts request to move use into specified organization
	# params:
	# userId - id of the user for the move request
	# orgId - destination org for the user
	# returns: true if 204, respose object if 500, else false
	# 

	@staticmethod
	def postUserMoveProcess(userId, orgId):
		logging.info("postUserMoveProcess-params:userId[" + str(userId) + "],orgId[" + str(orgId) + "]")

		params = {}
		payload = {"userId": userId, "parentOrgId": orgId}

		r = c42Lib.executeRequest("post", c42Lib.cp_api_userMoveProcess, params, payload)
		logging.debug(r.status_code)

		if (r.status_code == 204):
			return True
		elif (r.status_code == 500):
			content = r.content
			binary = json.loads(content)
			logging.debug(binary)
			return False
		else:
			return False

	# 
	# getOrg(orgId):
	# Returns all organization data for specified organization
	# params:
	# orgId - id of the organization you want to return
	# Returns:
	# json object
	# 
	
	@staticmethod
	def getOrg(orgId):
		logging.info("getOrg-params:orgId[" + str(orgId) + "]")

		params = {'incAll': 'true'}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_org + "/" + str(orgId), params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		org = binary['data']
		return org

	#
	# getOrgs(pgNum):
	# returns json list object of all users for the requested page number
	# params:
	# pgNum - page request for information (starting with 1)
	# 

	@staticmethod
	def getOrgs(pgNum):
		logging.info("getOrgs-params:pgNum[" + str(pgNum) + "]")

		params = {'pgNum': str(pgNum), 'pgSize': str(c42Lib.MAX_PAGE_NUM)}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_org, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		orgs = binary['data']
		return orgs

	# 
	# getOrgPageCount():
	# returns number of pages of orgs within the system using MAX_PAGE_NUM
	# returns: integer
	# 

	@staticmethod
	def getOrgPageCount():
		logging.info("getOrgPageCount")
		params = {'pgSize': '1', 'pgNum': '1'}
		payload = {}
		r = c42Lib.executeRequest("get", c42Lib.cp_api_org, params, payload)

		logging.debug(r.text)
		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		orgs = binary['data']
		totalCount = orgs['totalCount']

		logging.info("getOrgPageCount:totalCount= " + str(totalCount))

		# num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
		numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)

		logging.info("getOrgPageCount:numOfRequests= " + str(numOfRequests))

		return numOfRequests

	# 
	# getAllOrgs():
	# returns json list of all organizations within the system
	# 

	@staticmethod
	def getAllOrgs_old():
		logging.info("getAllOrgs")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getOrgPageCount()
		fullOrgList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			pagedOrgList = c42Lib.getOrgs(currentRequestCount)
			fullOrgList.extend(pagedOrgList)
		return fullOrgList

	@staticmethod
	def getAllOrgs():
		logging.info("getAllOrgs")
		currentPage = 1
		keepLooping = True
		fullList = []
		while keepLooping:
			pagedList = c42Lib.getOrgs(currentPage)
			if pagedList:
				fullList.extend(pagedList)
			else:
				keepLooping = False
			currentPage += 1
		return fullList

	# 
	# getDeviceByGuid(guid):
	# returns device information based on guid
	# params:
	# guid - guid of device
	# 

	@staticmethod
	def getDeviceByGuid(guid):
		logging.info("getDeviceByGuid-params:guid[" + str(guid) + "]")

		params = {'incAll': 'true', 'guid': str(guid)}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		device = binary['data']
		return device


	# 
	# getDeviceById(computerId):
	# returns device information based on computerId
	# params:
	# computerId: computerId of device
	# 

	@staticmethod
	def getDeviceById(computerId):
		logging.info("getDeviceById-params:computerId[" + str(computerId) + "]")

		params = {'incAll': 'true'}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer + "/" + str(computerId), params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		device = binary['data']
		return device


	# 
	# getDevicesPageCount():
	# returns number of pages it will take to return all of the devices based on MAX_PAGE_NUM
	# Returns: integer
	# 

	@staticmethod
	def getDevicesPageCount():
		logging.info("getDevicesPageCount")

		params = {'incCounts': 'true', 'active': 'true', 'pgSize': '1', 'pgNum': '1'}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)


		devices = binary['data']
		totalCount = devices['totalCount']

		logging.info("getDevicesPageCount:totalCount= " + str(totalCount))

		# num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
		numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)

		logging.info("getDevicesPageCount:numOfRequests= " + str(numOfRequests))

		return numOfRequests


	# 
	# getDevicesPageCountByOrg(orgId):
	# returns number of pages it will take to return devices by organization based on MAX_PAGE_NUM
	# Returns: integer

	@staticmethod
	def getDevicesPageCountByOrg(orgId):
		logging.info("getDevicesPageCountByOrg-params:orgId[" + str(orgId) + "]")

		params = {'orgId': orgId, 'incCounts': 'true', 'active': 'true', 'pgSize': '1', 'pgNum': '1'}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		devices = binary['data']
		totalCount = devices['totalCount']

		logging.info("getDevicesPageCountByOrg:totalCount= " + str(totalCount))

		# num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
		numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)

		logging.info("getDevicesPageCountByOrg:numOfRequests= " + str(numOfRequests))

		return numOfRequests

	# 
	# getDevices(pgNum):
	# returns all devices in system for requested page number within a single json object
	# 

	@staticmethod
	def getDevices(pgNum):
		logging.info("getDevices-params:pgNum[" + str(pgNum) + "]")

		# headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
		# url = cp_host + ":" + cp_port + cp_api_user
		params = {'pgNum': str(pgNum), 'pgSize': str(c42Lib.MAX_PAGE_NUM), 'active': 'true', 'incBackupUsage': 'true', 'incHistory': 'true'}
		 # ,'incHistory': 'true'}
		payload = {}

		# r = requests.get(url, params=payload, headers=headers)
		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		devices = binary['data']['computers']
		return devices


	# 
	# getDevicesByOrgPaged(orgId, pgNum):
	# returns devices by organization for requested page number within a single json object
	# 

	@staticmethod
	def getDevicesByOrgPaged(orgId, pgNum):
		logging.info("getDevicesByOrgPaged-params:orgId[" + str(orgId) + "]:pgNum[" + str(pgNum) + "]")

		# headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
		# url = cp_host + ":" + cp_port + cp_api_user
		params = {'orgId': orgId, 'pgNum': str(pgNum), 'pgSize': str(c42Lib.MAX_PAGE_NUM), 'active': 'true', 'incBackupUsage': 'true', 'incHistory': 'true'}
		payload = {}

		# r = requests.get(url, params=payload, headers=headers)
		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		devices = binary['data']['computers']
		return devices


	# 
	# getAllDevices():
	# returns all devices in system within single json object
	# 

	@staticmethod
	def getAllDevices_old():
		logging.info("getAllDevices")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getDevicesPageCount()
		fullDeviceList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			pagedDeviceList = c42Lib.getDevices(currentRequestCount)
			fullDeviceList.extend(pagedDeviceList)
		logging.debug(fullDeviceList)
		return fullDeviceList

	@staticmethod
	def getAllDevices():
		logging.info("getAllDevices")
		currentPage = 1
		keepLooping = True
		fullList = []
		while keepLooping:
			pagedList = c42Lib.getDevices(currentPage)
			if pagedList:
				fullList.extend(pagedList)
			else:
				keepLooping = False
			currentPage += 1
		return fullList


	@staticmethod
	def getAllDevicesByOrg_old(orgId):
		logging.info("getAllDevicesByOrg-params:orgId[" + str(orgId) + "]")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getDevicesPageCountByOrg(orgId)
		fullDeviceList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			pagedDeviceList = c42Lib.getDevicesByOrgPaged(orgId, currentRequestCount)
			fullDeviceList.extend(pagedDeviceList)
		logging.debug(fullDeviceList)
		return fullDeviceList

	@staticmethod
	def getAllDevicesByOrg(orgId):
		logging.info("getAllDevicesByOrg-params:orgId[" + str(orgId) + "]")
		currentPage = 1
		keepLooping = True
		fullList = []
		while keepLooping:
			pagedList = c42Lib.getDevicesByOrgPaged(orgId, currentPage)
			if pagedList:
				fullList.extend(pagedList)
			else:
				keepLooping = False
			currentPage += 1
		return fullList


	@staticmethod
	def putDeviceUpgrade(computerId):
		logging.info("putDeviceUpgrade-params:computerId[" + str(computerId) + "]")

		result = False

		params = {}
		payload = {}

		r = c42Lib.executeRequest("put", c42Lib.cp_api_deviceUpgrade + "/" + str(computerId), params, payload)
		
		logging.debug(r.text)
		logging.debug(r.status_code)

		if (r.status_code == 201):
			return True
		else:
			return False



	#
	# Adds the role to an individual user. 
	# Note: attempts to add the role to a user even if it already exists. 
	#
	@staticmethod
	def addUserRole(userId, roleName):
		logging.info("addUserRole-params: userId[" + userId + "]:roleName[" + roleName + "]")

		result = False
		if(userId!=1):
			# headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
			# url = cp_host + ":" + cp_port + cp_api_userRole
			params = {}
			payload = {'userId': userId, 'roleName': roleName}
			# r = requests.post(url, data=json.dumps(payload), headers=headers)
			
			r = c42Lib.executeRequest("post", c42Lib.cp_api_userRole, params, payload)

			logging.debug(r.text)
			logging.debug(r.status_code)
			if(r.status_code == 200):
				result = True
		else:
			logging.debug("user is the default admin user, skip adding the user role.")
			result = True
		# Post was successful with an HTTP return code of 200
		return result


	#
	# Adds a role for all users per org
	#
	def addAllUsersRoleByOrg(orgId, roleName):
		logging.info("addAllUsersRoleByOrg-params: orgId[" + str(orgId) + "]:userRole[" + roleName + "]")

		count = 0
		users = c42Lib.getAllUsersByOrg(orgId)
		for user in users['users']:
			userId = str(user['userId'])
			userName = user['username']
			if (c42Lib.addUserRole(userId, roleName)):
				count = count + 1
				logging.info("Success: userRole[" + roleName + "] added for userId[" + userId + "]:userName[" + userName + "]")
			else:
				logging.info("Fail: userRole[" + roleName + "] added for userId[" + userId + "]:userName[" + userName + "]")

		logging.info("Total Users affected: " + str(count))

	#
	# Adds a role for all users per org
	#
	def addAllUsersRole(roleName):
		logging.info("addAllUsersRole-params: roleName[" + roleName + "]")

		count = 0
		users = c42Lib.getAllUsers()
		for user in users['users']:
			userId = str(user['userId'])
			userName = user['username']
			if (c42Lib.addUserRole(userId, roleName)):
				count = count + 1
				logging.info("Success: userRole[" + userRole + "] added for userId[" + userId + "]:userName[" + userName + "]")
			else:
				logging.info("Fail: userRole[" + userRole + "] added for userId[" + userId + "]:userName[" + userName + "]")

		logging.info("Total Users affected: " + str(count))



	#
	# Remove the role from an individual user. 
	# Note: attempts to remove the role from a user even if the role doesn't exist. 
	#
	@staticmethod
	def removeUserRole(userId, roleName):
		logging.info("removeUserRole-params: userId[" + userId + "]:roleName[" + roleName + "]")

		# headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
		# url = cp_host + ":" + cp_port + cp_api_userRole
		params = {'userId': userId, 'roleName': roleName}
		payload = {}


		# r = requests.delete(url, data=json.dumps(payload), headers=headers)
		r = c42Lib.executeRequest("delete", c42Lib.cp_api_userRole, params, payload)

		logging.debug(r.text)
		logging.debug(r.status_code)

		# Delete was successful with an HTTP return code of 204
		return r.status_code == 204



	#
	# Removes the role for all users within an org
	#
	def removeAllUsersRoleByOrg(orgId, roleName):
		logging.info("removeAllUsersRoleByOrg-params:orgId[" + str(orgId) + "]:roleName[" + roleName + "]")

		count = 0
		users = c42Lib.getAllUsersByOrg(orgId)
		for user in users['users']:
			userId = str(user['userId'])
			userName = user['username']
			if (c42Lib.removeUserRole(userId, userRole)):
				count = count + 1
				logging.info("Success: userRole[" + userRole + "] removeal for userId[" + userId + "]:userName[" + userName + "]")
			else:
				logging.info("Fail: userRole[" + userRole + "] removal for userId[" + userId + "]:userName[" + userName + "]")

		logging.info("Total Users affected: " + str(count))

	#
	# Removes the role for all users
	#
	def removeAllUsersRole(roleName):
		logging.info("removeAllUsersRole-params:roleName[" + roleName + "]")

		count = 0
		users = c42Lib.getAllUsers()
		for user in users['users']:
			userId = str(user['userId'])
			userName = user['username']
			if (c42Lib.removeUserRole(userId, userRole)):
				count = count + 1
				logging.info("Success: userRole[" + userRole + "] removeal for userId[" + userId + "]:userName[" + userName + "]")
			else:
				logging.info("Fail: userRole[" + userRole + "] removal for userId[" + userId + "]:userName[" + userName + "]")

		logging.info("Total Users affected: " + str(count))


	@staticmethod
	def getArchivesPageCount(type, id):
		logging.info("getArchivesPageCount-params:type[" + type + "]:id[" + str(id) + "]")

		validTypes = ['storePointId','serverId','destinationId']
		if (type in validTypes):
			params = {type: str(id), 'pgSize': '1', 'pgNum': '1'}
			payload = {}
			
			r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)

			content = r.content
			binary = json.loads(content)
			logging.debug(binary)

			archives = binary['data']
			totalCount = archives['totalCount']

			logging.info("getArchivesPageCount:totalCount= " + str(totalCount))

			numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)
			logging.info("getArchivesPageCount:numOfRequests= " + str(numOfRequests))

			return numOfRequests

		else:
			return 0



	@staticmethod
	def getArchiveByStorePointId_old(storePointId):
		logging.info("getArchiveByStorePointId-params:storePointId[" + str(storePointId) + "]")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getArchivesPageCount('storePointId',storePointId)

		fullArchiveList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			params = {'storePointId': str(storePointId)}
			pagedArchiveList = getArchivesPaged(params,currentRequestCount)
			fullArchiveList.extend(pagedArchiveList)
		return fullArchiveList

	@staticmethod
	def getArchiveByStorePointId(storePointId):
		logging.info("getArchiveByStorePointId-params:storePointId[" + str(storePointId) + "]")
		currentPage = 1
		keepLooping = True
		fullList = []
		while keepLooping:
			params = {'storePointId': str(storePointId)}
			pagedList = c42Lib.getArchivesPaged(params,currentPage)
			if pagedList:
				fullList.extend(pagedList)
			else:
				keepLooping = False
			currentPage += 1
		return fullList


	@staticmethod
	def getArchiveByServerId_old(serverId):
		logging.info("getArchiveByServerId-params:serverId[" + str(serverId) + "]")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getArchivesPageCount('serverId',serverId)

		fullArchiveList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			params = {'serverId': str(serverId)}
			pagedArchiveList = c42Lib.getArchivesPaged(params,currentRequestCount)
			fullArchiveList.extend(pagedArchiveList)
		return fullArchiveList


	@staticmethod
	def getArchivesByServerId(serverId):
		logging.info("getArchiveByServerId-params:serverId[" + str(serverId) + "]")
		currentPage = 1
		keepLooping = True
		fullList = []
		while keepLooping:
			params = {'serverId': str(serverId)}
			pagedList = c42Lib.getArchivesPaged(params,currentPage)
			if pagedList:
				fullList.extend(pagedList)
			else:
				keepLooping = False
			currentPage += 1
		return fullList



	@staticmethod
	def getArchiveByDestinationId_old(destinationId):
		logging.info("getArchiveByDestinationId-params:destinationId[" + str(destinationId) + "]")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getArchivesPageCount('destinationId',destinationId)

		fullArchiveList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			params = {'destinationId': str(destinationId)}
			pagedArchiveList = c42Lib.getArchivesPaged(params,currentRequestCount)
			fullArchiveList.extend(pagedArchiveList)
		return fullArchiveList

	@staticmethod
	def getArchivesByDestinationId(destinationId):
		logging.info("getArchiveByDestinationId-params:destinationId[" + str(destinationId) + "]")
		currentPage = 1
		keepLooping = True
		fullList = []
		while keepLooping:
			params = {'destinationId': str(destinationId)}
			pagedList = c42Lib.getArchivesPaged(params,currentPage)
			if pagedList:
				fullList.extend(pagedList)
			else:
				keepLooping = False
			currentPage += 1
		return fullList

	@staticmethod
	def getArchiveByGuidAndComputerId(guid, targetComputerId):
		logging.info("getArchiveByGuidAndComputerId-params:guid[" + str(guid) + "]:targetComputerId[" + str(targetComputerId) + "]")

		params = {'guid': str(guid), 'targetComputerId': str(targetComputerId)}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		archives = binary['data']['archives']

		return archives


	@staticmethod
	def getArchivesByUserId(userId):
		logging.info("getArchivesByUserId-params:userId[" + str(userId) + "]")


		# params = {type: str(id), 'pgSize': '1', 'pgNum': '1'}
		# payload = {}
			
		# r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)
		
		params = {'userId': str(userId)}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		archives = binary['data']['archives']

		return archives



	@staticmethod
	def getArchivesPaged(params, pgNum):
		logging.info("getArchivesPaged-params:params[" + str(params) + "]:pgNum[" + str(pgNum) + "]")

		params['pgSize'] = c42Lib.MAX_PAGE_NUM
		params['pgNum'] = pgNum
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		archives = binary['data']['archives']

		return archives


	# @staticmethod
	# def getAllArchives():


	# cp_api_restoreHistory = "/api/restoreHistory"
	#?pgNum=1&pgSize=50&srtKey=startDate&srtDir=desc&days=9999&orgId=35

	@staticmethod
	def getRestoreHistoryForOrgId(orgId):

		return null


	@staticmethod
	def getRestoreHistoryForUserId(userId):

		return null


	@staticmethod
	def getRestoreHistoryForDeviceId(computerId):

		return null
		

	# only 3.6.3.1 and greater - json errors in pervious versions
	# will return array of info for every file within given archive
	# performance is not expected to be great when looking at large archives - impacted by number of files in archive
	# guid is int, decrypt is boolean
	@staticmethod
	def getArchiveMetadata(guid, decrypt):
		logging.info("getArchiveMetadata-params:guid["+str(guid)+"]:decrypt["+str(decrypt)+"]")

		params = {}
		if (decrypt):
			params['decryptPaths'] = "true"
		# always stream the response - remove memory limitation on requests library
		params['stream'] = "True"
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_archiveMetadata + "/" + str(guid), params, payload)

		# logging.debug(r.text)
		#null response on private passwords

		if r.text:
			content = ""
			for chunk in r.iter_content(1024):
				if chunk:
					content = content + chunk
			binary = json.loads(content)
			content = ""
			# may be missing data by doing this call.. 
			# but this means the parcing failed and we can't extract the data
			if 'data' in binary:
				archiveMetadata = binary['data']
				binary = ""
				return archiveMetadata
			else:
				return ""
		else:
			return ""



	# 
	# getServers():
	# returns servers information
	# params:
	# 

	@staticmethod
	def getServers():
		logging.info("getServers")

		params = {}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_server, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		device = binary['data']['servers']
		return device


	# 
	# getServer(serverId):
	# returns server information based on serverId
	# params: serverId
	# 

	@staticmethod
	def getServer(serverId):
		logging.info("getServer-params:serverId["+str(serverId)+"]")

		params = {}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_server + "/" + str(serverId), params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		device = binary['data']
		return device



	# 
	# getServersByDesitnationId(destinationId):
	# returns server information based on destinationId
	# params:
	# destinationId: id of destination
	# 

	@staticmethod
	def getServersByDesitnationId(destinationId):
		logging.info("getServersByDesitnationId-params:destinationId[" + str(destinationId) + "]")

		params = {'destinationId': str(destinationId)}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_server, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		device = binary['data']['servers']
		return device


	#
	# Compute base64 representation of the authentication token.
	#
	@staticmethod
	def getAuthHeader(u,p):

		token = base64.b64encode('%s:%s' % (u,p))

		return "Basic %s" % token

	#
	# Sets logger to file and console
	#
	@staticmethod
	def setLoggingLevel():
		# set up logging to file
		logging.basicConfig(
							# level=logging.DEBUG,
							level = logging.INFO,
							format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
							datefmt='%m-%d %H:%M',
							# filename='EditUserRoles.log',
							filename = str(c42Lib.cp_logFileName),
							filemode='w')
		# define a Handler which writes INFO messages or higher to the sys.stderr
		console = logging.StreamHandler()
		
		if(c42Lib.cp_logLevel=="DEBUG"):
			console.setLevel(logging.DEBUG)
			# console.setLevel(logging.INFO)
		else:
			console.setLevel(logging.INFO)
		
		# set a format which is simpler for console use
		formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
		# tell the handler to use this format
		console.setFormatter(formatter)
		# add the handler to the root logger
		logging.getLogger('').addHandler(console)


	@staticmethod
	def executeCLICommand(payload):
		params = {}
		
		r = c42Lib.executeRequest("post", c42Lib.cp_api_cli, params, payload)

		logging.debug(r.text)
		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		return binary['data']

	# 
	# credit: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
	# 
	@staticmethod
	def sizeof_fmt(num):
		for x in ['bytes','KiB','MiB','GiB']:
			if num < 1024.0 and num > -1024.0:
				return "%3.1f%s" % (num, x)
			num /= 1024.0
		return "%3.1f%s" % (num, 'TiB')



	@staticmethod
	def sizeof_fmt_si(num):
		for x in ['bytes','kB','MB','GB']:
			if num < 1000.0 and num > -1000.0:
				return "%3.1f%s" % (num, x)
			num /= 1000.0
		return "%3.1f%s" % (num, 'TB')




	@staticmethod
	def returnHostAndPortFromFullURL(url):
		p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
		m = re.search(p, str(url))
		
		# address = [m.group('protocol') +''+ m.group('host'),m.group('port')]
		# m.group('host') # 'www.abc.com'
		# m.group('port') # '123'
		# address = [m.group('http')]
		# print address
		return address


# class UserClass(object)


# class OrgClass(object)

# class DeviceClass(object)


