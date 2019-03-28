# By downloading and executing this software, you acknowledge and agree that Code42 is providing you this software at no cost separately from Code42's commercial offerings.
# This software is not provided under Code42's master services agreement.
# It is provided AS-IS, without support, and subject to the license below.
# Any support and documentation for this software are available at the Code42 community site.

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
#
# Code42 Forensic File Search Example Script - v1.1
#
# Description: This script will perform a Forensic File Search via the API. It 
# can perform a single search or be fed a list of search terms.
#
# https://support.code42.com/Administrator/Cloud/Administration_console_reference/Forensic_File_Search_reference_guide
#
# Author: Kyle Hatlestad
#
#

########################################################
# Catch parameters passed to script
########################################################
Param(
	[alias("u")]
	[string]$user,
	[alias("p")]
	[string]$password
)

$scriptVersion = "1.1"
########################################################
# Functions
########################################################
#---------------------------------------------------------------------------------------#
#                       Error handling function											#
#---------------------------------------------------------------------------------------#
function errorHandler {    	  
	  param( [Parameter(Mandatory=$false)][string]$errorMessage)
	Write-Host "Error: " $_; Write-Host "`n"; Write-Host "Terminating script."; Write-Host "`n"
	& cmd /c pause
	Exit
}

###################################
# Variables (Customize)
###################################
[string]$global:ContentType = "application/json"
[string]$FullCPServerAddress = "https://console.us.code42.com"
[string]$FullSTSServerAddress = "https://sts-east.us.code42.com"

###################################
# Intro Screen
###################################

Write-Host "####################################################################################"
Write-Host "`n"
Write-Host " Code42 Forensic File Search Example Script"
Write-Host "`n"
Write-Host " Script Version: " $scriptVersion
Write-Host "`n"
Write-Host " Description: This script will perform a Forensic File Search via the API. It "
Write-Host " shows how a call is made and results taht come back."
Write-Host "`n"
Write-Host " Requirements:"
Write-Host " * Code42 Cloud"
Write-Host " * Code42 Security Center Product"
Write-Host " * User with either Customer Cloud Admin or Security Center User role"
Write-Host " * Windows 10 Client with Windows PowerShell"
Write-Host " * You must run Internet Explorer (not Edge) at least once for the initial configuration"
Write-Host "`n"
Write-Host "Command-line Arguments:"
Write-Host "  -u"
Write-Host "     Username"
Write-Host "  -p"
Write-Host "     Password"
Write-Host "`n"
Write-Host "####################################################################################"

###################################
# Inputs 
###################################
# Username and Password prompt if not passed in

IF([string]::IsNullOrEmpty($user)) {            
    $CPUserName = Read-Host -Prompt 'Input username'            
} else {            
    $CPUserName = $user          
}

IF([string]::IsNullOrEmpty($password)) {            
    $CPSecureUserPassword = Read-Host 'Input password' -AsSecureString
	$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($CPSecureUserPassword)
	$CPUserPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)            
} else {            
    $CPUserPassword = $password          
}

$EncodedAuthorization = [System.Text.Encoding]::UTF8.GetBytes($CPUserName + ':' + $CPUserPassword)
$EncodedPassword = [System.Convert]::ToBase64String($EncodedAuthorization)
$headers = @{"Authorization" = "Basic $($EncodedPassword)"}

# Prompt for search parameters

#Search Term
Write-Host "Select the Search Term"
Write-Host "*1 - Filename"
Write-Host "2 - File Path"
Write-Host "3 - MD5 Hash"
Write-Host "4 - Hostname"
Write-Host "5 - Username"

$getSearchTerm = Read-Host -Prompt "Enter choice (1-5)"
$searchTerm = switch ($getSearchTerm)
		{
			1 {'fileName'}
			2 {'filePath'}
			3 {'md5Checksum'}
			4 {'osHostName'}
			5 {'deviceUserName'}
			default {'fileName'}
		}
		
