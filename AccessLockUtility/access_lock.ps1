# Copyright (c) 2017 Code42 Software, Inc.
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
#
# Code42 Access Lock Utility - v1.2
#
# Description: This script will remotely lock or unlock access on devices through 
# the Access Lock feature of Code42. Clients are required to be on Windows using 
# Bitlocker full-disk encryption. (6.0+)
#
# https://support.code42.com/Administrator/6/Monitoring_and_managing/Access_Lock
#
# Author: Kyle Hatlestad
#
#
########################################################
# Catch parameters passed to script
########################################################
Param(
  [Parameter(Mandatory=$False)]
	[string]$FullServerUrl,
	[string]$user,
	[string]$password,
	[string]$deviceGuid,
	[string]$report,
	
  [Parameter(Mandatory=$False)]
    [ValidateSet('LOCK','UNLOCK')]
	[string]$action
)

$scriptVersion = "1.2"
########################################################
# Functions
########################################################
#---------------------------------------------------------------------------------------#
#                       Perform Lock/Unlock per paramters passed						#
#---------------------------------------------------------------------------------------#
function errorHandler {    	  
	  param( [Parameter(Mandatory=$false)][string]$errorMessage)
	Write-Host "Error: " $_; Write-Host "`n"; Write-Host "Terminating script."; Write-Host "`n"
	& cmd /c pause
	Exit
}
#---------------------------------------------------------------------------------------#
#                       Perform Lock/Unlock per paramters passed						#
#---------------------------------------------------------------------------------------#
function getUserName {    	  
	  param( [Parameter(Mandatory=$true)][string]$FullServerUrl, [Parameter(Mandatory=$true)][HashTable]$headers, [Parameter(Mandatory=$true)][string]$userUid)
	$resourceurl = '/api/User/' + $userUid + '?idType=uid'
	$uri = $FullServerUrl + $resourceurl
	try {
		$getUserInfo = invoke-RestMethod -Uri $uri -Method GET -Headers $headers
	} catch {
		Write-Host "`n"; Write-Host "Error: " $_; Write-Host "`n"
	}
	return $getuserInfo.data.username
}
#---------------------------------------------------------------------------------------#
#                       Report on Lock/Unlock Status									#
#---------------------------------------------------------------------------------------#
function runReport {	    	  
	  param( [Parameter(Mandatory=$true)][string]$FullServerUrl, [Parameter(Mandatory=$true)][string]$CPUserName, [Parameter(Mandatory=$true)][string]$password, [Parameter(Mandatory=$true)][string]$report)
	$EncodedAuthorization = [System.Text.Encoding]::UTF8.GetBytes($CPUserName + ':' + $password)
	$EncodedPassword = [System.Convert]::ToBase64String($EncodedAuthorization)
	$headers = @{"Authorization" = "Basic $($EncodedPassword)"}
	$baseurl = $FullServerUrl
	$resourceurl = '/c42api/v3/auth/jwt'
	$uri = $baseurl + $resourceurl
	# Create session cookie
	try {
		$cookieRequest = invoke-WebRequest -Uri $uri -Method GET -Headers $headers -SessionVariable myWebSession
	} catch {
		errorHandler $_
	}
	# If -report is set to 'all', then generate a report for all devices
	if ($report -eq "all") {
		Write-Host "`n"
		Write-Host "Creating an Access Lock report on all devices can be a time consuming process. Note only devices that have ever been locked or unlocked will be reported. Continue?"
		$Readhost = Read-Host " ( y / n ) " 
		switch ($ReadHost) { 
			Y {$runReport=$true} 
			N {$runReport=$false} 
			Default {$runReport=$false} 
		} 
		if(-Not($runReport)) {
			Write-Host "Terminating script."
			Exit
		}
		# Create an array for the CSV values and establish variables for the Computer API call
		$numColsToExport = 11
		$holdarr = @()
		$pNames = @("LockingUserUid","LockingUserName","UnlockingUserUid","UnlockingUserName","IsLocked","LockEnabledDate","UnlockedDate","LockPasshprase","LastClientResponseDate","ModificationDate","CreationDate")
		$deviceCount = 1
		$currentPage = 1
		$pageSize = 250
		$keepLooping = $true
		$deviceLockStatus = "False"
		While ($keepLooping) {
			$resourceurl = '/api/Computer?pgSize=' + $pageSize + '&pgNum=' + $currentPage
			$uri = $baseurl + $resourceurl
			try {
				$deviceInfo = invoke-RestMethod -Uri $uri -Method GET -Headers $headers 
				foreach ($comp in $deviceInfo.data.computers) {
					[string]$FullVersion = $comp.version
					[int]$cpversionLength = $FullVersion.length
					[string]$cpversion = $FullVersion.Substring($cpversionLength-3)
					# Only check the access lock status for devices on 6.0.0 or greater
					If ($cpversion -ge 600) {
						$resourceurl = '/c42api/v3/AccessLock/' + $comp.guid
						$uri = $baseurl + $resourceurl
						try {
							$lockingUserName, $unlockingUserName = ""			
							$lockStatusRequest = invoke-RestMethod -Uri $uri -Method GET -ContentType $ContentType -WebSession $myWebSession
							$lockData = $lockStatusRequest.data	
							# The resultset only includes User Uid, so figure out the user name
							if ($lockData.lockingUserUid) {
								$lockingUserName = getUserName $baseurl $headers $lockData.lockingUserUid
							}
							if ($lockData.unlockingUserUid) {
								$unlockingUserName = getUserName $baseurl $headers $lockData.unlockingUserUid
							}
							# Establish an array of all the Access Lock info
							$row = @($lockData.lockingUserUid,$lockingUserName,$lockData.unlockingUserUid,$unlockingUserName,$lockData.isLockEnabled,$lockData.lockEnabledDate,$lockData.unlockDate,$lockData.lockPassphrase,$lockData.lastClientResponseDate,$lockData.modificationDate,$lockData.creationDate)
							# Add the data for the device to an object and add it to the larger arrow to export to CSV
							$obj = new-object PSObject
							for ($i=0;$i -lt $numColsToExport;$i++) {
								$obj | add-member -membertype NoteProperty -name $pNames[$i] -value $row[$i]
							}
							$holdarr += $obj
							$obj = $null
						} catch {
							$catcherror = ($error[0] | out-string)
							# If the device has never been locked or unlocked before, the status check will throw an certain error in not finding the status
							if($catcherror -notcontains "accessLock_not_found_for_device") {
								$deviceLockStatus = "False"
							} else {
								errorHandler $_
							}
						}
					}
				$deviceCount += 1
				}
			} catch {
				errorHandler $_
			}   
			if ($deviceInfo.data.computers.length -gt 0) {
				$keepLooping = $true
				Write-Host "Processed " $deviceCount " devices."
			} else {
				$keepLooping = $false
			}
			$currentPage += 1
		}	
		Write-Host "Processed " $deviceCount " devices in total."
		$resultsLogFileName = $(Get-Date -format M.d.yy.hh.mm.ss)
		# Export the results to a CSV file
		$holdarr | export-csv AccessLockReport_$resultsLogFileName.csv -NoTypeInformation 
		Write-Host "`n"
		Write-Host "See AccessLockReport_$resultsLogFileName.log for full details"
		Write-Host "`n"
	} else {
		# If not 'all', then it should be a specific device GUID
		$resourceurl = '/c42api/v3/AccessLock/' + $report
		$uri = $baseurl + $resourceurl
		try {
			$deviceLockInfo = invoke-RestMethod -Uri $uri -Method GET -ContentType $ContentType -WebSession $myWebSession
		} catch {
			errorHandler $_
		}
		$lockReport = $deviceLockInfo.data
		# The resultset only includes User Uid, so figure out the user name
		if ($lockReport.lockingUserUid)
		{
			$lockingUserName = getUserName $baseurl $headers $lockReport.lockingUserUid
		}
		if ($lockReport.unlockingUserUid)
		{
			$unlockingUserName = getUserName $baseurl $headers $lockReport.unlockingUserUid
		}
		Write-Host "The userUid of the user who locked the device: " $lockReport.lockingUserUid
		Write-Host "The user name of the user who locked the device: " $lockingUserName
		Write-Host "The userUid of the user who unlocked the device: " $lockReport.unlockingUserUid
		Write-Host "The user name of the user who unlocked the device: " $unlockingUserName	
		Write-Host "Lock status (True=LOCKED, False=UNLOCKED): " $lockReport.isLockEnabled
		Write-Host "Date and time device was unlocked: " $lockReport.unlockDate
		Write-Host "The passphrase used to lock the device. Use this passphrase to unlock the device: " $lockReport.lockPassphrase
		Write-Host "The date and time the Code42 cloud last received an update from the device: " $lockReport.lastClientResponseDate
		Write-Host "The date and time any Access Lock settings for this device were modified: " $lockReport.modificationDate
		Write-Host "The date and time Access Lock was initiated: " $lockReport.creationDate
		
		$resultsLogFileName = $(Get-Date -format M.d.yy.hh.mm.ss)
		"Locking User Uid: " + $lockReport.lockingUserUid | Out-File -append "AccessLockReport_$resultsLogFileName.log"
		"Locking User Name: " + $lockingUserName | Out-File -append "AccessLockReport_$resultsLogFileName.log"
		"Unlocking User Uid: " + $lockReport.unlockingUserUid | Out-File -append "AccessLockReport_$resultsLogFileName.log"
		"Unlocking User Name: " + $unlockingUserName | Out-File -append "AccessLockReport_$resultsLogFileName.log"
		"Lock Status: " + $lockReport.isLockEnabled | Out-File -append "AccessLockReport_$resultsLogFileName.log"
		"Date/Time of Unlock: " + $lockReport.unlockDate | Out-File -append "AccessLockReport_$resultsLogFileName.log"
		"Lock Passphrase: " + $lockReport.lockPassphrase | Out-File -append "AccessLockReport_$resultsLogFileName.log"
		"Date/Time of last checkin: " + $lockReport.lastClientResponseDate | Out-File -append "AccessLockReport_$resultsLogFileName.log"
		"Date/Time Access Lock settings were last modified: " + $lockReport.modificationDate | Out-File -append "AccessLockReport_$resultsLogFileName.log"
		"Date/Time Access Lock was initiated: " + $lockReport.creationDate | Out-File -append "AccessLockReport_$resultsLogFileName.log"
		Write-Host "`n"
		Write-Host "See AccessLockReport_$resultsLogFileName.log for full details"
		Write-Host "`n"
	}
	& cmd /c pause
	Exit
}

