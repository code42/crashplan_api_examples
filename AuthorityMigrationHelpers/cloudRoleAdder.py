# By downloading and executing this software, you acknowledge and agree that Code42 is providing you this software at no
# cost separately from Code42's commercial offerings.  This software is not provided under Code42's master services
# agreement.  It is provided AS-IS, without support, and subject to the license below.  Any support and documentation
# for this software are available at the Code42 community site.
#
# MIT LICENSE
# Copyright (c) 2019 Code42 Software, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# File: cloudRoleAdder.py
# Author: A Orrison, Code42 Software
# Last Modified: 2019-05-01
# Built for Python 3

import requests
import argparse
import getpass
import json
import pandas as pd
import time
import logging
import sys
import os# By downloading and executing this software, you acknowledge and agree that Code42 is providing you this software at no
# cost separately from Code42's commercial offerings.  This software is not provided under Code42's master services
# agreement.  It is provided AS-IS, without support, and subject to the license below.  Any support and documentation
# for this software are available at the Code42 community site.
#
# MIT LICENSE
# Copyright (c) 2019 Code42 Software, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# File: cloudRoleAdder.py
# Author: A Orrison, Code42 Software
# Last Modified: 2019-05-01
# Built for Python 3

import requests
import argparse
import getpass
import json
import pandas as pd
import time
import logging
import sys
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
parser = argparse.ArgumentParser(description='Input for this script')

parser.add_argument('-s',dest='serverUrl',help='Server and port for the server ex: "https://server.url.code42.com:4285"',required=True)
parser.add_argument('-u',dest='username',required=True,help='Username for a SYSADMIN user using local authentication')
parser.add_argument('-e',action='store_true',help='Add this flag to run it for real. Leave out for a dry run')

args = parser.parse_args()
credsUsername = args.username
serverAddress = args.serverUrl
#print ( args.inputFile )
execute = args.e
startTime = time.strftime("%y%m%d%I%M%S",time.localtime(time.time()))
cwd = os.getcwd()

cloudRoles = ["Admin Restore Limited","Admin Restore","Customer Cloud Admin","Desktop User","Org Admin","Org Help Desk","Org Legal Admin","Org Manager","Org Security Viewer","PROe User","Push Restore","Remote File Selection","Security Center User","Alert Emails","Desktop User - No Web Restore","Org Admin - No Web Restore","Cross Org Admin","Cross Org Admin - No Restore","Cross Org Help Desk","Cross Org Legal Admin","Cross Org Manager","Cross Org Security Viewer"]

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout

    def write(self, message):
        self.terminal.write(message)
        with open("cloudRoleAdder-"+startTime+".log", "a") as f:
             f.write(message)

    def flush(self):
        pass
sys.stdout = Logger()

if not execute:
    print ( "This is a dry run. Add the -e flag to run for real.")
else:
    print ("This wil add cloud roles to users \nIf you have second thoughts, or are not ready please quit now. (ctrl+c)")

print ( "Username:\t",credsUsername, "\nServer Address:\t", serverAddress )
userPassword = getpass.getpass(prompt='Please enter your password:')

def genericRequest(requestType,call, params={}, payload={}):
    address= serverAddress+call

    if requestType == 'get':
        r = requests.get(address,auth =(credsUsername,userPassword),params=params, verify=False)
    elif requestType == 'post' and execute:
        r = requests.post(address,auth =(credsUsername,userPassword),data=payload,params=params, verify=False)
    elif requestType == 'put' and execute:
        r = requests.put(address, auth =(credsUsername, userPassword),data=payload, params = params, verify=False)
    elif requestType == 'delete' and execute:
        r = requests.delete(address, auth =(credsUsername, userPassword),data=payload, params = params, verify=False)
    elif not execute:
        r = False
    else:
        print ( 'ERROR: Invalid Request type. Try again' )
        r = False
    return r

def testServerConnectivity():
    try:
        response = genericRequest('get','/api/ping',params={}, payload={})

        content =response.text
        data = json.loads(content)

        if response.status_code ==200 and data['data']['success'] == True:
            print ( "Server is accessible." )
    except:
        print ( serverAddress, "is not available. Please check the server address and try again" )
        exit()

def testCredentials():
    response = genericRequest('get', '/api/user/my?incRoles=True',params={}, payload={})

    content = response.text
    data = json.loads(content)
    if response.status_code == 200:
        print ( "Credentials are good." )
        print ( "\tthis user has the following roles:", data['data']['roles'] )
    else:
        print ( data )
        print ( "Exiting, please try your credentials again." )
        exit()

