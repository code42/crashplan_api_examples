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
# Description: This script will look for devices that have not completed a backup
# in the last X (Specified while running) days, but do NOT have a backup alert 
# (Meaning they have some backup activity recently).  It will output a CSV file 
# with the username, device name, destination name, last activity date and the 
# last completed backup date.
#
# Authors: Mike Hamilton, Mike Wallace
# 
###################################
# Variables (Customize)
###################################

# Your master server address and port number 
$MASTER="http://crashplan.demo42.com:4280"
# If you want to hardcode number of days, set this variable to the number of days
$days = Read-Host -Prompt 'Enter number of days without complete backup'

###################################
# Other Variables
###################################
$uriC = $MASTER + "/api/DeviceBackupReport?&active=true&alerted=false&srtKey=lastCompletedBackupDate"
$cred = get-credential
$a = Invoke-restmethod -Credential $cred -URi $uriC -Method Get
$compdate = (get-date).adddays(-$days)
$csv = "username","deviceName","destinationName","lastActivity","lastCompletedBackupDate"
$csv -join "," >> "NoCompletedBackups${days}Days.csv"

# Loop through each entry in device backup report
foreach ($d in $a.data) {

# If a backup has never been completed, export that device
    if (!$d.lastCompletedBackupDate){
        $outp=$d.username + "," + $d.deviceName + "," + $d.destinationName + "," + $d.lastActivity + "," + "Never Completed"
        $outp >> "NoCompletedBackups${days}Days.csv"
    }

# If a backup has completed, perform date conversions
    else{
    $pdate=$d.lastCompletedBackupDate.split("T") 
    $pdate=get-date($pdate[0])
    $pudate=(get-date $pdate).date
    $cudate=(get-date $compdate).date

# Export active devices that have not completed a backup within X days
        if ((get-date $pdate).date -lt (get-date $compdate).date) {
        $outp=$d.username + "," + $d.deviceName + "," + $d.destinationName + "," + $d.lastActivity + "," + $d.lastCompletedBackupDate
        $outp >> "NoCompletedBackups${days}Days.csv"
        }
    }
}