#---------------------------------------------------------------------------------------#
#                       Perform Lock/Unlock per paramters passed						#
#---------------------------------------------------------------------------------------#
function commandLineOperation {	    	  
	  param( [Parameter(Mandatory=$true)][string]$FullServerUrl, [Parameter(Mandatory=$true)][string]$CPUserName, [Parameter(Mandatory=$true)][string]$password, [Parameter(Mandatory=$true)][string]$deviceguid, [Parameter(Mandatory=$true)][string]$lockAction)
$EncodedAuthorization = [System.Text.Encoding]::UTF8.GetBytes($CPUserName + ':' + $password)
$EncodedPassword = [System.Convert]::ToBase64String($EncodedAuthorization)
$headers = @{"Authorization" = "Basic $($EncodedPassword)"}
$baseurl = $FullServerUrl
$resourceurl = '/c42api/v3/auth/jwt'
$uri = $baseurl + $resourceurl
# Create session cookie
try {
	$cookieRequest = invoke-WebRequest -Uri $uri -Method GET -Headers $headers -SessionVariable myWebSession
} catch {
	errorHandler $_
}
$resourceurl = '/c42api/v3/AccessLock/' + $deviceGuid
$uri = $baseurl + $resourceurl
# Determine if it's a LOCK(POST) or UNLOCK(PATCH) action
$requestMethod="PATCH"
switch ($action)
{
	UNLOCK {$requestMethod="PATCH"}
	LOCK {$requestMethod="POST"}
	default {$requestMethod="PATCH"}
}
# Send lock/unlock command
Try 
{
	$lockRequest = invoke-RestMethod -Uri $uri -Method $requestMethod -ContentType $ContentType -WebSession $myWebSession
} 
Catch 
{
	errorHandler $_
}
# Gather computer/device info including device name
$resourceurl = '/api/Computer/' + $deviceGuid + '?idType=guid'
$uri = $baseurl + $resourceurl
Try
{
	$deviceInfo = invoke-RestMethod -Uri $uri -Method GET -Headers $headers 
}
Catch
{
	errorHandler $_
}
$deviceName = $deviceInfo.data.name
# Call function to output the results to command window and file.
lockOutput $lockRequest $requestMethod $baseurl $CPUserName $deviceName $deviceGuid
# Wait for a key to continue
& cmd /c pause
Exit
}
#---------------------------------------------------------------------------------------#
#                               Output of Lock/Unlock Section							#
#---------------------------------------------------------------------------------------#
function lockOutput {	    	  
	  param( [Parameter(Mandatory=$true)][array]$lockRequest,[string]$requestMethod,[string]$baseurl,[string]$CPUserName,[string]$selectedDeviceName,[string]$selectedDeviceGuid)
	if ($requestMethod -eq "PATCH" )
	{
		$resultsLogFileName = $(Get-Date -format M.d.yy.hh.mm.ss)
		$lockRequestResult = $lockRequest.data
		if ($lockRequestResult.lockingUserUid)
		{
			$lockingUserName = getUserName $baseurl $headers $lockRequestResult.lockingUserUid
		}
		"Locking User Uid: " + $lockRequestResult.lockingUserUid | Out-File -append "UnlockResults_$resultsLogFileName.log"
		"Locking User Name: " + $lockingUserName | Out-File -append "UnlockResults_$resultsLogFileName.log"
		"Unlocking User Uid: " +  $lockRequestResult.unlockingUserUid | Out-File -append "UnlockResults_$resultsLogFileName.log"
		"Unlocking User Name: " + $CPUserName | Out-File -append "UnlockResults_$resultsLogFileName.log"
		"Unlock Date: " + $lockRequestResult.unlockDate | Out-File -append "UnlockResults_$resultsLogFileName.log"
		"Bitlocker Lock Passphrase: " +  $lockRequestResult.lockPassphrase | Out-File -append "UnlockResults_$resultsLogFileName.log"
		
		Write-Host "The device " $selectedDeviceName " is unlocked. The passphrase to enter into Bitlocker on the device is:"
		Write-Host "`n"
		Write-Host -ForegroundColor Green $lockRequestResult.lockPassphrase
		Write-Host "`n"
		Write-Host -ForegroundColor Red "WARNING: Save this lockpassphrase!  If you lock the device again (by submitting another POST request) before entering the lockPassphrase on the locked device, a new passphrase is created on the Code42 server, but the device is still locked with the original lockPassphrase."
		Write-Host "`n"
		Write-Host "See UnlockResults_$resultsLogFileName.log for full details"
		Write-Host "`n"
	} else {
		$resultsLogFileName = $(Get-Date -format M.d.yy.hh.mm.ss)
		"Locking User Name: " + $CPUserName | Out-File -append "LockResults_$resultsLogFileName.log"
		"Lock Date/Time: " + $(Get-Date -format G) | Out-File -append "LockResults_$resultsLogFileName.log"
		"Locked Device Name: " + $selectedDeviceName | Out-File -append "LockResults_$resultsLogFileName.log"
		"Locked Device GUID: " + $selectedDeviceGuid | Out-File -append "LockResults_$resultsLogFileName.log"
		"Lock Results: " + $lockRequest.data | Out-File -append "LockResults_$resultsLogFileName.log"

		[string]$lockResponseData = $lockRequest.data
		Write-Host $lockResponseData
		# Catch errors starting with HELPER_APP_. Those typically mean a problem invoking Bitlocker
		if ($lockResponseData.IndexOf("HELPER_APP") -ge 0) {
			Write-Host "`n"
			Write-Host "If the response results in a 'HELPER_APP_###' message, that typically indicates an issue in envoking Bitlocker. Ensure that Bitlocker is enabled and configured on the device. See documentation at https://support.code42.com/Administrator/Cloud/Monitoring_and_managing/Access_Lock for more information. "
			Write-Host "`n"
		} elseif ($lockResponseData.IndexOf("deviceLockableResult=OK") -ge 0 -and $lockResponseData.IndexOf("deviceRestarting=True") -ge 0) {
			Write-Host "`n"
			Write-Host "The device was successfully locked and has restared"
			Write-Host "`n"
		}
		Write-Host "`n"
		Write-Host "See LockResults_$resultsLogFileName.log for full details"
		Write-Host "`n"
	}
}

