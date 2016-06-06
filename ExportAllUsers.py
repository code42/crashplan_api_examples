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
This script retrieves a list of all users in your Code42 environment.

Arguments: Your admin password. 
The host, port and username parameters are set in the body of the script.

usage: from the command line enter:
python ExportAllUsers.py

To send output to a CSV file rather than standard output, redirect to desired filename, e.g.:
python ExportAllUsers.py > all_users.csv

Last modified: 3-18-2015 by Todd Ojala, to add a description of the script's purpose.

'''
import json

import httplib

import base64

import getpass

cpc_host = "HOST OR IP ADDRESS"

cpc_port = 4285

cpc_username = "<username"

cpc_password = getpass.getpass('Enter your CrashPlan console password: ') # You will be prompted for your password

def getAuthHeader(u,p):

        # Compute base64 representation of the authentication token.

    token = base64.b64encode('%s:%s' % (u,p))

    return "Basic %s" % token

def getUsers():

        # We supply HTTP authentication headers in advance.

        # And while the "Accept" header below is not strictly required

        # (JSON is the default encoding for the CrashPlan API)

        # it's good practice to explicitly include it.

    headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json"}

    try:

        conn = httplib.HTTPSConnection(cpc_host,cpc_port)

  

        conn.request("GET","/api/users?strKey=lastBackupDate&incAll=true",None,headers)

        data = conn.getresponse().read()

        conn.close()

	

	users = json.loads(data)['data']

	#header key row

 	hkeys = ("userId", "orgId","username","email","firstName","lastName", "status","computerCount", "lastLoginDate", "active", "blocked", "targetComputerId", "selectedFiles", "selectedBytes", "lastBackupDate", "lastCompletedBackupDate", "archiveBytes", "todoBytes", "todoFiles")

 	keys = ("userId", "orgId","username","email","firstName","lastName", "status","computerCount", "lastLoginDate", "active", "blocked", "backupUsage")

	bkeys= ("targetComputerId", "selectedFiles", "selectedBytes", "lastBackupDate", "lastCompletedBackupDate", "archiveBytes", "todoBytes", "todoFiles")

	first = True

	for d in users['users']:

		if first:

			first=False

			head=""

			for k in hkeys:

				head += k + ","

			print head

   			text = head

		line =""

		for k in keys:

			#checking  if hit backupUsage row and loop through the bkeys list

			if k=='backupUsage':

				backupData = d[k]

				for b in backupData:

					for a in bkeys:

						line += "%s," % b[a]

			else:	

				line += "%s," % d[k]

		print line

        return json.loads(data)

    except httplib.HTTPException as inst:

        print "Exception: %s" % inst

        return None

    except ValueError as inst:

        print "Exception decoding JSON: %s" % inst

        return None



getUsers()

