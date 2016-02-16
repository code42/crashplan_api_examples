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
'''
SUMMARY: restoreWatch.py is a data leak prevention (DSP) solution that
monitors users in the Code42 environment for restore activity that might
be of concern. It can take actions to stop suspcious restores from
occurring after detection, and warn admins  and users about the activity.

Version 1.3
by Todd Ojala
Date: 5/28/2015
Original creation date: 4/24/2015

Copyright (c) 2016 Code42, Inc.
Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the "Software"), to deal 
in the Software without restriction, including without limitation the rights 
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.

** DISCLAIMER **
This script is provided as-is, and is not guaranteed to be suitable for
any particular application. Use at your own risk.

PURPOSE
To prevent data leaks, detect restore activity of concern, and take
action when such activity is detected. Actions include warning the
admin, blocking admin, and blocking the user who has initiated the
restores.

OUTPUT
The script produces the following output:
1. Email to administrator or designated recipient of warning messages.
2. CSV file with warnings, affected users, actions taken, and other
information. This file is only created or appended to when a trigger
event is detected!
3. restoreWatchData: a binary file that stores data needed by the script.
This file is not user-viewable.

REQUIRED PERMISSIONS
The user credentials used to invoke this script must have SYSADMIN
permission.

WARNING
This script will contain the credentials of a user with SYSADMIN rights
on your Code42 master server in order to function as intended.
** Take appropriate precautions to restrict access to this file **

INSTRUCTIONS:
1. Copy the script to a safe location on your computer's filesystem. Set
    file permissions so that non-trusted users cannot read the contents
    of the file.
2. Set the variables under the "ADMIN PARAMETERS" section to values that
    work in your envirnment. WARNING: as this section may contain
    sensitive info, make sure that only trusted users have access to
    this file.
3. Set the variables under the "MONITORED USER PARAMETERS" section, or
    add multiple users to the "initial_data" dictionary object with
    care.
4. Set the email address for the person who should receive alerts. 
5. Configure your system's cron job scheduler (or other scheduler) to
    run the script at an interval that is appropriate for your
    environment, e.g. every minute.
6. To reset the start of monitoring, simply delete or rename the file
"restoreWatchData."
8. To change the monitoring parameters or actions after monitoring has
    started, change the constants under "MONITORED USER PARAMETERS",
    then delete the file "restoreWatchData."

AVAILABLE TRIGGERS FOR WARNINGS, ALERTS AND ACTIONS
1. TOO_MANY_RESTORES_ACTION: What action to take if the number of
    restores of a user's data exceeds a defined rate. Values: NONE,
    WARN, BLOCK.
2. TOO_MANY_RESTORES_THRESHOLD: The threshold for the action in #1.
    Values: integers from 1 to a large number. This threshold is a count
    of the number of restores that have been occurred since the script
    last ran. The count starts over after each run.
3. NON_ORIGIN_DEVICE_RESTORE_ACTION: What action to take if a user's
    files are restored to a device that was not the source of the files.
    Values: NONE, WARN, BLOCK
4. NON_OWNER_RESTORE_ACTION: What action to take if a user's files are
    restored by a user who is not the owner of the files. Values: NONE,
    WARN, BLOCK
5. WEB_RESTORE_ACTION: What action to take if a user's files are
restored via a web restore. Values: NONE, WARN, BLOCK

TECHNICAL NOTES
Working data about users in the monitored list, the restores that have
been detected, actions to take, and thresholds are stored in the file
"restoreWatchData." This file is not human readable, but may contain
sensitive info. The file name may be changed under MISC PARAMETERS
below, to facilitate running multiple instances of the script.

The parameters are set only during the first time the script is run, and
then stored in "restoreWatchData." The setup parameters will not be read
again, unless the file "restoreWatchData" is deleted or renamed. To
force the parameters to be read again, delete or rename the file
"restoreWatchData". This also resets the monitoring "start time", and
resets any other variables used by the script.

The results of the restore audit are stored in a file named
restoreWatch.csv. This file is cumulative, and stores all previous data
written to it, even if monitoring is reset by deleting or renaming
restoreWatchData.

The CSV file name may be changed under MISC PARAMETERS below, to
facilitate running multiple instances of the script.


Modifications:
5/6/2015 Improved docstrings for each function, so that the Python help function will work for each function.
    Also improved email function by breaking out into separate function that can use mailx or smtplib based on user preference 
5/8/2015 Further improvements to email functions. Mailx now uses the email address specified in the configuration variable/constant
    c42_admin_email. Smtplib can send successfully to an email server that uses SSL.
5/14/2015 Lots of changes, including support for sending email to the owner of the archive, and but fixes.
5/20/2015 Starting changes based on meeting with Peter L., Justin G., and Marc J. of 5/15/2015
5/27/2015 Improvements to comments, doc string, and general readability.
5/28/2015 Testing, added missing Web Restore event detection code.

'''