###################################
# Variables (Customize)
###################################
[string]$WebProtocol = "https"
[string]$global:ContentType = "application/json"

##############################################################
# Check if running command-line or interactive
##############################################################
if ($FullServerUrl) {
	if ($report) {
		runReport $FullServerUrl $user $password $report
	} else {
		commandLineOperation $FullServerUrl $user $password $deviceGuid $action
	}
}

###################################
# Intro Screen
###################################

Write-Host "####################################################################################"
Write-Host "`n"
Write-Host " Code42 Access Lock Utility"
Write-Host "`n"
Write-Host " Script Version: " $scriptVersion
Write-Host "`n"
Write-Host " This utiity is designed to perform an access lock on computer devices with the Code42"
Write-Host " CrashPlan 6.0+ client or above on Windows OS devices. It can also be used to unlock" 
Write-Host " devices previously locked and provide the Bitlocker recovery passphrase key."
Write-Host "`n"
Write-Host " Requirements:"
Write-Host " * Code42 Server 6.0+ or Code42 Fully Hosted"
Write-Host " * Code42 Enterprise License or Security Tools Add-On License"
Write-Host " * Code42 CrashPlan 6.0+ client"
Write-Host " * Windows OS configured with Bitlocker full-disk encryption"
Write-Host "`n"