Write-Host "Select the Operator"
Write-Host "*1 - Is"
Write-Host "2 - Is Not"

$getSearchOperator = Read-Host -Prompt "Enter choice (1-2)"
$searchOperator = switch ($getSearchOperator)
		{
			1 {'IS'}
			2 {'IS_NOT'}
			default {'IS'}
		}		

DO  {
	$searchValue = Read-Host -Prompt 'Input your search value'
} WHILE ([string]::IsNullOrEmpty($searchValue))


###################################
# Verify user has proper permissions
###################################
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$CPEncodedUserName = [uri]::EscapeDataString($CPUserName)
$resourceurl = '/api/User?incAll=true&active=true&q=' + $CPEncodedUserName
$uri = $FullCPServerAddress + $resourceurl
 
try {
	
	$securityUser = invoke-RestMethod -Uri $uri -Method GET -Headers $headers 
} catch {
	errorHandler $_
}

if ($securityUser.data.users.roles -contains "Security Center User" -Or $securityUser.data.users.roles -contains "Customer Cloud Admin") {
	#Permisions are good. They have one of the right roles
} else {
	Write-Host "`n"; Write-Host "User " $CPUserName " does not have permissions to run Forensic File Search. The role 'Security Center User' or 'Customer Cloud Admin' is required."
	errorHandler $_
}

######################################################
# Authenticate and establish Authorization Token 
######################################################

# Call the login-user method on the Secure Token Server to create the Code42 V3 User Token
$resourceurl = '/api/v1/login-user'
$uri = $FullSTSServerAddress + $resourceurl

try {
	$requestResponse = invoke-WebRequest -Uri $uri -Method GET -Headers $headers -SessionVariable myWebSession
} catch {
	errorHandler $_
}

# From the resonse, pull out the v3_user_token value to pass into the header for the FFS calls
$authBody = $requestResponse | ConvertFrom-Json
$v3Token = $authBody.v3_user_token

# Set the parameters based on the input. 
# Build FFS search terms into a JSON message
$json = '{
   "groups": [
	{
	  "filters": [
		{
		  "operator": "' + $searchOperator + '",
		  "term": "' + $searchTerm + '",
		  "value": "' + $searchValue + '"
		}
	  ]
	}
  ],
  "pgNum": 1,
  "pgSize": 10000,  
  "srtDir": "asc",
  "srtKey": "eventTimestamp"
}'


# Assemble the File Event API call with token authorization
$resourceurl = '/forensic-search/queryservice/api/v1/fileevent/'
$uri = $FullCPServerAddress + $resourceurl

$headers = @{}
$headers.Add("Authorization","v3_user_token " + $v3Token)
Write-Host "Executing search..."

# Execute the search and measure the search response
$time = Measure-Command {
$searchRequest = invoke-WebRequest -Uri $uri -Method POST -Body $json -ContentType $ContentType -Headers $headers
}
Write-Host "Done!"
Write-Host "Total search time: " $time.Milliseconds " milliseconds"

$searchResultBody = $searchRequest | ConvertFrom-Json

# Output the results and record the # of results and search in files
$timeStamp = (get-date -f yyyy-MM-dd_hh_mm_ss)
$pathToCsvOutputFile = "ffs_results_" + $timeStamp + ".csv"		
$pathToTxtOutputFile = "ffs_search_" + $timeStamp + ".txt"	
$searchResultBody | Select-Object -expand fileEvents | 
    ConvertTo-Csv -NoTypeInformation |
    Set-Content $pathToCsvOutputFile

"Total Results: " + $searchResultBody.totalCount | Set-Content $pathToTxtOutputFile
"Search Query: " | Add-Content $pathToTxtOutputFile
$json | Add-Content $pathToTxtOutputFile

# Final result count display
Write-Host "Results: " $searchResultBody.totalCount
Write-Host "See file" $pathToCsvOutputFile "for results."
# Wait for a key to continue
& cmd /c pause
Exit