def getAllUsersByRole(roleId):
    payload = {}
    params = {}
    params['pgSize']=250
    params['pgNum']=1
    params['active']=True
    params['roleId']=roleId
    allUsers = []
    response = genericRequest('get','/api/user', params=params,payload={})
    firstContent = response.text
    firstData = json.loads(firstContent)['data']
    totalUsers = firstData['totalCount']
    pagesNeeded = totalUsers // params['pgSize'] + (totalUsers % params['pgSize'] > 0)
    while params['pgNum'] <= pagesNeeded:
        response = genericRequest('get', '/api/user', params=params, payload={})
        content = response.text
        data = json.loads(content)['data']

        allUsers.extend(data['users'])
        params['pgNum'] += 1

    return allUsers



def createNonExistingCloudRole(newRoleName):
    params = {}
    toSend = {}
    toSend['roleName'] = newRoleName
    toSend['permissions'] = []
    payload = json.dumps(toSend)
    createdRole = genericRequest('post', '/api/role', params=params, payload=payload)
    return createdRole
def getRoles():
    roles = {}
    params = {}
    payload = {}
    request = genericRequest('get','/api/role',params=params,payload=payload)
    allRoles = json.loads(request.content.decode('UTF-8'))['data']

    for eachRole in allRoles:
        thisRole = {}
        numberOfUsers = eachRole['numberOfUsers']

        roleName = eachRole['roleName']
        thisRole['roleId'] = eachRole['roleId']
        thisRole['Number of users'] = numberOfUsers
        thisRole['Name'] = roleName

        permissions = ""
        allPermissions = eachRole['permissions']
        for eachPermission in allPermissions:
            permissions += eachPermission['permission'] + ","
        permissions = permissions[:-1]
        thisRole['Permissions'] = permissions
        default = eachRole['locked']
        if default:
            thisRole['Type'] = "Default"
        else:
            thisRole['Type'] = "Custom"
            rolesReady = False
        if numberOfUsers > 0:
            roles[roleName] = thisRole
    dfRoles = pd.DataFrame(roles, columns=['RoleId', 'Name', 'Number of users', 'Type', 'Permissions'])
    dfRoles.to_csv(cwd+"/"+"AllRoles-"+startTime+".csv",encoding='utf-8',index=False)
    return roles

def addRole(oldRoleName,newRoleName,userId):
    newparams = {}
    toSend = {}
    oldparams = {}
    oldparams['userId'] = userId
    oldparams['roleName']=oldRoleName
    call = '/api/UserRole'
    toSend['userId'] = userId
    toSend['roleName'] = newRoleName
    newPayload = json.dumps(toSend)
    #add the new role to the user
    roleAddRequest = genericRequest('post',call,params=newparams,payload=newPayload)
    return roleAddRequest


testServerConnectivity()
testCredentials()
allRoles = getRoles()
print ( "\nPlease refer to https://support.code42.com/Administrator/Cloud/Monitoring_and_managing/Manage_user_roles to determine what cloud roles you want to map your on premis roles to.\nYou will be using the role name\n\n" )
allResults = []

for eachRole in allRoles:
    if allRoles[eachRole]['Name'] not in cloudRoles:
        oldRoleName = eachRole
        oldRoleId = allRoles[eachRole]['roleId']
        numUsers = allRoles[eachRole]['Number of users']
        waitingForNewRoleName = True
        while waitingForNewRoleName:
            print ( "Please enter the new role name for the",numUsers,"user(s) who currently have", oldRoleName,". Type \"skip\" to skip this role and move onto the next")
            newRoleName = input("")
            if newRoleName != 'skip':
                    print ( "You have chosen\n\tRole name:", newRoleName )
                    for eachCloudRole in cloudRoles:
                        if newRoleName == eachCloudRole:
                            print(newRoleName," is a cloud role")
                            waitingForNewRoleName= False
                    if waitingForNewRoleName == True:
                        print ( "please choose a role present in the cloud." )
            else:
                break
        if newRoleName != 'skip':
            print ( "Adding the role", newRoleName,"for", numUsers, "users with",oldRoleName)

            thisRoleUsers  = getAllUsersByRole(oldRoleId)
            if execute:
                print("Trying to create", newRoleName, "if it does not exist already.")
                wasRoleMade = createNonExistingCloudRole(newRoleName)
                print("Result:",wasRoleMade)
            for user in thisRoleUsers:
                result = {}
                userId = user['userId']
                username = user['username']
                result['User Id'] = userId
                result['Username'] = username
                try:
                    if execute:
                        roleAddRequest = addRole(oldRoleName,newRoleName,userId)
                    if roleAddRequest.status_code ==200:
                        print ( "Added", newRoleName,"successfully for:",username )
                        result['Status'] = 'Success'
                    else:
                        print ( "Did not add", newRoleName,"to:",username )
                        result['Status'] = 'Failure'

                    result['Old Role'] = oldRoleName
                    result['New Role'] = newRoleName

                except:
                    print ( "ERROR failed to add the new role",newRoleName,"for:", username )
                    result['Old Role'] = oldRoleName
                    result['New Role'] = newRoleName
                    result['Status'] = 'Failure'
                allResults.append(result)

