#
# File: c42SharedLibary.py
# Author: AJ LaVenture, Code 42 Software
# Last Modified: 08-21-2013
#
# Common and reused functions to allow for rapid script creation
# 


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
	cp_api_deviceUpgrade = "/api/DeviceUpgrade"
	cp_api_computer = "/api/Computer"
	cp_api_userMoveProcess = "/api/UserMoveProcess"

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
			r = requests.get(url, params=params, data=json.dumps(payload), headers=header)
			logging.debug(r.text)
			return r
		elif type == "delete":
			r = requests.delete(url, params=params, data=json.dumps(payload), headers=header)
			logging.debug(r.text)
			return r
		elif type == "post":
			r = requests.post(url, params=params, data=json.dumps(payload), headers=header)
			logging.debug(r.text)
			return r
		elif type == "put":
			# logging.debug(str(json.dumps(payload)))
			r = requests.put(url, params=params, data=json.dumps(payload), headers=header)
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
	    params = {'active': 'true'}
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
	    params = {'orgId': orgId, 'active': 'true'}
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
	# getUsers(pageNum):
	# Returns list of active users within the system based on page number
	# params:
	# pgNum - page request for user list (starting with 1)
	# 
	@staticmethod
	def getUsers(pgNum):
	    logging.info("getUsers-params:pgNum[" + str(pgNum) + "]")

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
	def getAllUsers():
		logging.info("getAllUsers")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getUsersPageCount()
		fullUserList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			pagedUserList = c42Lib.getUsers(currentRequestCount)
			fullUserList.extend(pagedUserList)
		return fullUserList

	# 
	# getAllUsersByOrg(orgId):
	# Returns json users in single list limited by organization
	# no limit or batching, will return all users within the organization
	# Params:
	# orgId - ID of the organization to query for users
	# 

	@staticmethod
	def getAllUsersByOrg(orgId):
		logging.info("getAllUsersByOrg-params:orgId[" + str(orgId) + "]")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getUsersPageCountByOrg(orgId)
		fullUserList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			pagedUserList = c42Lib.getUsersByOrgPaged(orgId, currentRequestCount)
			fullUserList.extend(pagedUserList)
		return fullUserList


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
			return binary
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
		params = {}
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
	def getAllOrgs():
		logging.info("getAllOrgs")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getOrgPageCount()
		fullOrgList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			pagedOrgList = c42Lib.getOrgs(currentRequestCount)
			fullOrgList.extend(pagedOrgList)
		return fullOrgList

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

		params = {'incCounts': 'true', 'active': 'true'}
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

		params = {'orgId': orgId, 'incCounts': 'true', 'active': 'true'}
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
		params = {'pgNum': str(pgNum), 'pgSize': str(c42Lib.MAX_PAGE_NUM), 'active': 'true', 'incBackupUsage': 'true'}
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
	def getAllDevices():
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
	def getAllDevicesByOrg(orgId):
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
		logging.info("removeAllUsersRoleByOrg-params: orgId[" + str(orgId) + "]:roleName[" + roleName + "]")

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


	# 
	# credit: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
	# 
	@staticmethod
	def sizeof_fmt(num):
		for x in ['bytes','KB','MB','GB']:
			if num < 1024.0 and num > -1024.0:
				return "%3.1f%s" % (num, x)
			num /= 1024.0
		return "%3.1f%s" % (num, 'TB')


# class UserClass(object)


# class OrgClass(object)

# class DeviceClass(object)