Write-Host "####################################################################################"

###################################
# Inputs 
###################################
# Your master server address (e.g. code42.company.com, 177.14.34.193, etc)
$CPServer = Read-Host -Prompt 'Input your server address and web port(no http/s needed. e.g. company.c.code42.com:4285)'
# Username and Password prompt
$CPUserName = Read-Host -Prompt 'Input username'
$CPSecureUserPassword = Read-Host 'Input password' -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($CPSecureUserPassword)
$CPUserPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
$EncodedAuthorization = [System.Text.Encoding]::UTF8.GetBytes($CPUserName + ':' + $CPUserPassword)
$EncodedPassword = [System.Convert]::ToBase64String($EncodedAuthorization)
$headers = @{"Authorization" = "Basic $($EncodedPassword)"}

###################################
# Verify user has proper permissions
###################################
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$FullCPServerAddress = $WebProtocol + "://" + $CPServer
$resourceurl = '/api/User?incAll=true&active=true&q=' + $CPUserName
$uri = $FullCPServerAddress + $resourceurl

Write-Host "Trying " $uri 
try {
	
	$adminUser = invoke-RestMethod -Uri $uri -Method GET -Headers $headers 
} catch {
	[string]$catcherror = ($error[0] | out-string)
	# If using a self-signed cert, Powershell will not allow a connection. Use HTTP instead.
	if($catcherror.IndexOf("SSL/TLS") -ge 0) {
		$WebProtocol = "http"
		$FullCPServerAddress = $WebProtocol + "://" + $CPServer
		$uri = $FullCPServerAddress + $resourceurl
		try {
			$adminUser = invoke-RestMethod -Uri $uri -Method GET -Headers $headers 
		} catch {
			errorHandler $_
		}
	} else {
		errorHandler $_
	}
}
if ($adminUser.data.users.roles -contains "SYSADMIN" -Or $adminUser.data.users.roles -contains "Customer Cloud Admin") {
	#Permisions are good. They have one of the right roles
} else {
	Write-Host "`n"; Write-Host "User " $CPUserName " does not have permissions to run the Access Lock commands. The role 'SYSADMIN' or 'Customer Cloud Admin' is required."
	errorHandler $_
}
# Store the User Uid of the user performing the lock/unlock
$CPUserUid = $adminUser.data.users.userUid

