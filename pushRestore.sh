#!/bin/bash
#######################################################################################
#
# pushRestore.sh
#
# This example script performs an automated Push Restore (via REST):
#  * One or more source files/directories.
#  * To local or remote destination computer.  To remote directory of choice.
#  * Using MPC or Cloud storage.
#  * Recursive restore (includes subdirectories).
#  * Between computers of different users (if Admin).
#  * ...and more.
#
# Simply edit the variables near the top of this script.
#
# Notes:
#  * Push destination should be running authenticated Crashplan client.
#  * Archive adoption (or original owner) not requried.
# 
# Author: Marc Johnson, Code 42 Software
# Last Modified: 03-02-2014
# 
# --------
#
# Copyright (c) 2014 Code 42 Software
#
# Licensed under the Apache License, Version 2.0 (the “License”); you may not use this 
# file except in compliance with the License. You may obtain a copy of the License at
# 
# www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed 
# under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS 
# OF ANY KIND, either express or implied. See the License for the specific language 
# governing permissions and limitations under the License.
#######################################################################################


###################################
# Local Variables (customize)
###################################

# PROe Master Server
MASTER='https://127.0.01:4285' 

# Restore credentials 
CPLOGIN='admin:admin' 

# Computers (both can be remote and different)
sourceComputer=C02HT6EGF57J
destComputer=C02HT6EGF57J

# Where on destination computer to restore
restorePath='/tmp/mjohnson'

# Add any number of Files or Directories.
# Restore still works if some not in archive.
# Note that Windows systems need "C:/" prepended
getDirs=(
	"/Users/mjohnson/Documents/test"
	"/Users/mjohnson/Documents/Scratch Projects"
)
getFiles=(
	"/Users/mjohnson/Desktop/test.pdf" 
	"/Users/mjohnson/Desktop/test2.pdf"  
	"/Users/mjohnson/Desktop/test3.pdf"
)
# Timeout limit for Web Restore
TIMEOUT=900 #seconds

# Flag to move restored files out of container restore directory.
# Performs additional status monitoring.  Currently only works 
# if script running on destination + MPC.  See below.
DOMOVE=false

###################################
# Helper Functions 
###################################

# API Get
function api {
	echo `curl -sku $CPLOGIN --header "Accept: application/json" "$MASTER/api/${1}?${2}"`
}

# API Post
function apiPost {
	echo `curl -sku $CPLOGIN --header "Content-Type: application/json" -X POST -d "${2}" "$MASTER/api/${1}"`
}

# Json value for given key
function jsonValue {
	echo "${2}" | grep "${1}" | sed 's/^.*"'${1}'":"\([^"]*\)".*$/\1/'
}

###################################
# Setup Session
###################################

echo "Setting up Session..."

# Get source computer info
JSON=`api Computer 'q="'${sourceComputer}'"&incBackupUsage=true&active=true'`
sourceGuid=`jsonValue guid "${JSON}"`
serverName=`jsonValue serverName "${JSON}"`

# If provider node
if [[ "${serverName}" == *ProviderNode* ]]; then
	echo "Detected Public Cloud storage source..."
	destGuid=`echo ${JSON} | sed 's/^.*ProviderMountPoint: node: //; s/".*$//'`
else
	# Get destination data is stored on
	echo "Detected MPC storage source..."
	JSON=`api Server 'q="'${serverName}'"'`
	destGuid=`jsonValue guid "${JSON}"`
fi

# Get accepting computer guid
JSON=`api Computer 'q="'${destComputer}'"&active=true'`
acceptingGuid=`jsonValue guid "${JSON}"`

echo "Getting up Data Key Token..."

# Get Data Key Token
DATA='{"computerGuid":'${sourceGuid}'}'
JSON=`apiPost DataKeyToken "${DATA}"`
dataKeyToken=`jsonValue dataKeyToken "${JSON}"` 

# Get Web Restore Session Id
DATA='{"computerGuid":"'${sourceGuid}'", "dataKeyToken":"'${dataKeyToken}'" }'
JSON=`apiPost WebRestoreSession "${DATA}"`
webRestoreSessionId=`jsonValue webRestoreSessionId "${JSON}"`

###################################
# Build Push Restore
###################################

# Display status and build request
echo "Requesting restore from ${sourceComputer}:"
for var in "${getDirs[@]}" 
do
  echo "			${var}"
  pathJSON=${pathJSON}'{"type":"directory", "path":"'"${var}"'","selected":true},'
done
for var in "${getFiles[@]}" 
do
  echo "			${var}"
  pathJSON=${pathJSON}'{"type":"file", "path":"'"${var}"'","selected":true},'
done
pathJSON="${pathJSON%?}" #remove trailing comma
echo "...Pushed to ${restorePath} on ${destComputer}"

# Payload to POST
DATA='		{ 
		    "webRestoreSessionId":"'${webRestoreSessionId}'", 
		    "sourceGuid":"'${sourceGuid}'", 
		    "targetNodeGuid":"'${destGuid}'", 
		    "acceptingGuid":"'${acceptingGuid}'", 
		    "restorePath":"'"${restorePath}"'",
		    "pathSet":[
		    	'${pathJSON}'
		    ], 
		    "numBytes":1, 
		    "numFiles":1, 
		    "showDeleted":true, 
		    "restoreFullPath":true 
		}'

###################################
# Push Restore
###################################
JSON=`apiPost PushRestoreJob "${DATA}"`
restoreId=`jsonValue restoreId "${JSON}"`

###################################
# Result
###################################
echo
echo "Request / POST: 			${DATA}"
echo 
echo "Response from Server: 	${JSON}"
echo
if [ -z "${restoreId}" ]
then
	echo "Push Restore NOT successful."
	exit
else
	echo "Push Restore successfully submitted and accepted."
	echo "In progress... may take a few minutes."
	echo "Restored files in ${restorePath}"
fi

#################################################
# PERFORM LOCAL MOVE if flag set:
# Move restored files out of container directory.  
# Perform additional status monitoring. 
# Script must be running on destination + MPC.
#################################################
if [ "${DOMOVE}" == "true" ];
then

	###################################
	# Watch RestoreRecord
	###################################
	echo
	echo -n "Monitoring restore progress"
	counter=0
	until [ -z "${JSON}" ] || [[ ${counter} -gt ${TIMEOUT} ]]; do
			sleep 1
		counter=$((counter + 1)) 
		JSON=`api "RestoreRecord/${restoreId}" | grep "not found"`
		echo -n .
	done
	echo

	###################################
	# Move to destination directory
	###################################
	JSON=`api "RestoreRecord/${restoreId}"`
	completedDate=`jsonValue completedDate "${JSON}"`

	if [ -z "${completedDate}" ]
	then
		echo "Push Restore NOT successful.  Timed out."
	else
		echo "Push Restore completed successfully."
		restoreDir=`ls -tr ${restorePath} | grep crashplan-restore | tail -n 1` # todo: timiestamp testing
		if [ -z "${restoreDir}" ]
		then
			echo "Could not find Restore diretory."
		else
			echo "Contents of Restore directory:"
			restoreDir=${restorePath}/${restoreDir}
			find ${restoreDir} | sed s:"${restoreDir}"::

			# move out of temporary container folder (prompt for overwrite)
			sudo mv -i ${restoreDir}/* ${restorePath}
			# sudo rm -rf ${restoreDir}       # optional cleanup temp folder		
			exit
		fi
	fi	
fi