# All modules below are part of the standard Python distribution 
import sys
import os
import json
import csv
import datetime
import requests
from requests.auth import HTTPBasicAuth
import getpass
import pickle       # Used to serialize data before writing to disk
import smtplib      # Used to send email to those who get alerts (note being used in version 1.0)
from email.mime.text import MIMEText
import subprocess   # Used to run Unix commands from within Python (currently sending email via mailx and bash)


## ADMIN PARAMETERS

c42_master='https://master-server.example.com'
c42_port='4285'
c42_admin='admin'
c42_password='serect_password'        # Come up with a safer method for deployment. Store in file with restricted read access? 
c42_admin_email='c42admin@example.com'

## MONITORED USER PARAMETERS
##
## Enter a single user to monitor and the user's configuration, by setting the
## constants below. To enter multiple users, fill in the data
## dictionary "initial_data" with extra iterations of user entries by
## copying the first user's entry, then changing USERID to the actual
## userId's of the additional users.  The other constants can be copied verbatim.

USERID='1100'    

# Options are: NONE, WARN, BLOCK. Case sensitive.
TOO_MANY_RESTORES_ACTION='WARN'                                                       
TOO_MANY_RESTORES_THRESHOLD=3
NON_ORIGIN_DEVICE_RESTORE_ACTION='WARN'
NON_OWNER_RESTORE_ACTION='NONE'            
WEB_RESTORE_ACTION='BLOCK'                   

## The constants set below are not stored in the user state binary file, and can be changed after monitoring has started, without resetting/deleting binary file.

## REPORTING SETTINGS
EMAIL_ARCHIVE_OWNER=True

## MISC PARAMETERS
DATA_FILE='restoreWatchData'                
CSV_FILE='restoreWatch.csv'

## SSL SECURITY SETTINGS
# Verify SSL certs for requests to Code42 API. Set to False if your
# master server's cert is self-certified to avoid fatal error. Case
# sensitive.
VERIFY_CERT=False                           


## EMAIL SETTINGS
USE_MAILX=False                                     
MAIL_HOST='smtp.your_email_server.com'                  
SMTP_USE_SSL=True                           
SMTP_PORT='Default'                         # Set to string "Default" to use defaults set by SMTP Lib, or to an integer value.
SMTP_REQUIRES_AUTH=True                     
SMTP_USER='user@your_email_server.com'              
SMTP_PASS='secret_password'
SMTP_SENDING_USER=SMTP_USER                 


## Modify initial_data dictionary object with care.
initial_data={ USERID:{
                              'too_many_restores_action':TOO_MANY_RESTORES_ACTION,
                              'too_many_restores_threshold':TOO_MANY_RESTORES_THRESHOLD,
                              'non_origin_device_restore_action':NON_ORIGIN_DEVICE_RESTORE_ACTION,
                              'non_owner_restore_action':NON_OWNER_RESTORE_ACTION,
                              'web_restore_action':WEB_RESTORE_ACTION }
                              }

# *** Do not change anything below this line! ***

now=str(datetime.datetime.now())            
default_key_values={'monitorStartTime':now,
                    'restores':[{'restoreId':'1'}],
                    'too_many_restores_action':'NONE',
                    'too_many_restores_threshold':3,
                    'non_origin_device_restore_action':'WARN',
                    'non_owner_restore_action':'WARN',
                    'web_restore_action':'WARN', 'firstLook':True}


def getStoredDataFromDisk(file):
    ''' Retrieves the serialized user data and program data from disk
    where it is stored between script executions. '''
    try:
        data_from_file=pickle.load(open(file, 'rb'))
    except IOError:
        data_from_file={}           
    return data_from_file