# Check if the server is 6.0 or above. If fully-hosted using crashplan.com, then it will be fine
if ($FullCPServerAddress -notcontains "crashplan.com") {
	$resourceurl = '/api/Server'
	$uri = $FullCPServerAddress + $resourceurl
	try {	
		$serverInfo = invoke-RestMethod -Uri $uri -Method GET -Headers $headers 
		[string]$fullServerVersion = $serverInfo.data.servers.version
		[int]$majorVersion = $fullServerVersion.substring(0,1)
		if ($majorVersion -le 5) {
			Write-Host "`n"; Write-Host "The version of your server is " $fullServerVersion " and does not support Access Lock. You must be on version 6.0 or greater."
			errorHandler $_
		}
	} catch {
		errorHandler $_
	}
}

###################################
# Find user and their device(s)
###################################
$userCount = 0
while ( $userCount -ne 1){
	# User ID whose device you need to lock/unlock
	$lockUser = Read-Host -Prompt 'Enter the user ID for the owner of the device that is needed to lock or unlock access'
	$resourceurl = '/api/User?incAll=true&active=true&q=' + $lockUser
	$uri = $FullCPServerAddress + $resourceurl
	try {
		$userRequest = invoke-RestMethod -Uri $uri -Method GET -Headers $headers 
	} catch {
		errorHandler $_
	}
	$userCount = $userRequest.data.totalCount
	if ($userCount -eq 0) {
		# If the count is 0, no user is found
	} elseif ($userCount -gt 1) {
		#if the count is greather then 1, then more then one user was found
		foreach ($userFound in $userRequest.data.users) {
			if ($lockUser -eq $userFound.username) {
				# Pull the User Uid from the resultset
				$userUid = $userFound.userUid
				$userCount = 1
			}
		}
		if ($userCount -gt 1) {
				Write-Host "User not found. Please enter a valid user ID."
				Write-Host "`n"
		}
	} else {
		# Pull the User Uid from the resultset
		$userUid = $userRequest.data.users.userUid
	}
}

