#
# File: deactivateDevices.py
# Author: Nick Olmsted, Code 42 Software
# Last Modified: 03-08-2013
#
# Uses relativedelta python module that can be downloaded from:
# http://labix.org/python-dateutil
#
# Deactivates users based on the number of months since they have last connected to a master server
# Params:
# 1 arg - number of months (i.e 3)
# 2 arg - type of logging (values: verbose, nonverbose)
# 3 arg - set to deactivate devices or only print the devices that will be deactivated, but not deactivate them.
#        - values: deactivate, print
# Example usages: 
# python deactivateDevices.py 3 verbose print
# python deactivateDevices.py 3 noverbose deactivate
#
# NOTE: Make sure to set cpc_host, cpc_port, cpc_username, cpc_password to your environments values.
#

import sys

import json

import httplib

import base64

import math

import calendar

import logging

from dateutil.relativedelta import *

from datetime import *

# Number of Months of no backup (should be a number)
MAX_NUM_OF_MONTHS = str(sys.argv[1])

# verbose logging (should be text with words "verbose" or "noverbose")
VERBOSE_LOGGING = str(sys.argv[2])

# Deactivate devices (should be text that equals "deactivate")
RUN_DEACTIVATION_SCRIPT = str(sys.argv[3])

MAX_PAGE_NUM = 250
NOW = datetime.now()

# Set to your environments vlaues
# Note: do not include http or http in the cpc_host environment variable
cpc_host = "<HOST OR IP ADDRESS>"
cpc_port = "<PORT>"

cpc_username = "<username"
cpc_password = "<pw>"

#
# Compute base64 representation of the authentication token.
#
def getAuthHeader(u,p):

    # 

    token = base64.b64encode('%s:%s' % (u,p))

    return "Basic %s" % token

#
# Get the total page count that is used to determine the number of GET requests needed to return all
# all of the devices since the API currently limits this call to return 250 devices. 
# Returns: total number of requests needed
#
def getDevicesPageCount():
    if (VERBOSE_LOGGING == "verbose"):
        print "BEGIN - getDevicesPageCount"
        logging.debug("BEGIN - getDevicesPageCount")

    headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json"}

    try:
        conn = httplib.HTTPSConnection(cpc_host,cpc_port)
        conn.request("GET","/api/Computer?pgNum=1&pgSize=1&incCounts=true&active=true",None,headers)
        data = conn.getresponse().read()
        conn.close()

        devices = json.loads(data)['data']
        totalCount = devices['totalCount']

        # num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
        numOfRequests = math.ceil(totalCount/MAX_PAGE_NUM)+1

        if (VERBOSE_LOGGING == "verbose"):
           print "numOfRequests: " + str(numOfRequests)
           print "END - getDevicesPageCount"
        return numOfRequests

    except httplib.HTTPException as inst:

        print "Exception: %s" % inst

        return None

    except ValueError as inst:

        print "Exception decoding JSON: %s" % inst

        return None

#
# Calls the API to get a list of active devices. Calls the API multiple times because the API limits the results to 250. 
# Loops through the devices and adds devices that are older than the month threshold (i.e. devices older than 3 months)
# Parameter: totalNumOfRequest - integrer that is used to determine the number of times the API needs to be called. 
# Returns: list of devices to be deactivated
# API: /api/Computer/
# API Params:
#   pgNum - pages through the results.
#   psSize - number of results to return per page. Current API max is 250 results.
#   incCounts - includes the total count in the result
#   active - return only active devices
#
def getDevices(totalNumOfRequests):

    logging.debug("BEGIN - getDevices")
    if (VERBOSE_LOGGING == "verbose"):
        print "BEGIN - getDevices"

    headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json"}

    currentRequestCount=0
    deactivateCount = 0
    deactivateList = []

    while (currentRequestCount <= totalNumOfRequests):

        logging.debug("BEGIN - getDevices - Building devices list request count: " + str(currentRequestCount))
        if (VERBOSE_LOGGING == "verbose"):
            print "BEGIN - getDevices - Building devices list request count: " + str(currentRequestCount)

        try:
            currentRequestCount = currentRequestCount + 1
            conn = httplib.HTTPSConnection(cpc_host,cpc_port)
            conn.request("GET","/api/Computer?pgNum=" + str(currentRequestCount) + "&pgSize=250&incCounts=true&active=true",None,headers)
            data = conn.getresponse().read()
            conn.close()
        except httplib.HTTPException as inst:

            print "Exception: %s" % inst

            return None

        except ValueError as inst:

            print "Exception decoding JSON: %s" % inst

            return None

        devices = json.loads(data)['data']
        for d in devices['computers']:
            # Get fields to compasre
            computerId = d['computerId']
            lastConnected = d['lastConnected']
            deviceName = d['name']
            # If last connected date is greater than month threshold than add device to deactivate list
            dtLastConnected = datetime.strptime(str(lastConnected)[:10], "%Y-%m-%d")
            comparedate = datetime(dtLastConnected.year, dtLastConnected.month, dtLastConnected.day)
            three_months = NOW+relativedelta(months=-3)
            if three_months > comparedate:
                if (VERBOSE_LOGGING == "verbose"):
                    try:
                        logging.debug("DEACTIVATE - device id: " + str(computerId) + " device name: " + str(deviceName) + " with last connected date of: " + str(lastConnected))
                        print "DEACTIVATE - device id: " + str(computerId) + " device name: " + str(deviceName) + " with last connected date of: " + str(lastConnected)
                    except:
                        #ignore name errors
                        pass
                deactivateCount = deactivateCount + 1
                deactivateList.append(d)
            else:
                if (VERBOSE_LOGGING == "verbose"):
                    logging.debug("IGNORE - device id: " + str(computerId) + " with last connected date of: " + str(lastConnected))
                    print "IGNORE - device id: " + str(computerId) + " with last connected date of: " + str(lastConnected)
        
        if (VERBOSE_LOGGING == "verbose"):
            logging.debug("END - getDevices - Building devices list request count: " + str(currentRequestCount))
            print "END - getDevices - Building devices list request count: " + str(currentRequestCount)
        else:
            logging.debug("Building devices list... request count:  " + str(currentRequestCount))
            print "Building devices list... request count:  " + str(currentRequestCount)

    if (VERBOSE_LOGGING == "verbose"):
        logging.debug("TOTAL Devices that are scheduled to be deactivated: " + str(deactivateCount))
        logging.debug("END - getDevices")
        print "TOTAL Devices that are scheduled to be deactivated: " + str(deactivateCount)
        print "END - getDevices"

    return deactivateList