def storeDataToDisk(file, data):
    ''' Serializes and stores user data and program data to disk. '''
    pickle.dump(data, open(file,'wb')) # The 'w' option overwrites any existing file


def verifyData(data): 
    ''' Verifies that each required key in the main data dictionary used to
    store user data, actions, thresholds, etc. exists. If not, create
    the key and give it a default value. '''
    for user in data: 
        for key in default_key_values:
            if data[user].has_key(key) == False:
                data[user][key]=default_key_values[key] 
    
    
def getNewUserRestores(user):
    ''' Retrieve up to the last 100 restores for this user or for all users
    if no user supplied. '''
    # This function should be improved to page back to the last stored
    # restore record if necessary. Currently, if more than 100 restores
    # were performed for this user between runs, restores over 100 will
    # be ignored.
    request_url=c42_master+':'+c42_port+'/api/restoreRecord'
    if user is not None:	
        payload={'sourceUserId': user }     
    else:
        payload={}
    new_restores_json=requests.get(request_url,auth=(c42_admin, c42_password), params=payload, verify=VERIFY_CERT)
    new_restores_converted_to_python_object=json.loads(new_restores_json.text)['data']
    return new_restores_converted_to_python_object['restoreRecords']

def getRecentRestores(from_hours_ago=24):
    '''
    Retrieve all restores going back in time by the defined number of hours. The default number of hours is 24.
    '''
    ## Remove this from master branch

def newRestoreEvents(user,user_data,restore_events):
    ''' Returns only the restores that are new for this user since the last
    monitoring event (the last time the script was run). '''
# If this is the first time this user has been monitored, this is a
#   special case: just store the last restore as the benchmark for
#   change. # If there was no "last restore," then nothing will be
#   inserted, but the first seeded restore with restoreID of 1 will be
#   there, and the # flag firstLook will be changed to false
    if user_data['firstLook']==True:
        user_data['firstLook']=False        
        try:
            last_restore=restore_events[0]  
        except IndexError:                  
            last_restore=False
        if last_restore is not False:
            user_data['restores'].append(last_restore)
        return []                       

    else: #                  
        temp_list_restores=[]           
        for restore in restore_events:
            restoreId=restore['restoreId']
            if int(restoreId)>int(user_data['restores'][-1]['restoreId']): # The restoreId of the restore event is greater than the restoreId of the last one in the list, so append it. I assume that the restoreIds increase with each new restore.
                temp_list_restores.append(restore)
                temp_list_restores.reverse()    
        return temp_list_restores 
                              
                
def buildReport(report_data, restore, event_type, action, result, monitorStartTime):
    '''
    Build the CSV report by adding a new entry to the list containing the data. 
    '''
    row={}
    row['Event type']=event_type
    row['restoreId']=restore['restoreId']
    row['startDate']=restore['startDate']
    row['Device owner Id']=restore['sourceUserId']
    row['Restore user Id']=restore['requestingUserId']
    row['File count']=restore['fileCount']
    row['Type']=restore['type']
    row['Action']=action
    row['Action result']=result
    row['Monitoring start']=monitorStartTime

    report_data.append(row)
     
def blockUser(user):
    ''' Block specified user using the UserBlock resource of the Code42
    API. '''
    request_url=c42_master+':'+c42_port+'/api/UserBlock/'+str(user)
    r=requests.put(request_url,auth=(c42_admin, c42_password),verify=VERIFY_CERT)

    if r.status_code==201:
        return 'SUCCESS'
    else:
        return 'FAIL'

def sendEmail(use_mailx, email_address, email_string):
    ''' Write admin email to disk, but only if there were events to
    report In the current version, using mailx requires the email text
    to be on a disk file. '''
    f=open('restoreWatchEmail.tmp','w')
    f.write(email_string)
    f.close()

    if use_mailx==True:
        mail_cmd="cat restoreWatchEmail.tmp | mailx -s 'RestoreWatch alert!' "+c42_admin_email
        p=subprocess.Popen(mail_cmd, shell=True, stdout=subprocess.PIPE)
