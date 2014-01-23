#
# File: LicensedUsedReport.py
# Author: Paul Hirst, Code 42 Software
# Last Modified: 12-02-2013
#
# This script outputs a single number of currently used licenses.
#
# Params:
# 1 arg - type of logging (values: verbose, nonverbose)
#
# Example usages: 
# python totalLicenseCount.py 1 
# The above example will show a verbose log.
#
# python totalLicenseCount.py noverbose 0
# The above exmaple will show terse logging
#
# NOTE: Make sure to set cpc_host, cpc_port, cpc_username, cpc_password to your environments values.
#

import sys

import json

import httplib

import base64

import math

import logging

import array


# verbose logging (set to DEBUG for additional console output)
cp_logLevel = "INFO"
if len(sys.argv)==1:
    cp_logLevel = str(sys.argv[1])

# Set to your environments vlaues
cpc_host = "localhost"
cpc_port = "4285"
cpc_username = "admin"
cpc_password = "admin"

#
# Compute base64 representation of the authentication token.
#
def getAuthHeader(u,p):

    # 

    token = base64.b64encode('%s:%s' % (u,p))

    return "Basic %s" % token
    

#
# Get the total number of licnesed users using an undocumented API call
#
def getLicensedUsers():

	logging.debug("Start - getLicensedUsers")
	
	headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json"}
	
	try:    
		conn = httplib.HTTPSConnection(cpc_host,cpc_port)
		conn.request("GET","/api/MasterLicense",None,headers)
		data = conn.getresponse().read()
		conn.close()
	except httplib.HTTPException as inst:

		logging.error("Exception: %s" % inst)

		return None

	except ValueError as inst:

		logging.error("Exception decoding JSON: %s" % inst)

		return None

	MasterLicense = json.loads(data)['data']

	return MasterLicense['seatsInUse']

	logging.debug("END - getLicensedUsers")
	
print 'Total Licensed Users:' + str(getLicensedUsers())
