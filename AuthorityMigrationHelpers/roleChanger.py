# The MIT License (MIT)
# Copyright (c) 2018 Code42

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
# File: roleChanger.py
# Author: A Orrison, Code42 Software
# Last Modified: 2018-10-29
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


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout

    def write(self, message):
        self.terminal.write(message)
        with open("usernameToEmailChange-"+startTime+".log", "a") as f:
             f.write(message)

    def flush(self):
        pass
sys.stdout = Logger()

if not execute:
    print ( "This is a dry run. Add the -e flag to run for real.")
else:
    print ("This wil change roles on your system if you continue\nIf you have second thoughts, or are not ready please quit now. (ctrl+c)")

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
        dfRoles = pd.DataFrame(roles, columns=['Role Id', 'Name', 'Number of Users', 'Type', 'Ready', 'Permissions'])
        dfRoles.to_csv(cwd+"/"+"AllRoles-"+startTime+".csv",encoding='utf-8',index=False)
    return roles

def changeRole(oldRoleName,newRoleName,userId):
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

    #remove the old role from the user"
    oldRequest = genericRequest('delete',call,params=oldparams,payload=oldPayload)
    if newRoleName != 'None':
        #add the new role to the user
        newRequest = genericRequest('post',call,params=newparams,payload=newPayload)

testServerConnectivity()
testCredentials()
allRoles = getRoles()
print ( "Please refer to AllRoles.csv (exported by this script), or the roles page in console to determine what default roles you want to map your custom roles to.\nYou will be using the role name" )
allResults = {}

for eachRole in allRoles:
    if allRoles[eachRole]['Type'] == 'Custom':
        oldRoleName = eachRole
        oldRoleId = allRoles[eachRole]['roleId']
        numUsers = allRoles[eachRole]['Number of users']
        while True:
            print ( "Please enter the new role name for users who currently have", oldRoleName,". Type \"skip\" to skip this role and move onto the next, type \"None\" to remove this role from the users" )
            newRoleName = input("")
            if newRoleName != 'skip' or newRoleName !='None':
                try:
                    newRoleType = allRoles[newRoleName]['Type']
                    newRoleId = allRoles[newRoleName]['roleId']
                    print ( "You have chosen\n\tRole name:", newRoleName )
                    if newRoleType == 'Default':
                        break
                    else:
                        print ( "please choose a default role." )
                except:
                    print ( "Please choose a valid role name" )
            else:
                break
        if newRoleName != 'skip':
            print ( "Removing the role", oldRoleName,"for", numUsers, "Replacing with", newRoleName )

            thisRoleUsers  = getAllUsersByRole(oldRoleId)
            for user in thisRoleUsers:
                result = {}
                userId = user['userId']
                username = user['username']
                result['User Id'] = userId
                result['Username'] = username
                try:
                    changeRole(oldRoleName,newRoleName,userId)
                    print ( "changed roles from ",oldRoleName, "to", newRoleName,"successfully for:",username )
                    result['Old Role'] = oldRoleName
                    result['New Role'] = newRoleName
                    result['Status'] = 'Success'
                except:
                    print ( "ERROR failed to change roles from ",oldRoleName, "to", newRoleName, "for:", username )
                    result['Old Role'] = oldRoleName
                    result['New Role'] = newRoleName
                    result['Status'] = 'Failure'
                allResults.append(result)
        else:
            print ( "skipping this role" )
dfAllResults = pd.DataFrame(allResults,columns=['User Id','Username','New Role','Old Role','Status'])

if execute:
    print ( "Completed. \nUsers changed:",len(dfAllResults[allResults.Status == 'Success']),"Users with an error:",len(dfAllResults[allResults.Status == 'Failure']) )
else:
    print ( "This was a dry run. Use the -e flag to run for real. All lines in the resulting RolesChangedResults.csv will be marked 'Failure' " )

dfAllResults.to_csv(cwd+"/"+"RolesChangedResults-"+startTime+".csv", encoding='utf-8', index=False)

print ( "Complete" )