#
# Prints out all devices that will be deactivated
#
def printDevices(devices):
    count = 0
    if (VERBOSE_LOGGING == "verbose"):
        logging.debug("BEGIN - printDevices")
        print "BEGIN - printDevices"

    logging.debug("The following devices will be deactivated as they have not connected in more than " + str(MAX_NUM_OF_MONTHS) + " months:")
    print "The following devices will be deactivated as they have not connected in more than " + str(MAX_NUM_OF_MONTHS) + " months:"
    for d in devices:
        count = count + 1
        try:
            logging.debug("device name: " + str(d['name']))
            print "device name: " + str(d['name'])
        except:
            #ignore any name exceptions
            pass

    if (VERBOSE_LOGGING == "verbose"):
        logging.debug("END - printDevices")
        print "END - printDevices"

    return count

#
# Calls the API to deactivate a single device
#
def deactivateDevice(computerId):

    headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json","Content-Type":"application/json"}

    try:

        conn = httplib.HTTPSConnection(cpc_host,cpc_port)

        conn.request("PUT","/api/ComputerDeactivation/" + str(computerId),None,headers)

        data = conn.getresponse().read()

        conn.close()

        # Since no response is returned from a PUT request as long as no exception is thrown we can assume the device was deactivated
        return "success"

    except httplib.HTTPException as inst:

        print "Exception in HTTP operations: %s" % inst

        return None

    except ValueError as inst:

        print "Exception decoding JSON: %s" % inst

        return None

#
# Returns logging levels based on passed in argument
#
def getLoggingLevel():
    logging.basicConfig(filename='deactivateDevices.log',level=logging.DEBUG, format='%(asctime)s %(message)s')

#
# Deactivates devices if argument is set to deacivate
#
def deactivateDevices():
    logging.debug("START - DeactivateDevices")

    if (VERBOSE_LOGGING == "verbose"):
        logging.debug("BEGIN - deactivateDevices")
        print "BEGIN - deactivateDevices"

    pageCount = getDevicesPageCount()
    devices = getDevices(pageCount)
    deviceCount = printDevices(devices)

    count = 0
    # Deactivate devices
    if (RUN_DEACTIVATION_SCRIPT == "deactivate"):
        logging.debug("RUN_DEACTIVATION_SCRIPT set to true")
        print "RUN_DEACTIVATION_SCRIPT set to true"

        for d in devices:
            succ = deactivateDevice(d["computerId"])
            try:
                if succ:
                    count = count + 1
                    logging.debug("Deactivation successful for id: " + str(d["computerId"]) + " device name: " + str(d["name"]))
                    print "Deactivation successful for id: " + str(d["computerId"]) + " device name: " + str(d["name"])
                else:
                    logging.debug("Deactivation unsuccessful for id: " + str(d["computerId"]) + " device name: " + str(d["name"]))
                    print "Deactivation unsuccessful for id: " + str(d["computerId"]) + " device name: " + str(d["name"])
            except:
                #ignore any name errors
                pass
    else:
        logging.debug("RUN_DEACTIVATION_SCRIPT set to false")
        print "RUN_DEACTIVATION_SCRIPT set to false"

    logging.debug("TOTAL devices schdeuled to be deactivated: " + str(deviceCount))
    logging.debug("TOTAL devices deactivated: " + str(count))
    print "TOTAL devices schdeuled to be deactivated: " + str(deviceCount)
    print "TOTAL devices deactivated: " + str(count)

    if (VERBOSE_LOGGING == "verbose"):
        logging.debug("END - deactivateDevices")
        print "END - deactivateDevices"

    logging.debug("END - DeactivateDevices")

getLoggingLevel()
deactivateDevices()