# Envoke the request to establish a session cookie with the new v3 API call that the Access
# Lock API requires
$resourceurl = '/c42api/v3/auth/jwt'
$uri = $FullCPServerAddress + $resourceurl
try {
	$cookieRequest = invoke-WebRequest -Uri $uri -Method GET -Headers $headers -SessionVariable myWebSession
} catch {
	errorHandler $_
}

# Get the list of devices under the user
$resourceurl = '/api/Computer?userUid=' + $userUid + '&incBackupUsage=true&active=true'
$uri = $FullCPServerAddress + $resourceurl
try {
	$deviceList = invoke-RestMethod -Uri $uri -Method GET -Headers $headers
} catch {
	errorHandler $_
}

# Loop through the devices and show each one as a choice along with their information and current lock status
$deviceALGuids = @()
$deviceAlNames = @()
$deviceLockStatusArray = @()
$deviceLockStatus = "False"
$i = 1

$noALCompName = @()
$noALCompGuid = @()
$noALCompLastConnected = @()
$noALCompVersion = @()
$j = 1

$k = 0
$displayStatus="UNLOCKED"

Write-Host "`n"
Write-Host "Computers available for Access Lock"
Write-Host "==================================================================="
foreach ($comp in $deviceList.data.computers) {
	#If the client is on Windows and 6.0 or greater, make it a choice. If not, create an array of the ineligible devices
	[string]$FullVersion = $comp.version
	[int]$cpversionLength = $FullVersion.length
	[string]$cpversion = $FullVersion.Substring($cpversionLength-3)
	if ($cpversion -ge 600) {
		# If the device is 6.0+, we next need to check the current status of the lock.
		$resourceurl = '/c42api/v3/AccessLock/' + $comp.guid
		$uri = $FullCPServerAddress + $resourceurl
		try {
			$lockStatusRequest = invoke-RestMethod -Uri $uri -Method GET -ContentType $ContentType -WebSession $myWebSession
			$deviceLockStatus = $lockStatusRequest.data.isLockEnabled
		} catch {
			$catcherror = ($error[0] | out-string)
			# If the device has never been locked or unlocked before, the status check will throw an certain error in not finding the status
			if($catcherror.Contains("accessLock_not_found_for_device")) {
				$deviceLockStatus = "False"
			} else {
				errorHandler $_
			}
		}
		switch ($deviceLockStatus)
		{
			true {$textColor="Red";$displayStatus="LOCKED"}
			false {$textColor="Green";$displayStatus="UNLOCKED"}
			default {$textColor="Green";$displayStatus="UNLOCKED"}
		}
		# Now display the information as a selection for locking/unlocking the device
		Write-Host "[$i] Computer Name: " $comp.name " | GUID: "$comp.guid " | LastConnected: "$comp.lastConnected " | Current Access Lock Status: " -NoNewLine; Write-Host -ForegroundColor $textColor $displayStatus
		$deviceALGuids += $comp.guid
		$deviceAlNames += $comp.name
		$deviceLockStatusArray += $deviceLockStatus
		$i++
		$k++	
	} else {
		# build a list of devices that are not available for locking/unlocking
		$deviceNoALGuids += $comp.guid
		$noALCompName += $comp.name
		$noALCompGuid += $comp.guid
		$noALCompLastConnected += $comp.lastConnected
		$noALCompVersion += $cpversion
		$j++
		$k++
	}
	
}
Write-Host "[$i] None - Exit"
Write-Host "`n"
Write-Host "Computers not eligible for Access Lock"
Write-Host "==================================================================="

