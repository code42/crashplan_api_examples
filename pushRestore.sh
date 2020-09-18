#!/bin/bash
#######################################################################################
#
# 	Edit the variables near the top of this script then run it!
#	This script is fire and forget, progress is not monitored with this script. That must be done via client or server logs.
#   Usage: ./pushRestore.sh
#
# This example script performs an automated Push Restore (via REST):
#  * One or more source files/directories.
#  * To local or remote destination computer.  To remote directory of choice.
#  * Using MPC or Cloud storage.
#  * Recursive restore (includes subdirectories).
#  * Between computers of different users (if Admin).
#  * Supports restoring to origional location
#  * ...and more.
#
#
# Notes:
#  * Push destination must be running authenticated Code42 client.
#  * Archive adoption (or original owner) not required.
#
# Author: Code 42 Software
# Modified by Jack Phinney, Code42 Software, 9/19/2016
# Modified by Bryan Coe, Code42 Software, 3/7/2017
# Modified by Evan Niessen-Derry, Code42 Software, 3/23/2017
# Modified by Andrew Orrison, Code42 Software, 12/10/2018
#
# --------
#
# # Copyright (c) 2017 Code42, Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#######################################################################################


###################################
# Variables (customize before running)
###################################

# PROe Master Server (e.g. http/4280 or https/4285)
MASTER=''

# Restore credentials
CPUSER=''
read -r -s -p Password: CPPASS
CPLOGIN="$CPUSER:$CPPASS"
echo ""

# Source computer
sourceComputerGuid=

# Accepting computer
acceptingComputerGuid=

# Add any number of Files or Directories, no need to be specific.
# "C:/" or "/" will restore everything that was backed up from the main drive
# Note that Windows systems need "C:/" or other drive letter prepended
getDirs=(
	"C:/"
)
# Example getFiles array. If you'd like to restore only particular files add
# them one per line, quoted, in the getFiles array
#getFiles=(
#	"/Users/example/Desktop/test.pdf"
#	"C:/Users/example/Desktop/test.pdf"
#)
getFiles=()

#Backup date for the restore
#Default date is most recent/when the script is run. That is calculated with: $(date +%Y%m%d)
#Enter date as 'YYYYMMDD' to override
restoreDate=''

# Where on accepting computer to restore
restorePath='C:/pushrestore/'

L1SEC='AccountPassword'
L2SEC='PrivatePassword'
L3SEC='CustomKey'

#Original Location Support
#May be "ORIGINAL_LOCATION" or "TARGET_DIRECTORY" using target directory takes into account the restorePath
pushRestoreStrategy="TARGET_DIRECTORY"
#true or false. default value is "false", 
permitRestoreToDifferentOsVersion=false
#May be "OVERWRITE_ORIGINAL" or "RENAME_ORIGINAL"
existingFiles="RENAME_ORIGINAL"
#May be "CURRENT" or "ORIGINAL"
filePermissions="CURRENT"
###################################
# Helper Functions
###################################

# API Get
function api {
	curl -sku "$CPLOGIN" --header "Accept: application/json" "$MASTER/api/${1}?${2}"
}

# API Post
function apiPost {
	curl -sku "$CPLOGIN" --header "Content-Type: application/json" -X POST -d "${2}" "$MASTER/api/${1}"
}

# Json value for given key
function jsonValue {
	echo "${2}" | grep -o "\"${1}\":\"[^\"]*\"" | sed 's/^.*"'"${1}"'":"\([^"]*\)".*$/\1/'
}


###################################
# Auth Tester
###################################
#Basic check to see if we can authenticate with the server
#This is to prevent account lockout by successive api call failures due to a bad password
#Generic. On error this will output the "description" value
# JSON=$(api Computer 'q="'${sourceComputerGuid}'"')
JSON=$(api Computer/"${sourceComputerGuid}" 'idType=guid&active=true')
if [[ ${sourceComputerGuid} != $(jsonValue guid "${JSON}") ]]; then
	echo Error: "$(jsonValue description "${JSON}")"
	exit 2
fi

userUID=$(jsonValue userUid "$JSON")
JSON=$(api "User/$userUID" "idType=uid&incSecurityKeyType=true")
securityLevel=$(jsonValue securityKeyType "$JSON")

###################################
# Setup Session
###################################

#Perform basic sanity checks on restoreDate
#Set to now if left empty
if [[ ${restoreDate} == '' ]]; then
	restoreDate=$(date +%Y%m%d)
elif [[ ${restoreDate} =~ ^-?[0-9]+$ ]]; then
	if [[ "$restoreDate" -gt $(date +%Y%m%d) ]] || [[ "$restoreDate" -lt 20020507 ]]; then
		echo "Error: date of ${restoreDate} is not within valid range"
		exit 1
	fi
else
	echo "Error: \"${restoreDate}\" is not a valid date"
	exit 1
fi
#convert restoreDate to epoch date with ms (needed for api)
if [[ "$(uname)" = 'Darwin' ]]; then
	restoreDateEpoch=$(date -j -f %Y%m%d "$restoreDate" +%s)
else
	restoreDateEpoch=$(date -d "$restoreDate" +'%s')
fi
restoreDateEpochMS=$(( restoreDateEpoch * 1000 ))

echo -e "Setting up Session...\n"

