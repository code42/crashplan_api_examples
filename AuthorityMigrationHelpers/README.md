By downloading and executing this software, you acknowledge and agree that Code42 is providing you this software with cost separately from Code42's commercial offerings. This software is not provided under Code42's master services agreement. It is provided AS-IS, without support, and subject to the license below. Any support and documentation for this software are available at the Code42 community site.
# Authority Migration Helpers
These scripts are designed for customers that will be migrating their on-prem Code42 authority into the Code42 multi-tenant cloud.  Two of the most common tasks that admins need to do are to remove any custom roles, and to make sure all of their usernames are in an e-mail format.
For both scripts run with -h to get help on the syntax needed for running the scripts.

Required non default libraries:
requests
pandas


### cloudRoleAdder.py
#Usage
cloudRoleAdder.py [-h] -s SERVERURL -u USERNAME [-e]

Input for this script

optional arguments:
  -h, --help    show this help message and exit
  -s SERVERURL  Server and port for the server ex:
                "https://server.url.code42.com:4285"
  -u USERNAME   Username for a SYSADMIN user using local authentication
  -e            Add this flag to run it for real. Leave out for a dry run
  
#Information

This is a standalone Python script which will walk the admins through dealing with and adding cloud roles to users that may have a on premis only role. Suggested mappings to be used when running this script are below:

 * SYSADMIN             --> Customer Cloud Admin
 * Server Administrator       --> Customer Cloud Admin
 * All Org Admin        --> Cross Org Admin
 * All Org Legal Admin    --> Cross Org Legal Admin
 * All Org Manager        --> Cross Org Manager
 * All Org Security Viewer--> Cross Org Security Viewer


Options while running the script:

* Type skip, or s to skip a role assingment.
* For known on prem roles the script has a pre set mapping for roles. You may accept the suggestions in the script by typing yes in response to them.

For help with this app/script, post your question on the Code42 community in the Open Discussion forum: https://success.code42.com/discussion. If you don't already have an account, you can create one. For more information, see https://success.code42.com/help/community-documentation/join-forums.


### usernamesToEmails.py

#Usage 
usernameToEmails.py [-h] -s SERVERURL -u USERNAME --method {1,2,3,4} [-e] [-f INPUTFILE]

Input for this script

optional arguments:
  -h, --help          show this help message and exit
  -s SERVERURL        Server and port for the server ex:
                      "https://server.url.code42.com:4285"
  -u USERNAME         Username for a SYSADMIN user using local authentication
  --method {1,2,3,4}  Select which method you want to use for changing
                      usernames to email addresses. 1=Make user's email their
                      username.2=username@domain.com 3=first.last@domain.com.
                      4=Check to see if all usernames are emails
  -e                  Add this flag to run it for real. Leave out for a dry
                      run
  -f INPUTFILE        File that contains just the userIds you want to alter

#Information
This is a standalone Python script which will change users' usernames to the e-mail format required by the Code42 cloud based on one of three methods that the admin can specify:
1. Make user's email their username
    * This method simply copies whatever is used in the Code42 `email` field and pastes it into their `username` field
    * For the example user below, the username would get changed to ` bob@company.com`
2. Append a static domain to the username
    * This method takes the current username and appends an admin-defined suffix (` @company.com`) at the end
    * For the example user below, the username would get changed to ` bsmith@company.com`
3. Use the user's first and last name, along with a static domain
    * This method uses the `First Name` and `Last Name` fields of a Code42 user account as well as an admin-defined domain suffix and puts the result in the username field.
    * For the example user below, the username would get changed to ` bob.smith@company.com`
4. Runs a read only report and prints out a list of users that don't have emails as their username.
    * Used for reporting purposes only, to check the work of the other methods.
    * Can also be used to generate a starting file for the -f flag.

Example User (beginning state):
* username: `bsmith`
* email: ` bob@company.com`
* First Name: `Bob`
* Last Name: `Smith`
