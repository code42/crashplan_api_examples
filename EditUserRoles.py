#
# File: EditUserRoles.py
# Author: Nick Olmsted, Code 42 Software
# Last Modified: 05-21-2013
#
# Adds or Removes a role from all users. If an orgId is specified than only adds/removes from that Org.
# Log file: EditUserRoles.log
#
# Python 2.7
# REQUIRED MODULE: Requests
# http://docs.python-requests.org/en/latest/user/install/
#
# API Call: POST/DELETE api/UserRole
#
# Arguments: orgId, action, userRole, loggingLevel(optional)
#
# Example usages: 
# 1) Delete 'test' role for all users
# python EditUserRoles.py 0 delete test
#
# 2) Add 'test' role to orgId 3 users
# python EditUserRoles.py 3 add test
#
# 3) Delete 'test' role for orgId 4 users in DEBUG mode
# python EditUserRoles.py 3 add test DEBUG
#
# NOTE: Make sure to set cpc_host, cpc_port, cpc_username, cpc_password to your environments values.
# Also make sure the role you are trying to add or remove has been added to your PROe environment. 
# 
import sys

import json

import base64

import logging

import requests

import math

# Set to your environments values
#cp_host = "<HOST OR IP ADDRESS>" ex: http://localhost or https://localhost
#cp_port = "<PORT>" ex: 4280 or 4285
#cp_username = "<username>"
#cp_password = "<pw>"

# Test values
cp_host = "http://localhost"
cp_port = "4280"
cp_username = "admin"
cp_password = "admin"

# REST API Calls
cp_api_userRole = "/api/UserRole"
cp_api_user = "/api/User"

# This number is set to the maximum limit (current ver. 3.5.4) the REST API allows a resultset size to be.
MAX_PAGE_NUM = 250

## ARGUMENTS ##
# ARG1 - ORG ID (Integer) - pass in 0 to make the change to all users
cp_orgId = str(sys.argv[1])

# ARG2 - add/delete userRole
cp_action = str(sys.argv[2])

# ARG3 - userRole
cp_userRole = str(sys.argv[3])

# ARG4 (optional)- logging level for console (default is INFO, add DEBUG for additional output to console)
cp_logLevel = "INFO"
if len(sys.argv)==5:
    cp_logLevel = str(sys.argv[4])

#
# Compute base64 representation of the authentication token.
#
def getAuthHeader(u,p):

    token = base64.b64encode('%s:%s' % (u,p))

    return "Basic %s" % token

#
# Sets logger to file and console
#
def setLoggingLevel():
    # set up logging to file
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='EditUserRoles.log',
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
# Removes the role for all users
#
def removeAllUsersRole(orgId):
    logging.debug("removeAllUsersRole-params: orgId[" + orgId + "]")

    count = 0
    numRequests = getUsersPageCount(orgId)

    # Outer loop for number of user requests
    for x in xrange(1, numRequests+1):
        users = getUsers(orgId, str(x))
        # Inner loop to cycle through each user and remove the role
        for user in users['users']:
            userId = str(user['userId'])
            userName = user['username']
            if (removeUserRole(userId, cp_userRole)):
                count = count + 1
                logging.info("Success: userRole[" + cp_userRole + "] removal for userId[" + userId + "]:userName[" + userName + "]")
            else:
                logging.info("Fail: userRole[" + cp_userRole + "] removal for userId[" + userId + "]:userName[" + userName + "]")

    logging.info("Total Users affected: " + str(count))

#
# Adds a role for all users
#
def addAllUsersRole(orgId):
    logging.debug("addAllUsersRole-params: orgId[" + orgId + "]")

    count = 0
    numRequests = getUsersPageCount(orgId)

    # Outer loop for number of user requests
    for x in xrange(1, numRequests+1):
        users = getUsers(orgId, str(x))
        # Inner loop to cycle through each user and add the role
        for user in users['users']:
            userId = str(user['userId'])
            userName = user['username']
            if (addUserRole(userId, cp_userRole)):
                count = count + 1
                logging.info("Success: userRole[" + cp_userRole + "] added for userId[" + userId + "]:userName[" + userName + "]")
            else:
                logging.info("Fail: userRole[" + cp_userRole + "] added for userId[" + userId + "]:userName[" + userName + "]")

    logging.info("Total Users affected: " + str(count))

#
# Remove the role from an individual user. 
# Note: attempts to remove the role from a user even if the role doesn't exist. 
#
def removeUserRole(userId, roleName):
    logging.debug("removeUserRole-params: userId[" + userId + "]:roleName[" + roleName + "]")

    headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
    url = cp_host + ":" + cp_port + cp_api_userRole
    payload = {'userId': userId, 'roleName': roleName}
    
    r = requests.delete(url, data=json.dumps(payload), headers=headers)

    logging.debug(r.text)
    logging.debug(r.status_code)

    # Delete was successful with an HTTP return code of 204
    return r.status_code == 204

#
# Adds the role to an individual user. 
# Note: attempts to add the role to a user even if it already exists. 
#
def addUserRole(userId, roleName):
    logging.debug("addUserRole-params: userId[" + userId + "]:roleName[" + roleName + "]")

    result = False
    if(userId!=1):
        headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
        url = cp_host + ":" + cp_port + cp_api_userRole
        payload = {'userId': userId, 'roleName': roleName}
    
        r = requests.post(url, data=json.dumps(payload), headers=headers)

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
# Returns a list of users, 
# Params:
# orgId - integer, that is used to limit the users to an org. Can be set to 0 to return all users.
# pgNum - Current page request count. 
#
def getUsers(orgId, pgNum):
    logging.debug("getUsers-params:orgId[" + orgId + "]:pgNum[" + str(pgNum) + "]")

    headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
    url = cp_host + ":" + cp_port + cp_api_user
    payload = {'orgId': orgId, 'pgNum': str(pgNum), 'pgSize': str(MAX_PAGE_NUM)}

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
def getUsersPageCount(orgId):
    logging.debug("getUsersPageCount-params: orgId[" + orgId + "]")

    headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
    url = cp_host + ":" + cp_port + cp_api_user
    payload = {'orgId': orgId}
    
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

#
# Performs the Add or remove user role action.
#
def performUserRoleAction():
    logging.info("User Role Action: " + cp_action)

    orgId = cp_orgId
    if (cp_orgId == "0"):
        orgId = "All Orgs"
    logging.info("Users pulled from OrgId: " + str(orgId))

    if(cp_action == "remove"):
        removeAllUsersRole(cp_orgId)
    elif(cp_action == "add"):
        addAllUsersRole(cp_orgId)
    else:
        logging.error("Invalid second argument value. Please enter remove or add for second argument")

setLoggingLevel()
performUserRoleAction()