##      Errors for sending email can be caught below. Use for testing script.
##      output, errors = p.communicate()
##      print errors,output
	os.remove('restoreWatchEmail.tmp')
        
    else:
        email_file=open('restoreWatchEmail.tmp', 'rb')
        email_msg=MIMEText(email_file.read())
        email_file.close()

        email_msg['Subject']= 'restoreWatch Data Leak & Protection Report'
        email_msg['From'] = SMTP_USER
        email_msg['To'] = email_address

        if SMTP_USE_SSL==False:
            if SMTP_PORT is not 'Default':
                s=smtplib.SMTP(MAIL_HOST, SMTP_PORT)
            else:
                s=smtplib.SMTP(MAIL_HOST)
        else:
            if SMTP_PORT is not 'Default':
                s=smtplib.SMTP_SSL(MAIL_HOST, SMTP_PORT)
            else:
                s=smtplib.SMTP_SSL(MAIL_HOST)
        if SMTP_REQUIRES_AUTH==True:
            s.login(SMTP_USER,SMTP_PASS)
        s.sendmail( SMTP_SENDING_USER, email_address, email_msg.as_string() )
        s.quit()
	os.remove('restoreWatchEmail.tmp')

def getUserEmail(userId):
    ''' Retrieve the email address of the user using the API '''
    request_url=c42_master+':'+c42_port+'/api/User/'+str(userId)
    user_info_json=requests.get(request_url,auth=(c42_admin, c42_password), verify=VERIFY_CERT)
    convert_user_info_to_python_object=json.loads(user_info_json.text)['data']
    email=convert_user_info_to_python_object['email']
    if '@' not in email:
        email=None
    return email


