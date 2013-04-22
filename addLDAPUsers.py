#
# File: addLDAPUsers.py
# Author: Nick Olmsted, Code 42 Software
# Last Modified: 04-22-2013
#
# Takes a comma-delimited CSV file of user names and adds those users to a LDAP Org.
# 
# Python 2.7
# REQUIRED MODULE: Requests
#
# API Call: POST api/User
#
# Arguments: orgId, username
#

import sys

import json

import base64

import logging

import csv

import requests

# Set to your environments values
#cp_host = "<HOST OR IP ADDRESS>"
#cp_port = "<PORT>"
#cp_username = "<username>"
#cp_password = "<pw>"

#cp_ldap_orgId = "<Org Id>"
#cp_csv_file_name = "<filename.csv>"
cp_api = "/api/user"

#
# Compute base64 representation of the authentication token.
#
def getAuthHeader(u,p):

    token = base64.b64encode('%s:%s' % (u,p))

    return "Basic %s" % token

#
# Sets logger
#
def setLoggingLevel():
    logging.basicConfig(filename='addLDAPUsers.log',level=logging.DEBUG, format='%(asctime)s %(message)s')

#
# Adds the user to the LDAP Org. Returns true if API call was successful
#
def addLDAPUser(userId, orgId):
    headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
    url = cp_host + ":" + cp_port + cp_api
    payload = {'orgId': orgId, 'username': userId}
    logging.debug("adding user: " + userId)
    r = requests.post(url, data=json.dumps(payload), headers=headers)

    logging.debug(r.text)
    print r.text

    return r.status_code == requests.codes.ok

#
# Reads CSV file that contains a comma-delimited list of LDAP users and adds the users through the API.
#
def addLDAPUsers():
    logging.debug('BEGIN - addLDAPUsers')
    count = 0
    try:
        with open(csv_file_name, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in csvreader:
                #print ', '.join(row)
                for item in row:
                    #print item
                    if (addLDAPUser(item, ldap_orgId)):
                        count = count + 1
    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    print "Total Users Added: " + str(count)
    logging.debug("Total Users Added: " + str(count))
    logging.debug('END - addLDAPUsers')

setLoggingLevel()
addLDAPUsers()
