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

	@staticmethod
	def getRequestHeaders():
		header = {"Authorization":c42Lib.getAuthHeader(c42Lib.cp_username,c42Lib.cp_password), "Content-Type": "application/json"}
		# print header
		return header

	@staticmethod
	def getRequestUrl(cp_api):
		url = c42Lib.cp_host + ":" + c42Lib.cp_port + cp_api
		return url

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


	@staticmethod
	def getUsersPageCount():
	    logging.debug("getUsersPageCount")

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

	    logging.debug("getUsersPageCount:totalCount= " + str(totalCount))

	    # num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
	    numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)

	    logging.debug("getUsersPageCount:numOfRequests= " + str(numOfRequests))
	   
	    return numOfRequests

	# 
	# Gets the number of page requests needed to return all users within an org.
	# Note: This is used because of the current REST API resultset limit of 250 results.
	#
	@staticmethod
	def getUsersPageCountByOrg(orgId):
	    logging.debug("getUsersPageCountByOrg-params: orgId[" + str(orgId) + "]")

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

	    logging.debug("getUsersPageCountByOrg:totalCount= " + str(totalCount))

	    # num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
	    numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)

	    logging.debug("getUsersPageCountByOrg:numOfRequests= " + str(numOfRequests))
	   
	    return numOfRequests


	@staticmethod
	def getUserById(userId):
		logging.debug("getUser-params:userId[" + str(userId) + "]")

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
	# Returns a list of users, 
	# Params:
	# orgId - integer, that is used to limit the users to an org. Can be set to 0 to return all users.
	# pgNum - Current page request count. 
	# active - only return active users
	#
	@staticmethod
	def getUsersByOrgPaged(orgId, pgNum):
	    logging.debug("getUsersByOrgPaged-params:orgId[" + str(orgId) + "]:pgNum[" + str(pgNum) + "]")

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

	@staticmethod
	def getUsers(pgNum):
	    logging.debug("getUsers-params:pgNum[" + str(pgNum) + "]")

	    # headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
	    # url = cp_host + ":" + cp_port + cp_api_user
	    params = {'pgNum': str(pgNum), 'pgSize': str(c42Lib.MAX_PAGE_NUM), 'active': 'true'}
	    payload = {}

	    # r = requests.get(url, params=payload, headers=headers)
	    r = c42Lib.executeRequest("get", c42Lib.cp_api_user, params, payload)

	    logging.debug(r.text)
	    
	    content = r.content
	    binary = json.loads(content)
	    logging.debug(binary)

	    users = binary['data']['users']
	    return users



	@staticmethod
	def getAllUsers():
		logging.debug("getAllUsers")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getUsersPageCount()
		fullUserList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			pagedUserList = c42Lib.getUsers(currentRequestCount)
			fullUserList.extend(pagedUserList)
		return fullUserList



	@staticmethod
	def getAllUsersByOrg(orgId):
		logging.debug("getAllUsersByOrg-params:orgId[" + str(orgId) + "]")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getUsersPageCountByOrg(orgId)
		fullUserList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			pagedUserList = c42Lib.getUsersByOrgPaged(orgId, currentRequestCount)
			fullUserList.extend(pagedUserList)
		return fullUserList


	@staticmethod
	def putUserUpdate(userId, payload):
		logging.debug("putUserUpdate-params:userId[" + str(userId) + "],payload[" + str(payload) + "]")

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



	@staticmethod
	def postUserMoveProcess(userId, orgId):
		logging.debug("postUserMoveProcess-params:userId[" + str(userId) + "],orgId[" + str(orgId) + "]")

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


	@staticmethod
	def getOrg(orgId):
		logging.debug("getOrg-params:orgId[" + str(orgId) + "]")

		params = {'incAll': 'true'}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_org + "/" + str(orgId), params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		org = binary['data']
		return org


	@staticmethod
	def getOrgs(pgNum):
		logging.debug("getOrgs-params:pgNum[" + str(pgNum) + "]")

		params = {'pgNum': str(pgNum), 'pgSize': str(c42Lib.MAX_PAGE_NUM)}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_org, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		orgs = binary['data']
		return orgs

	@staticmethod
	def getOrgPageCount():
		logging.debug("getOrgPageCount")
		params = {}
		payload = {}
		r = c42Lib.executeRequest("get", c42Lib.cp_api_org, params, payload)

		logging.debug(r.text)
		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		orgs = binary['data']
		totalCount = orgs['totalCount']

		logging.debug("getOrgPageCount:totalCount= " + str(totalCount))

		# num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
		numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)

		logging.debug("getOrgPageCount:numOfRequests= " + str(numOfRequests))

		return numOfRequests

	@staticmethod
	def getAllOrgs():
		logging.debug("getAllOrgs")

		currentRequestCount = 0
		numberOfRequests = c42Lib.getOrgPageCount()
		fullOrgList = []
		while (currentRequestCount <= numberOfRequests):
			currentRequestCount += 1
			pagedOrgList = c42Lib.getOrgs(currentRequestCount)
			fullOrgList.extend(pagedOrgList)
		return fullOrgList


	@staticmethod
	def getDeviceByGuid(guid):
		logging.debug("getDeviceByGuid-params:guid[" + str(guid) + "]")

		params = {'incBackupUsage': 'true', 'guid': str(guid)}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		device = binary['data']
		return device


	@staticmethod
	def getDeviceById(computerId):
		logging.debug("getDeviceById-params:computerId[" + str(computerId) + "]")

		params = {'incBackupUsage': 'true'}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer + "/" + str(computerId), params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		device = binary['data']
		return device


	@staticmethod
	def getDevicesPageCount():
		logging.debug("getDevicesPageCount")

		params = {'incCounts': 'true', 'active': 'true'}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)


		devices = binary['data']
		totalCount = devices['totalCount']

		logging.debug("getDevicesPageCount:totalCount= " + str(totalCount))

		# num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
		numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)

		logging.debug("getDevicesPageCount:numOfRequests= " + str(numOfRequests))

		return numOfRequests

	@staticmethod
	def getDevicesPageCountByOrg(orgId):
		logging.debug("getDevicesPageCountByOrg-params:orgId[" + str(orgId) + "]")

		params = {'orgId': orgId, 'incCounts': 'true', 'active': 'true'}
		payload = {}

		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		devices = binary['data']
		totalCount = devices['totalCount']

		logging.debug("getDevicesPageCountByOrg:totalCount= " + str(totalCount))

		# num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
		numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)

		logging.debug("getDevicesPageCountByOrg:numOfRequests= " + str(numOfRequests))

		return numOfRequests

	@staticmethod
	def getDevices(pgNum):
		logging.debug("getDevices-params:pgNum[" + str(pgNum) + "]")

		# headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
		# url = cp_host + ":" + cp_port + cp_api_user
		params = {'pgNum': str(pgNum), 'pgSize': str(c42Lib.MAX_PAGE_NUM), 'active': 'true'}
		payload = {}

		# r = requests.get(url, params=payload, headers=headers)
		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		devices = binary['data']['computers']
		return devices



	@staticmethod
	def getDevicesByOrgPaged(orgId, pgNum):
		logging.debug("getDevicesByOrgPaged-params:orgId[" + str(orgId) + "]:pgNum[" + str(pgNum) + "]")

		# headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
		# url = cp_host + ":" + cp_port + cp_api_user
		params = {'orgId': orgId, 'pgNum': str(pgNum), 'pgSize': str(c42Lib.MAX_PAGE_NUM), 'active': 'true'}
		payload = {}

		# r = requests.get(url, params=payload, headers=headers)
		r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

		logging.debug(r.text)

		content = r.content
		binary = json.loads(content)
		logging.debug(binary)

		devices = binary['data']['computers']
		return devices



	@staticmethod
	def getAllDevices():
		logging.debug("getAllDevices")

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
		logging.debug("getAllDevicesByOrg-params:orgId[" + str(orgId) + "]")

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
		logging.debug("putDeviceUpgrade-params:computerId[" + str(computerId) + "]")

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
		logging.debug("addUserRole-params: userId[" + userId + "]:roleName[" + roleName + "]")

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
		logging.debug("addAllUsersRoleByOrg-params: orgId[" + str(orgId) + "]:userRole[" + roleName + "]")

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
		logging.debug("addAllUsersRole-params: roleName[" + roleName + "]")

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
		logging.debug("removeUserRole-params: userId[" + userId + "]:roleName[" + roleName + "]")

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
		logging.debug("removeAllUsersRoleByOrg-params: orgId[" + str(orgId) + "]:roleName[" + roleName + "]")

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
		logging.debug("removeAllUsersRole-params:roleName[" + roleName + "]")

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
							level = logging.DEBUG,
							format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
							datefmt='%m-%d %H:%M',
							# filename='EditUserRoles.log',
							filename = str(c42Lib.cp_logFileName),
							filemode='w')
		# define a Handler which writes INFO messages or higher to the sys.stderr
		console = logging.StreamHandler()
		
		if(c42Lib.cp_logLevel=="DEBUG"):
			console.setLevel(logging.DEBUG)
		else:
			console.setLevel(logging.INFO)
		
		# set a format which is simpler for console use
		formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
		# tell the handler to use this format
		console.setFormatter(formatter)
		# add the handler to the root logger
		logging.getLogger('').addHandler(console)




# class UserClass(object)


# class OrgClass(object)

# class DeviceClass(object)