for ($l=0; $l -lt $k-1; $l++) {
    Write-Host "Computer Name: " $noALCompName[$l] " | GUID: "$noALCompGuid[$l] " | LastConnected: "$noALCompLastConnected[$l] " | Client Version: " $noALCompVersion[$l]
}
Write-Host "`n"

[int]$srccomp = read-host -prompt "`nPlease choose the computer number from list above to lock/unlock"
if ($srccomp -eq $i -Or $srccomp -eq "") {
	Write-Host "Terminating script."; Write-Host "`n"
	& cmd /c pause
	Exit
}
$selectedDeviceGuid = $deviceALGuids[$srccomp-1]
$selectedDeviceName = $deviceALNames[$srccomp-1]
$selectedDeviceLockStatus = $deviceLockStatusArray[$srccomp-1]
# Based on the current status of the device, perform the opposite action to lock/unlock the device
# the POST method will lock and the PATCH method with unlock
$requestMethod="PATCH"
switch ($selectedDeviceLockStatus)
{
	true {$requestMethod="PATCH"}
	false {$requestMethod="POST"}
	default {$requestMethod="PATCH"}
}
[string]$ContentType = "application/json"
$resourceurl = '/c42api/v3/AccessLock/' + $selectedDeviceGuid
$uri = $FullCPServerAddress + $resourceurl
try {
	$lockRequest = invoke-RestMethod -Uri $uri -Method $requestMethod -ContentType $ContentType -WebSession $myWebSession
} catch {
	Write-Host "`n"; Write-Host "Error: " $_; Write-Host "`n"
}
Write-Host "`n"
lockOutput $lockRequest $requestMethod $FullCPServerAddress $CPUserName $selectedDeviceName $selectedDeviceGuid
# Wait for a key to continue
& cmd /c pause
Exit