# Get source computer info
JSON=$(api Computer/"${sourceComputerGuid}" 'idType=guid&incBackupUsage=true&active=true')
sourceComputerName=$(jsonValue name "${JSON}")

# Get backup destination
# If more than one, prompt user to select
IFS=$'\n'
backupDestArray=($(jsonValue serverGuid "${JSON}"))
backupDestCount=${#backupDestArray[@]}
backupDestChosen=false # this is just a string, but substitutes alright for a boolean

if [[ ${backupDestCount} == 1 ]]; then
	backupServerGuid=${backupDestArray[0]}
	backupDestName=$(jsonValue serverName "${JSON}")
elif [[ ${backupDestCount} -gt 1 ]]; then
	backupDestArray+=($(jsonValue serverName "${JSON}"))
	echo -e "Multiple backup destinations found!\n"

	while [[ $backupDestChosen == false ]]; do
		for (( i=0; i<backupDestCount; i++ )); do
			echo $i: "${backupDestArray[i+${backupDestCount}]}"
		done
		# Since we're hinting at a default value, let's set one
		backupDestChoice=1
		read -r -p "Enter destination to restore from (e.g. 1): " backupDestChoiceRaw
		if [[ "$backupDestChoiceRaw" =~ ^[0-9]+$ && $backupDestChoiceRaw -ge 0 && $backupDestChoiceRaw -lt "$backupDestCount" ]]; then
			backupDestChoice=$backupDestChoiceRaw
			backupDestChosen=true
		elif [[ "$backupDestChoiceRaw" =~ ^$ ]]; then
			backupDestChosen=true
		else
			echo -e "\n\"$backupDestChoiceRaw\" is not in the range of possible options; please pick between 0 and $backupDestCount, or hit enter for the default.\n"
		fi
	done

	backupServerGuid=${backupDestArray[${backupDestChoice}]}
else
	echo "Error: No backup destinations found for source device ${sourceComputerName} (${sourceComputerGuid})"
	exit 4
fi
unset IFS

echo -e "Getting Data Key Token...\n"

# Get Data Key Token
DATA='{"computerGuid":'"${sourceComputerGuid}"'}'
JSON=$(apiPost DataKeyToken "${DATA}")
dataKeyToken=$(jsonValue dataKeyToken "${JSON}")

## Get Web Restore Session Id

# When you string a bunch of single and double quotes together, making sure
# they're all correct is extremely difficult, so we're going to use cat and a
# here doc to make this human readable/debuggable

compGuidJSON=$(cat <<EOH
"computerGuid":"${sourceComputerGuid}"
EOH
)

dataKeyTokenJSON=$(cat <<EOH
"dataKeyToken":"${dataKeyToken}"
EOH
)

# Construct the DATA payload based on security level
if [[ $securityLevel == "$L1SEC" ]]; then
	DATA=$(cat <<-EOH
	{$compGuidJSON,$dataKeyTokenJSON}
EOH
)
elif [[ $securityLevel == "$L2SEC" ]]; then
	read -r -s -p "Archive Password: " archivePassword
	echo ""
	DATA=$(cat <<-EOH
	{$compGuidJSON,$dataKeyTokenJSON,"privatePassword":"$archivePassword"}
EOH
)
elif [[ $securityLevel == "$L3SEC" ]]; then
	read -r -s -p "Archive Encryption Key: " archiveEncKey
	echo ""
	DATA=$(cat <<-EOH
	{$compGuidJSON,"encryptionKey":"$archiveEncKey"}
EOH
)
fi

# Get the restore session id
JSON=$(apiPost WebRestoreSession "${DATA}")
webRestoreSessionId=$(jsonValue webRestoreSessionId "${JSON}")

###################################
# Build Push Restore
###################################

# Display status and build request
echo "Requesting restore from ${sourceComputerGuid} ($sourceComputerName):"
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
echo "...Pushed to ${restorePath} on ${acceptingComputerGuid}"

# Payload to POST
DATA='{
	"webRestoreSessionId":"'${webRestoreSessionId}'",
	"sourceGuid":"'${sourceComputerGuid}'",
	"targetNodeGuid":"'${backupServerGuid}'",
	"acceptingGuid":"'${acceptingComputerGuid}'",
	"restorePath":"'"${restorePath}"'",
	"pathSet":[
		'${pathJSON}'
	],
	"numBytes":1,
	"numFiles":1,
	"showDeleted":true,
	"restoreFullPath":true,
	"timestamp":'${restoreDateEpochMS}',
	"pushRestoreStrategy":'${pushRestoreStrategy}',
	"permitRestoreToDifferentOsVersion":'${permitRestoreToDifferentOsVersion}',
	"existingFiles":'${existingFiles}',
	"filePermissions":'${filePermissions}'
	
}'

###################################
# Push Restore
###################################
JSON=$(apiPost PushRestoreJob "${DATA}")
restoreId=$(jsonValue restoreId "${JSON}")

###################################
# Result
###################################
echo
echo "Request / POST: 			${DATA}"
echo
echo "Response from Server: 	${JSON}"
echo
if [[ -z "${restoreId}" ]]
then
	echo "Push Restore NOT successful."
	exit
else
	echo "Push Restore successfully submitted and accepted."
	echo "In progress... may take a few minutes."
	echo "Restored files in ${restorePath}"
fi
