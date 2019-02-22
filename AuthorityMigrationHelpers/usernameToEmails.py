# The MIT License (MIT)
# Copyright (c) 2019 Code42

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
# File: usernameToEmails.py
# Author: A Orrison, Code42 Software
# Last Modified: 2019-2-19
# Built for python 3
#################### TO do: 1. Get rid of insecure warning when running, add option to only do one org, users with blank email address not incremented for failure.

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
# Force UTF-8, only on Macs
#reload(sys)
#sys.setdefaultencoding('utf-8')

parser = argparse.ArgumentParser(description='Input for this script')

parser.add_argument('-s',dest='serverUrl',help='Server and port for the server ex: "https://server.url.code42.com:4285"',required=True)
parser.add_argument('-u',dest='username',required=True,help='Username for a SYSADMIN user using local authentication')
parser.add_argument('--method',dest='method',required=True,type=int,choices=[1,2,3,4],help="Select which method you want to use for changing usernames to email addresses. 1=Make user's email their username.2=username@domain.com 3=first.last@domain.com. 4=Check to see if all usernames are emails")
parser.add_argument('-e',action='store_true',help='Add this flag to run it for real. Leave out for a dry run')
parser.add_argument('-f',dest='inputFile',type=argparse.FileType('r'),help='File that contains just the userIds you want to alter')

args = parser.parse_args()
method = args.method
username = args.username
serverAddress = args.serverUrl
#print (args.inputFile )
filename = args.inputFile
execute = args.e
startTime = time.strftime("%y%m%d%I%M%S",time.localtime(time.time()))

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
    print ("This is a dry run. Add the -e flag to run for real." )
else:
    print ("BE AWARE, THIS WILL CHANGE ALL USERNAMES ON YOUR SYSTEM TO EMAIL ADDRESSES\nIf you have second thoughts, or are not ready please quit now. (ctrl+c)")

if method >1 and method < 4:
    while True:
        print ("Please enter the domain for your users ex: @example.com")
        domain = input()
        if '@' in domain:
            break
        else:
            print ("Double check the domain for an @ symbol and try again. You entered:",domain )
    print ("Domain:\t\t",domain)
print ("Username:\t",username, "\nServer Address:\t", serverAddress,"\nMethod:\t\t",method)
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
            print ("Server is accessible." )
    except:
        print (serverAddress, "is not available. Please check the server address and try again" )
        sys.exit()

def testCredentials():
    response = genericRequest('get', '/api/user/my?incRoles=True',params={}, payload={})

    content = response.text
    data = json.loads(content)
    if response.status_code == 200:
        print ("Credentials are good." )
        print ("\tthis user has the following roles:", data['data']['roles'] )
    else:
        print (data )
        print ("Exiting, please try your credentials again." )
        sys.exit()

def getAllUsers():
    payload = {}
    params = {}
    params['pgSize']=250
    params['pgNum']=1
    #params['active']=False
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

def usernameIsEmail(username):
    try:
        usernameTest = username.split("@")
        if len(usernameTest) == 2:
            return True
        else:
            return False
    except:
        return False

def checkIfUsernamesAreEmailAddresses(allUsers):
    if os.path.exists("usernamesNotemailAddresses.csv"):
        os.remove("usernamesNotemailAddresses.csv")
    notCorrectUsers = []
    for eachUser in allUsers:
        if not usernameIsEmail(eachUser['username']):
            notCorrectUsers.append(eachUser)
            content = str(eachUser['userId'])+","+ eachUser['username']+"\n"
            with open("usernamesNotemailAddresses.csv", "a") as text_file:
                text_file.write(content)
                text_file.close()

testServerConnectivity()
testCredentials()

allUsers = getAllUsers()

dfAllUsersToProcess =  pd.DataFrame(allUsers,columns=['userId','userUid','active','username','email','firstName','lastName'])
dfAllUsersToProcess['Old Username'] = dfAllUsersToProcess['username']

if method == 1:
    dfAllUsersToProcess['username'] = dfAllUsersToProcess['email']
elif method ==2:
    dfAllUsersToProcess['username'] = dfAllUsersToProcess['username'] + domain
elif method == 3:
    dfAllUsersToProcess['username'] = dfAllUsersToProcess['firstName'] + '.' + dfAllUsersToProcess['lastName'] + domain
elif method == 4:
    checkIfUsernamesAreEmailAddresses(allUsers)
    print ("Users without email addresses have been printed to usernamesNotEmailAddresses.csv")
    sys.exit()


#dfAllUsersToProcess = dfAllUsersToProcess.fillna('empty')

if args.inputFile:
    lines = filename.read().splitlines()
    dfAllUsersToProcess = dfAllUsersToProcess[dfAllUsersToProcess['userId'].isin(lines)]
else:
    print ("Processing all users." )
#print (dfAllUsersToProcess.to_string() )
#Check to see if there are any users that don't have an @ symbol in their username.
#If this is the case something is not right, and needs to be fixed.
#If this is the case something is not right, and needs to be fixed.

allResults = []
for index, row in dfAllUsersToProcess.iterrows():
    result = {}
    newUsername = row['username']
    oldUsername  = row['Old Username']
    userId = row['userId']

    result['User Id'] = userId
    result['New Username'] = newUsername
    result['Old Username'] = oldUsername

    call = '/api/user/' + str(userId)
    toSend = {}
    toSend['email'] = newUsername
    toSend['username'] = newUsername
    payload = json.dumps(toSend)
    attemptStatus=""
    singleQuote='\''
    if usernameIsEmail(newUsername):
        if usernameIsEmail(oldUsername):
            print("Did not change", oldUsername + " to ", newUsername, "it is already an email address.")
            attemptStatus = ", username is already an email address"
        elif newUsername == oldUsername:
            print ("Did not change", oldUsername + " to ", newUsername, "it is already the same.")
            attemptStatus = ", already Set to Username"
        elif singleQuote in newUsername :
            print ("Did not change",oldUsername+" to ",newUsername,"it has a single quote in it. Please manually change username to an email address.")
            attemptStatus=", ' in email address."
        elif not username==oldUsername:
            response = genericRequest('put', call, params={}, payload=payload)
        else:
            print ("Did not change",oldUsername+" to ",newUsername,"This is the user running this script.")
            attemptStatus= ", username used for script"
    else:
        print("Did not change", oldUsername + " to ", newUsername, "It is not a valid email address.")
        attemptStatus = ", new username not a valid email address"
    try:
        if (response.status_code != 200):
            print (response.text )
            result['Status'] = 'Failure'
            print (payload )
        else:
            print ("Changed",oldUsername+" to",newUsername )
            result['Status'] = 'success'
    except :

        if not execute and attemptStatus == "":
            result['Status'] = 'Dry run Success'
        else:
            result['Status'] = 'Failure'+attemptStatus

        try:
            print (response.text )
        except:
            None

    allResults.append(result)
dfAllResults = pd.DataFrame(allResults,columns=['User Id','New Username','Old Username','Status'])
failures = dfAllResults.shape[0]-dfAllResults[dfAllResults.Status == 'Success'].shape[0]
if execute:
    print ("Completed. \nUsers changed:",dfAllResults[dfAllResults.Status == 'Success'].shape[0],"Users with an error:",failures )
else:
    print ("This was a dry run. Use the -e flag to run for real.")

#print (dfAllResults.to_string())
dfAllResults.to_csv('UsernamesChangedResults-'+startTime+'.csv', encoding='utf-8', index=False)
