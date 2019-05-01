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
# File: addLDAPUsers.py
# Author: Nick Olmsted, Code 42 Software
# Last Modified: 03-30-2015 by Todd Ojala. Environment variable names cp_ldap_orgId and cp_csv_file_name changed
# to ldap_orgId and csv_file_name to match the script below.
# Also added note to usage of cp_host, which must include http or https 
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

import getpass

global filename

# Set to your environments values
# Note: cp_host must include http or https in front of host name for script to function
cp_host = "http://172.16.233.142"
cp_port = "4280"
cp_username = "admin"
cp_password = getpass.getpass('Enter your CrashPlan console password: ') # You will be prompted to enter your password

cp_ldap_orgId = "4"
csv_file_name = "input.csv"
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
        with open(csv_file_name, 'rU') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in csvreader:
                #print ', '.join(row)
                for item in row:
                    #print item
                    if (addLDAPUser(item, cp_ldap_orgId)):
                        count = count + 1
    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, csvreader.line_num, e))

    print "Total Users Added: " + str(count)
    logging.debug("Total Users Added: " + str(count))
    logging.debug('END - addLDAPUsers')

setLoggingLevel()
addLDAPUsers()
