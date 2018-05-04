# Copyright (c) 2016 Code42, Inc.
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

#!/bin/bash 
#
# usage:  SearchCheckum.sh
#
#   This program searches CrashPlan Archives for directories and files with a specific MD5 checksum. It was adapted from SearchPath.sh
#   
#
# Created: by Jeff Dugan 12/9/14 (original version is named SearchPath.sh )
# Modified and adapted by Todd Ojala 2/5/2015
# Version Info
# V1.0 - Base Script - Jeff Dugan - 12/9/14
# V1.1 - Added case sensitivity logic and accounted for spaces in string - Kyle Hatelstad - 12/22/14
# V2.0 - Adapted to use the storePoint and server resources, to reflect our changed data model. This version also searches for MD5 checksums rather than an arbitrary
#	 string in the file path. See the updated SearchPath.sh for the ability to search for an arbitrary string in the pathname. - Todd Ojala - 2/5/2015


echo "*************************************************************"
echo "——————————————————————————Code42—————————————————————————————"
echo "This is an unofficial script that is not supported."
echo "Feel free to modify and use as you see fit."
echo "*************************************************************"
echo ""
echo "*************************************************************"
echo "———————————————————————SearchChecksum.sh—————————————————————————"
echo "This script searches CrashPlan Archives for directories and"
echo "files with a specific MD5 checksum."
echo "Output is directed to the folder the script is run in."
echo "It is designed for Private Deployments only."
echo "*************************************************************"
echo ""
echo ""


# Collect Master Appliance info

echo "Enter Your Master Server IP"
read MASTER

echo "Enter Your Master Server Management Port"
read PORT


#Set HTTP: or HTTPS:
if [ "$PORT" == "4280" ]
	then
		PROTOCOL="http"
	else
		PROTOCOL="https"
fi

# Collect User info to connect to perform search
echo "Enter Your UserID"
read C42UID

echo "Enter your Password"
read -s C42PASS

echo "Enter the MD5 checksum to search for:"
read CHECKSUM	


echo "At which level would you like to search.  all, org, device?"
read LEVEL

#Set timestamp for Filename
TIMESTAMP=$(date +"%Y%m%d%H%M%S")