dfAllResults = pd.DataFrame(allResults,columns=['User Id','Username','New Role','Old Role','Status'])
failures = dfAllResults.shape[0]-dfAllResults[dfAllResults.Status == 'Success'].shape[0]
if execute:
    print ( "Completed. \nUsers changed:",dfAllResults[dfAllResults.Status == 'Success'].shape[0],"Users with an error:",failures )
else:
    print ( "This was a dry run. Use the -e flag to run for real. All lines in the resulting RolesAddedResults.csv will be marked 'Failure' " )

dfAllResults.to_csv(cwd+"/"+"RolesAddedResults-"+startTime+".csv", encoding='utf-8', index=False)

print ( "Complete" )
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
parser = argparse.ArgumentParser(description='Input for this script')

parser.add_argument('-s',dest='serverUrl',help='Server and port for the server ex: "https://server.url.code42.com:4285"',required=True)
parser.add_argument('-u',dest='username',required=True,help='Username for a SYSADMIN user using local authentication')
parser.add_argument('-e',action='store_true',help='Add this flag to run it for real. Leave out for a dry run')

args = parser.parse_args()
username = args.username
serverAddress = args.serverUrl
#print ( args.inputFile )
execute = args.e
startTime = time.strftime("%y%m%d%I%M%S",time.localtime(time.time()))
cwd = os.getcwd()

cloudRoles = ["Admin Restore Limited","Admin Restore","Customer Cloud Admin","Desktop User","Org Admin","Org Help Desk","Org Legal Admin","Org Manager","Org Security Viewer","PROe User","Push Restore","Remote File Selection","Security Center User","Alert Emails","Desktop User - No Web Restore","Org Admin - No Web Restore","Cross Org Admin","Cross Org Admin - No Restore","Cross Org Help Desk","Cross Org Legal Admin","Cross Org Manager","Cross Org Security Viewer"]

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout

    def write(self, message):
        self.terminal.write(message)
        with open("cloudRoleAdder-"+startTime+".log", "a") as f:
             f.write(message)

    def flush(self):
        pass
sys.stdout = Logger()

if not execute:
    print ( "This is a dry run. Add the -e flag to run for real.")
else:
    print ("This wil add cloud roles to users \nIf you have second thoughts, or are not ready please quit now. (ctrl+c)")

print ( "Username:\t",username, "\nServer Address:\t", serverAddress )
userPassword = getpass.getpass(prompt='Please enter your password:')

def genericRequest(requestType,call, params={}, payload={}):
    address= serverAddress+call

    if requestType == 'get':
        r = requests.get(address,auth =(username,userPassword),params=params, verify=False)
    elif requestType == 'post' and execute:
        r = requests.post(address,auth =(username,userPassword),data=payload,params=params, verify=False)
    elif requestType == 'put' and execute:
        r = requests.put(address, auth =(username, userPassword),data=payload, params = params, verify=False)
    elif requestType == 'delete' and execute:
        r = requests.delete(address, auth =(username, userPassword),data=payload, params = params, verify=False)
    elif not execute:
        r = False
    else:
        print ( 'ERROR: Invalid Request type. Try again' )
        r = False
    return r

def testServerConnectivity():
    try:
        response = genericRequest('get','/api/ping',params={}, payload={})

        content =response.text
        data = json.loads(content)

        if response.status_code ==200 and data['data']['success'] == True:
            print ( "Server is accessible." )
    except:
        print ( serverAddress, "is not available. Please check the server address and try again" )
        exit()

def testCredentials():
    response = genericRequest('get', '/api/user/my?incRoles=True',params={}, payload={})

    content = response.text
    data = json.loads(content)
    if response.status_code == 200:
        print ( "Credentials are good." )
        print ( "\tthis user has the following roles:", data['data']['roles'] )
    else:
        print ( data )
        print ( "Exiting, please try your credentials again." )
        exit()

def getAllUsersByRole(roleId):
    payload = {}
    params = {}
    params['pgSize']=250
    params['pgNum']=1
    params['active']=True
    params['roleId']=roleId
    allUsers = []
    response = genericRequest('get','/api/user', params=params,payload={})
    firstContent = response.text
    firstData = json.loads(firstContent)['data']
    totalUsers = firstData['totalCount']
    pagesNeeded = totalUsers // params['pgSize'] + (totalUsers % params['pgSize'] > 0)
    while params['pgNum'] <= pagesNeeded:
        response = genericRequest('get', '/api/user', params=params, payload={})
        content = response.text
        data = json.loads(content)['data']

        allUsers.extend(data['users'])
        params['pgNum'] += 1

    return allUsers

