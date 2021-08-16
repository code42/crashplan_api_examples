# Deprecated
[![No Maintenance Intended](http://unmaintained.tech/badge.svg)](http://unmaintained.tech/)

Code42 recommends that customers visit [developer.code42.com](https://developer.code42.com) for current documentation and reference to current supported toolkits.

---
# CrashPlan API Examples

This project is a showcase area for various scripts that either Code42 or its customers have provided that run against the Code42 REST API and extend the functionality or reporting beyond what is possible in the default console.

---
## Folder Descriptions
### AccessLockUtility
This Windows utility (.exe and powershell script provided) uses the Access Lock feature present in Code42 versions 6.0+ to remotely lock or unlock a device running the Code42 client application.  For full readme information, see the `access_lock.pdf` file inside the directory.

### AuthorityMigrationHelpers
If you're planning on migrating your Code42 authority to the cloud, these scripts will help you with the most common tasks needed to get your authority migrated.  See `README.md` in this directory for more detailed info on the below scripts:
1. `roleChanger.py` - batch add or remove roles for users in your environment
2. `usernameToEmails.py` - change usernames to e-mail addresses using a few different methods

### CompiledScripts
This folder contains compiled versions of scripts that appear elsewhere in this repository.  No dependencies needed, just download and run the binary.

### FFS
This Windows utility (.exe and powershell script provided) uses the Code42 API in order to return Forensic File Search events matching one or more search terms.

### c42SharedLibScripts
This folder contains a number of all-purpose scripts built off of Code42's shared python library.  See `README.md` in this folder for more information.

---
## Standalone Scripts

#### NoBackupsInXDays.ps1
This script will look for devices that have not completed a backup in the last X (Specified while running) days, but do NOT have a backup alert (Meaning they have some backup activity recently).  It will output a CSV file with the username, device name, destination name, last activity date and the last completed backup date.

#### addLDAPUsers.py
Takes a comma-delimited CSV file of user names and adds those users to a LDAP Org.

PRE-REQS:
* Python 2.7
* Requests Module
  * http://www.python-requests.org/
* PROe Server Host and Port
* PROe Server Admin and Password
* CSV file name
* LDAP ORG ID. You can get this by navigating to the org and getting the org id value from the url. For example, `http://localhost:4280/console/app.html#v=orgs:overview&t=0mbunsjn5sbz91tlzg5clpd7qg&s=orgDetail&so[orgId]=3` would be an Org ID of 3.

STEPS:
1. Create CSV file with comma-delmited list of LDAP users to add to the PROe Server. Save it in the same location as the addLDAPUsers.py script.
2. Update addLDAPUsers.py and add your environment values for cp_host, cp_port, etc.
3. Execute the script and check the addLDAPUsers.log file for your results.

#### deactivateDevices.py
Deactivates users devices based on the number of months since they have last connected to the authority server

Params:
* 1st arg - number of months (i.e 3)
* 2nd arg - type of logging
  * values: `verbose`, `nonverbose`
* 3rd arg - set to deactivate devices or only print the devices that will be deactivated, but not deactivate them.
  * values: `deactivate`, `print`

Example usages:
* `python deactivateDevices.py 3 verbose print`
* `python deactivateDevices.py 3 noverbose deactivate`

#### pushRestore.sh
pushRestore.sh [sourceComputer] [destComputer] [restorePath] [getDirs] [getFiles]

Example:

`./pushRestore.sh 'COMP1' 'COMP2' '/tmp/restore' '/tmp/dir1,/tmp/dir 2' '/tmp/file1,/tmp/file 2'`

This example script performs an automated Push Restore (via REST):
* One or more source files/directories.
* To local or remote destination computer.  To remote directory of choice.
* Using MPC or Cloud storage.
* Recursive restore (includes subdirectories).
* Between computers of different users (if Admin).
* ...and more.

Edit the variables near the top of this script, or pass in optional args.

Notes:
* Push destination should be running authenticated Code42 client.
* Archive adoption (or original owner) not required.

#### restoreWatch.py
To prevent data leaks, detect restore activity of concern, and take
action when such activity is detected. Actions include warning the
admin, blocking admin, and blocking the user who has initiated the
restores.

The script produces the following output:
1. Email to administrator or designated recipient of warning messages.
2. CSV file with warnings, affected users, actions taken, and other
information. This file is only created or appended to when a trigger
event is detected!
3. restoreWatchData: a binary file that stores data needed by the script.
This file is not user-viewable.

See full description and instructions in the header of this script.