#Gather computer guids at the appropriate level.	
case $LEVEL in
	org)
		#Gather ORG Registration to determine Organization ID
		echo "Enter Organization Registration Key XXXX-XXXX-XXXX-XXXX" 
		read ORGREG
		ORGID=$(curl -sku $C42UID:$C42PASS "$PROTOCOL://$MASTER:$PORT/api/Org?q=$ORGREG" | python -mjson.tool | grep orgId | tr -cd '[:digit:]')

		#Use Organization ID to get a list of all guids of service type CrashPlan in the given Org.
		TEMP=$(curl -sku $C42UID:$C42PASS "$PROTOCOL://$MASTER:$PORT/api/computer?orgId=$ORGID" | python -mjson.tool | grep 'guid\|service' | awk -F "\"" '{print $4}')
		TEMPARRAY=($TEMP)
		COUNT=0
		INDEX=0
		while [ $COUNT -lt ${#TEMPARRAY[@]} ]
		do
			if [ ${TEMPARRAY[COUNT+1]} == "CrashPlan" ]
			
			then	
				ARRAY[$INDEX]=${TEMPARRAY[COUNT]}
				INDEX=$(($INDEX + 1))
			fi
			COUNT=$(($COUNT + 2))
		done		
		
		#Set Filename
		FILENAME=("SearchPath_Org_""$ORGID""_""$TIMESTAMP"".csv")
		;;
		
	all) 
		#Get a list of all guids of service type CrashPlan.
		TEMP=$(curl -sku $C42UID:$C42PASS "$PROTOCOL://$MASTER:$PORT/api/computer" | python -mjson.tool | grep 'guid\|service' | awk -F "\"" '{print $4}')
		TEMPARRAY=($TEMP)
		
		COUNT=0
		INDEX=0
		while [ $COUNT -lt ${#TEMPARRAY[@]} ]
		do
			if [ ${TEMPARRAY[COUNT+1]} == "CrashPlan" ]
			
			then	
				ARRAY[$INDEX]=${TEMPARRAY[COUNT]}
				INDEX=$(($INDEX + 1))
			fi
			COUNT=$(($COUNT + 2))
		done		
		
		#Set Filename
		FILENAME=("SearchPath_Org_all_""$TIMESTAMP"".csv")		
		;;
		
	device) 
		echo "Enter Device GUID" 
		read DEVICE
		ARRAY=$DEVICE
		#ARRAY=662507403751203534
		
		#Set Filename
		FILENAME=("SearchPath_GUID_""$DEVICE""_""$TIMESTAMP"".csv")
		;;
		
	*) 
		echo "INVALID OPTION. Only all, org and device accepted." 
		exit 1
		;;
esac

#List Header
echo "USERNAME,USERID,COMPUTERNAME,GUID,PATH" >> $FILENAME
 
COUNT=0
HITS=0
while [ $COUNT -lt ${#ARRAY[@]} ]
do

	#get Username + UserID from computer guid
	DEVICE=${ARRAY[COUNT]}
	USERINFO=$(curl -sku $C42UID:$C42PASS "$PROTOCOL://$MASTER:$PORT/api/computer/$DEVICE?idType=guid" | python -mjson.tool)
	USERID=$(echo "$USERINFO" | grep '"userId":' | tr -cd '[:digit:]')
	USERNAME=$(curl -sku $C42UID:$C42PASS "$PROTOCOL://$MASTER:$PORT/api/user/$USERID" | python -mjson.tool | grep '"username":')
	USERNAME=$(echo ${USERNAME##*:})
	USERNAME=$(echo ${USERNAME#\"})
	USERNAME=$(echo ${USERNAME%\"\,})		
		
	#get Computername from computer guid
	COMPNAME=$(echo "$USERINFO" | grep '"name":')
	COMPNAME=$(echo ${COMPNAME##*:} | tr -cd '[:alnum:]')

	#get archiveGuid from computer guid using Archive resource, as you can no longer go directly to ArchiveMetadata with a computer guid (Todd 1/27/2015)
	ARCHIVE_CALL=$(curl -sku $C42UID:$C42PASS "$PROTOCOL://$MASTER:$PORT/api/archive?backupSourceGuid=$DEVICE")
	ARCHIVE=$(echo $ARCHIVE_CALL | python -mjson.tool | grep '"archiveGuid":')
	ARCHIVE=$(echo ${ARCHIVE##*:})
	ARCHIVE=$(echo ${ARCHIVE#\"})
	ARCHIVE=$(echo ${ARCHIVE%\"\,})

	#Get the storePointId from the Archive resource. It does not make another call to the Archive resource, but extracts from the variable ARCHIVE_CALL above
	STOREPOINT=$(echo $ARCHIVE_CALL | python -mjson.tool | grep '"storePointId":')
	STOREPOINT=$(echo ${STOREPOINT##*:})
	STOREPOINT=$(echo ${STOREPOINT%\,})

	#Get the ServerId using the storePoint resource (using the storePointId acquired in the previous section)
  	SERVER=$(curl -sku $C42UID:$C42PASS "$PROTOCOL://$MASTER:$PORT/api/storePoint/$STOREPOINT" | python -mjson.tool | grep '"serverId":')
	SERVER=$(echo ${SERVER##*:})
        SERVER=$(echo ${SERVER%\,})

	#Get the server address or IP from the Server resource (using the serverId from previous section)
	STORAGE_SERVER=$(curl -sku $C42UID:$C42PASS "$PROTOCOL://$MASTER:$PORT/api/server/$SERVER" | python -mjson.tool | grep '"primaryAddress":')
	STORAGE_SERVER=$(echo ${STORAGE_SERVER##*ss\":})
        STORAGE_SERVER=$(echo ${STORAGE_SERVER#\"})
        STORAGE_SERVER=$(echo ${STORAGE_SERVER%\"\,})
	STORAGE_SERVER=$(echo ${STORAGE_SERVER%:4282})
	
	#Test for Archive Metadata output to avoid JSON decoding errors
	TESTNULL=$(curl -sku $C42UID:$C42PASS "https://$STORAGE_SERVER:4285/api/ArchiveMetadata/$ARCHIVE?decryptPaths=true" | grep "$CHECKSUM")
	
	if [ -n "$TESTNULL" ] 
	then
		#Get data, extract paths, and print 
		curl -sku $C42UID:$C42PASS "https://$STORAGE_SERVER:4285/api/ArchiveMetadata/$ARCHIVE?decryptPaths=true" | python -mjson.tool| grep -B3 "$CHECKSUM" | grep "path\"" | awk -F "\"" '{print "'$USERNAME'," "'$USERID'," "'$COMPNAME'," "'$DEVICE'," $4}' >> $FILENAME
		
		#Increment counter of number of Guids with positive match
		HITS=$(($HITS +1))
	fi
		
	COUNT=$(($COUNT + 1))

done

#Print results summary to terminal
echo "Number of Devices scanned"
echo $COUNT
echo "Number of Devices matching search"
echo $HITS
echo "Percentage positive search"
if [ $COUNT != 0 ]
then
	echo "scale=1;$HITS/$COUNT*100"| bc
else 
	echo "N/A - No Devices Found"
fi
echo "Results can be found in the following file where the script is located."
echo $FILENAME

exit 0
