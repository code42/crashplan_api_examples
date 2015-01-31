
# File: pushRestore.py
# Author: Amir Kader
# Last Modified: 01/31/2015
#
# This sample uses the WebRestoreSession api to do a push restore
# of a file from a device archive of one computer, sourceComputer,
# to loacation on another computer, targetComputer.
# Make sure to set the values of the following variable in the script (current script doesn't take input params):
#  	- sourceComputer : device name of the source computer you want restore the file from
#	- targetComputer : device name of the target computer you want to push restore to
#	- restoreFile : the path and file name of the file you want to restore
#	- restoreFilePath : the directory location on the target device to push the restore to
#	
# This sample is dependent on the c42SharedLibrary.py
# The c4ShardLibary.py needs to include the variable settings for:
# 	cp_api_webRestoreSession = "/api/WebRestoreSession"
#	cp_api_dataKeyToken = "/api/DataKeyToken"
#	cp_api_pushRestoreJob = "/api/pushRestoreJob"
#
# This script has been tested with 4.x releases of the CODE42 Edge Platform
#

from c42SharedLibrary import c42Lib
import sys
import csv
import getpass
import os
import ntpath
import json

from collections import defaultdict

# Test values
c42Lib.cp_host = "http://demo.code42.com"
c42Lib.cp_port = "4280"

master_cp_host = c42Lib.cp_host
master_cp_port = c42Lib.cp_port

c42Lib.cp_username = "admin"
c42Lib.cp_password = getpass.getpass()
c42Lib.cp_logLevel = "INFO"
c42Lib.cp_logFileName = "pushRestore.log"
c42Lib.setLoggingLevel()

sourceComputer="C02M50TZFH04"
targetComputer="ROBERTS-WIN7"
restoreFile="/Users/amir.kader/Documents/test/amir.png"
restorePath="C:/Users/Robert/Desktop/restore"

print 'calling api/Computer to get guid of target computer: ' + targetComputer 
params = {}
params['q'] = targetComputer
params['active'] = 'true'
payload = {}
r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)
content = r.content
binary = json.loads(content)
targetGUID = binary['data']['computers'][0]['guid'] 
print 'target computers guid: ' + targetGUID

print 'calling api/Computer to get guid of source computer: ' + sourceComputer + '  and serverName...'
params = {}
params['q'] = sourceComputer
params['incBackupUsage'] = 'true'
params['active'] = 'true'
 
payload = {}
r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)
content = r.content
binary = json.loads(content)

computers = binary['data']['computers']
srcGUID = computers[0]['guid']
backupUsage = computers[0]['backupUsage']
serverName = backupUsage[0]['serverName']
#print computers 
print 'source guid: ' + srcGUID
print 'serverName: ' + serverName

print 'calling api/Server?q=' + serverName + ' to get destinationServerGuid...'
params = {}
params['q'] = serverName

r = c42Lib.executeRequest("get", c42Lib.cp_api_server, params, payload)
content = r.content
binary = json.loads(content)
#print binary['data'] 
serverGUID = binary['data']['servers'][0]['guid']
print 'server guid: ' + serverGUID


print 'calling api/DataKeyToken with payload of: '
params = {}
payload = {'computerGuid': srcGUID}
print payload
print ' to get value of dataKeyToken'
r = c42Lib.executeRequest("post", c42Lib.cp_api_dataKeyToken, params, payload)
content = r.content
binary = json.loads(content)
dataKeyToken = binary['data']['dataKeyToken']
print 'dataKeyToken: ' + dataKeyToken

print 'calling api/WebRestoreSession with a payload of : '
params = {}
payload = {'computerGuid': srcGUID, 'dataKeyToken' : dataKeyToken}
print payload
print 'to get value of webRestoreSessionId'
print c42Lib.cp_api_webRestoreSession
r = c42Lib.executeRequest("post", c42Lib.cp_api_webRestoreSession, params, payload)

content = r.content
binary = json.loads(content)
print binary
webRestoreSessionId = binary['data']['webRestoreSessionId']
print 'webRestoreSessionId: ' + webRestoreSessionId
print 'building payload for push restore..'
file1 = [{'type' : "file", 'path' : restoreFile, 'selected': True}]
#print(file1)
payload = {
		'webRestoreSessionId' : webRestoreSessionId, 
		'sourceGuid' : srcGUID, 
		'targetNodeGuid' : serverGUID, 
		'acceptingGuid' : targetGUID, 
		'restorePath' : restorePath,
		'pathSet' : file1, 
		'numBytes' : 1, 
		'numFiles' : 1, 
		'showDeleted' : True, 
		'restoreFullPath': True
}
#print payload
print json.dumps(payload, indent=4)
r = c42Lib.executeRequest("post", c42Lib.cp_api_pushRestoreJob, params, payload)
content = r.content
binary = json.loads(content)
#print json.dumps(binary, indent=4)
restoreID = binary['data']['restoreId']
print "restoreID is: " + restoreID