def createNonExistingCloudRole(newRoleName):
    params = {}
    toSend = {}
    toSend['roleName'] = newRoleName
    toSend['permissions'] = []
    payload = json.dumps(toSend)
    try:
        genericRequest('post', '/api/role', params=params, payload=payload)
    except:
        print ("Did not create role")

def getRoles():
    roles = {}
    params = {}
    payload = {}
    request = genericRequest('get','/api/role',params=params,payload=payload)
    allRoles = json.loads(request.content.decode('UTF-8'))['data']

    for eachRole in allRoles:
        thisRole = {}
        numberOfUsers = eachRole['numberOfUsers']

        roleName = eachRole['roleName']
        thisRole['roleId'] = eachRole['roleId']
        thisRole['Number of users'] = numberOfUsers
        thisRole['Name'] = roleName

        permissions = ""
        allPermissions = eachRole['permissions']
        for eachPermission in allPermissions:
            permissions += eachPermission['permission'] + ","
        permissions = permissions[:-1]
        thisRole['Permissions'] = permissions
        default = eachRole['locked']
        if default:
            thisRole['Type'] = "Default"
        else:
            thisRole['Type'] = "Custom"
            rolesReady = False

        roles[roleName] = thisRole
    dfRoles = pd.DataFrame(roles, columns=['RoleId', 'Name', 'Number of users', 'Type', 'Permissions'])
    dfRoles.to_csv(cwd+"/"+"AllRoles-"+startTime+".csv",encoding='utf-8',index=False)
    return roles

def addRole(oldRoleName,newRoleName,userId):
    newparams = {}
    toSend = {}
    oldparams = {}
    oldPayload = {}
    oldparams['userId'] = userId
    oldparams['roleName']=oldRoleName
    call = '/api/UserRole'
    toSend['userId'] = userId
    toSend['roleName'] = newRoleName
    newPayload = json.dumps(toSend)

    if newRoleName != 'None':
        #add the new role to the user
        newRequest = genericRequest('post',call,params=newparams,payload=newPayload)

testServerConnectivity()
testCredentials()
allRoles = getRoles()
print ( "Please refer to https://support.code42.com/Administrator/Cloud/Monitoring_and_managing/Manage_user_roles to determine what cloud roles you want to map your on premises roles to.\nYou will be using the role name" )
allResults = []

for eachRole in allRoles:
    if allRoles[eachRole]['Name'] not in cloudRoles:
        oldRoleName = eachRole
        oldRoleId = allRoles[eachRole]['roleId']
        numUsers = allRoles[eachRole]['Number of users']
        if numUsers > 0:
            waitingForNewRoleName = True
            while waitingForNewRoleName:
                print ( "Please enter the new role name for users who currently have", oldRoleName,". Type \"skip\" to skip this role and move onto the next")
                newRoleName = input("")
                if newRoleName != 'skip':
                        print ( "You have chosen\n\tRole name:", newRoleName )
                        for eachCloudRole in cloudRoles:
                            if newRoleName == eachCloudRole:
                                waitingForNewRoleName= False
                        else:
                            print ( "please choose a role present in the cloud." )
                else:
                    break
            if newRoleName != 'skip':
                print ( "Adding the role", newRoleName,"for", numUsers, "with",oldRoleName)

                thisRoleUsers  = getAllUsersByRole(oldRoleId)
                for user in thisRoleUsers:
                    result = {}
                    userId = user['userId']
                    username = user['username']
                    result['User Id'] = userId
                    result['Username'] = username
                    try:
                        createNonExistingCloudRole(newRoleName)
                        if execute:
                            print("Creating",newRoleName,"if it does not exist already.")
                        addRole(oldRoleName,newRoleName,userId)
                        print ( "Added", newRoleName,"successfully for:",username )
                        result['Old Role'] = oldRoleName
                        result['New Role'] = newRoleName
                        result['Status'] = 'Success'
                    except:
                        print ( "ERROR failed to add the new role",newRoleName,"for:", username )
                        result['Old Role'] = oldRoleName
                        result['New Role'] = newRoleName
                        result['Status'] = 'Failure'
                    allResults.append(result)
            else:
                print ( "skipping this role" )
dfAllResults = pd.DataFrame(allResults,columns=['User Id','Username','New Role','Old Role','Status'])
failures = dfAllResults.shape[0]-dfAllResults[dfAllResults.Status == 'Success'].shape[0]
if execute:
    print ( "Completed. \nUsers changed:",dfAllResults[dfAllResults.Status == 'Success'].shape[0],"Users with an error:",failures )
else:
    print ( "This was a dry run. Use the -e flag to run for real. All lines in the resulting RolesAddedResults.csv will be marked 'Failure' " )

dfAllResults.to_csv(cwd+"/"+"RolesAddedResults-"+startTime+".csv", encoding='utf-8', index=False)

print ( "Complete" )