def main():
    
    report_data=[]      # This list contains the report to send via email and output to a CSV file on disk
    admin_email_string='SUMMARY OF ALERTS AND ACTIONS\n'                
    separator="***********************************************\n"       
    
    temp_data=getStoredDataFromDisk(DATA_FILE) 
    if len(temp_data)==0: # If there is no stored data, then load initial data from variables set in script
        data= initial_data.copy()
        verifyData(data) 
    else: 
        data=temp_data.copy()


    for user in data:
        user_data=data[user]
        monitorStartTime=user_data['monitorStartTime']
        user_email_string='ALERT FROM RESTORE WATCH REGARDING YOUR DATA\n'  
        user_email_trigger=False

        if user=='ALL':
            user=None   # When user none is passed to getNewUserRestores, returned restores are not restricted to a user
        restore_events=getNewUserRestores(user)
        
        # Further processing is required to determine which events are new, by
        # comparing the events to the previously stored events
        new_restores=newRestoreEvents(user,user_data,restore_events) 
        
        # Append the new restores for this user to the current data file in memory
        user_data['restores'].extend(new_restores)

        # Check for non-owner restore
        if user_data['non_owner_restore_action']<>'NONE':
            action=user_data['non_owner_restore_action']
            result='N/A'
            for restore in new_restores:
                sourceUserId=restore['sourceUserId']
                if restore['requestingUserId'] <> sourceUserId:
                    if action=='BLOCK':
                        result=blockUser(int(restore['requestingUserId']))
                    buildReport(report_data, restore, 'Non-owner restore', action, result, monitorStartTime)
                    user_email_trigger=True

                    # Build the string to send in email about this event
                    str1="Non-owner restore detected for user with GUID {}.\n".format(sourceUserId)
                    str2="Action taken: {}\n".format(action)
                    str3="The restoring user's GUID is {}\n".format(restore['requestingUserId'])
                    str4="The accepting device is {}\n".format(restore['acceptingComputerGuid'])
                    str5="Action result: {}\n".format(result)
                    user_email_string+=str1+str2+str3+str4+str5
                    user_email_string+="\nPlease contact your CrashPlan administrator.\n{}".format(separator)
                    admin_email_string+=str1+str2+str3+str4+str5
                    admin_email_string+="\nPlease view the CSV file {} for more details.\n{}".format(CSV_FILE, separator)

                    

        # Check for non-origin device restore
        if user_data['non_origin_device_restore_action']<>'NONE':
            action=user_data['non_origin_device_restore_action']
            result='N/A'
            for restore in new_restores:
                sourceUserId=restore['sourceUserId']
                if restore['sourceComputerGuid'] <> restore['acceptingComputerGuid']:
                    if action=='BLOCK':
                        result=blockUser(int(restore['requestingUserId']))
                    buildReport(report_data, restore, 'Non-origin device restore', action, result, monitorStartTime)
                    user_email_trigger=True
                    
                    # Build the string to send in email about this event
                    str1="Non-origin device restore detected for user with GUID {}.\n".format(sourceUserId)
                    str2="Action taken: {}\n".format(action)
                    str3="The restoring user's GUID is {}\n".format(restore['requestingUserId'])
                    str4="The accepting device is {}\n".format(restore['acceptingComputerGuid'])
                    str5="Action result: {}\n".format(result)
                    user_email_string+=str1+str2+str3+str4+str5
                    user_email_string+="\nPlease contact your CrashPlan administrator.\n{}".format(separator)
                    admin_email_string+=str1+str2+str3+str4+str5
                    admin_email_string+="\nPlease view the CSV file {} for more details.\n{}".format(CSV_FILE, separator)

        # Check for Web restore
        if user_data['web_restore_action']<>'NONE':
            action=user_data['web_restore_action']
            result='N/A'
            for restore in new_restores:
                sourceUserId=restore['sourceUserId']
                if restore['type']=='WEB':
                    if action=='BLOCK':
                        result=blockUser(int(restore['requestingUserId']))
                    buildReport(report_data, restore, 'Web restore detected', action, result, monitorStartTime)
                    user_email_trigger=True
                    
                    # Build the string to send in email about this event
                    str1="Web restore detected for user with GUID {}.\n".format(sourceUserId)
                    str2="Action taken: {}\n".format(action)
                    str3="The restoring user's GUID is {}\n".format(restore['requestingUserId'])
                    str4="The accepting device is {}\n".format(restore['acceptingComputerGuid'])
                    str5="Action result: {}\n".format(result)
                    user_email_string+=str1+str2+str3+str4+str5
                    user_email_string+="\nPlease contact your CrashPlan administrator.\n{}".format(separator)
                    admin_email_string+=str1+str2+str3+str4+str5
                    admin_email_string+="\nPlease view the CSV file {} for more details.\n{}".format(CSV_FILE, separator)


        # Check for too many restores. 
        if user_data['too_many_restores_action']<>'NONE':
            action=user_data['too_many_restores_action']
            result='N/A'
            restore_count=len(new_restores)

            if restore_count>user_data['too_many_restores_threshold']:
                restore=new_restores[-1] # The restore to use for determining the suspect user to block taken from last in series (most recent)
                sourceUserId=restore['sourceUserId']    # Only makes sense to set this for when user is not ALL (None)
                if action=='BLOCK' and user is not None:  # A block action doesn't make sense for all users and possibly different users doing restores
                    result=blockUser(int(restore['requestingUserId']))
                buildReport(report_data, restore, 'Too many restores', action, result, monitorStartTime) #Include the very last restore in the report
                user_email_trigger=True
                
                # Build the string to send in email about this event
                str1="Too many restores detected for user with GUID {}.\n".format(sourceUserId) # This doesn't really make sense for ALL users
                str2="Action taken: {}\n".format(action)
                str3="The restoring user's GUID is {}\n".format(restore['requestingUserId']) # This doesn't really make sense for ALL users
                str4="The accepting device is {}\n".format(restore['acceptingComputerGuid']) # This doesn't really make sense for ALL users
                str5="Total number of restores since last monitoring event: {}\n".format(str(restore_count))
                str6="Action result: {}\n".format(result)
                user_email_string+=str1+str2+str3+str4+str5+str6
                user_email_string+="\nPlease contact your CrashPlan administrator.\n{}".format(separator)
                admin_email_string+=str1+str2+str3+str4+str5+str6
                admin_email_string+="\nPlease view the CSV file {} for more details.\n{}".format(CSV_FILE, separator)
                
        if user_email_trigger==True and EMAIL_ARCHIVE_OWNER==True:
            user_email=getUserEmail(user)
            if user_email is not None:
                sendEmail(USE_MAILX, user_email, user_email_string)
                
## Create CSV report and write to disk file.
    if len(report_data)>0:
        keys= report_data[0].keys()
        
        # Output the report data to a disk file in CSV format. 
        with open(CSV_FILE, 'ab+') as csv_file:     # Append the new data to the current file. Delete the csv file manually if desired.
            dict_writer = csv.DictWriter(csv_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(report_data)

        
        sendEmail(USE_MAILX, c42_admin_email, admin_email_string)

    # Store the important user and config data to disk between runs           
    storeDataToDisk(DATA_FILE, data)
    

main()    
