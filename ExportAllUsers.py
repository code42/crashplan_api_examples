import json

import httplib

import base64

cpc_host = "HOST OR IP ADDRESS"

cpc_port = 4285

cpc_username = "<username"

cpc_password = "<pw>"

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

