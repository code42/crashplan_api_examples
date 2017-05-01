# Copyright (c) 2016, 2017 Code42, Inc.

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

# File: c42SharedLibrary.py
# Last Modified: 05-01-2017
#   Modified By: Paul H.

# Author: AJ LaVenture
# Author: Paul Hirst
# Author: Hank Brekke
# Author: Jack Phinney
#
# Common and reused functions to allow for rapid script creation
#
# install pip
# sudo pip install requests
# sudo pip install python-dateutil [-update]


import math
import sys
import json
import csv
import base64
import logging
import requests
import math
from dateutil.relativedelta import *
import datetime
import calendar
import re
import getpass
import os

class c42Lib(object):

    cp_c42Lib_version = '1.5.2'.split('.')

    # Set to your environments values
    #cp_host = "<HOST OR IP ADDRESS>" ex: http://localhost or https://localhost
    #cp_port = "<PORT>" ex: 4280 or 4285
    #cp_username = "<username>"
    #cp_password = "<pw>"

    # Test values
    #cp_host = "http://localhost"
    #cp_port = "4280"
    #cp_username = "admin"
    #cp_password = "admin"
    #cp_magic_restoreRecordKey = '987db1c5-8840-41f1-8c97-460d03347895'

    # REST API Calls

    cp_api_restoreHistory = "/api/restoreHistory"
    #?pgNum=1&pgSize=50&srtKey=startDate&srtDir=desc&days=9999&orgId=35
    cp_api_archive = "/api/Archive"
    cp_api_archiveMetadata = "/api/ArchiveMetadata"
    cp_api_authToken = "/api/AuthToken"
    cp_api_cli = "/api/cli"
    cp_api_coldStorage = "/api/ColdStorage"
    cp_api_computer = "/api/Computer"
    cp_api_computerBlock = "/api/ComputerBlock"
    cp_api_dataKeyToken = "/api/DataKeyToken"
    cp_api_deacivateDevice = "/api/ComputerDeactivation"
    cp_api_deactivateUser = "/api/UserDeactivation"
    cp_api_destination = "/api/Destination"
    cp_api_deviceBackupReport = "/api/DeviceBackupReport"
    cp_api_deviceUpgrade = "/api/DeviceUpgrade"
    cp_api_ekr = "/api/EKR"
    cp_api_fileContent = "/api/FileContent"
    cp_api_fileMetadata = "/api/FileMetadata"
    cp_api_legaHold = "/api/LegalHold"
    cp_api_legalHoldMembership = "/api/LegalHoldMembership"
    cp_api_legalHoldMembershipDeactivation = "/api/LegalHoldMembershipDeactivation"
    cp_api_loginToken = "/api/LoginToken"
    cp_api_networkTest = "/api/NetworkTest"
    cp_api_org = "/api/Org"
    cp_api_orgDeactivation = "/api/OrgDeactivation"
    cp_api_orgSettings = "/api/OrgSettings"
    cp_api_ping = "/api/Ping"
    cp_api_plan = "/api/Plan"
    cp_api_pushRestoreJob = "/api/PushRestoreJob"
    cp_api_restoreRecord = "/api/RestoreRecord"
    cp_api_server = "/api/Server"
    cp_api_smartsearch = "/api/SmartSearch"
    cp_api_storage = "/api/Storage"
    cp_api_storageAuthToken = "/api/StorageAuthToken"
    cp_api_storedBytesHistory = "/api/StoredBytesHistory"
    cp_api_storePoint = "/api/StorePoint"
    cp_api_user = "/api/User"
    cp_api_userMoveProcess = "/api/UserMoveProcess"
    cp_api_userRole = "/api/UserRole"
    cp_api_webRestoreJob = "/api/WebRestoreJob"
    cp_api_webRestoreJobResult = "/api/WebRestoreJobResult"
    cp_api_webRestoreSearch = "/api/WebRestoreSearch"
    cp_api_webRestoreSession = "/api/WebRestoreSession"
    cp_api_webRestoreTreeNode = "/api/WebRestoreTreeNode"
    cp_api_ekr = "/api/EKR"
    cp_api_legalHoldMembershipSummary = "/api/LegalHoldMembershipSummary"
    cp_api_legalHoldMembership = "/api/LegalHoldMembership"
    cp_api_legalHoldMembershipDeactivation = "/api/LegalHoldMembershipDeactivation"
    cp_api_plan = "/api/Plan"


    # Overwrite `cp_authorization` to use something other than HTTP-Basic auth.
    cp_authorization = None
    cp_logLevel = "INFO"
    cp_logFileName = "c42SharedLibrary.log"
    MAX_PAGE_NUM = 250
    cp_verify_ssl = False


    #
    # getRequestHeaders:
    # Returns the dictionary object containing headers to pass along with all requests to the API,
    #
    # Params:
    # login_token (kwargs): use login_token
    # auth_token (kwargs): use auth token
    #
    # Uses global / class variables for username and password authentication if 'auth_token' or 'login_token'
    # are not passed in as type
    #
    @staticmethod
    def getRequestHeaders(**kwargs):
        header = {}

        if not c42Lib.cp_authorization:
            if kwargs and 'login_token' in kwargs:
                logging.info("---- headers eval = login_token ----")
                header["Authorization"] = "login_token {0}".format(kwargs['login_token'])
            elif kwargs and 'auth_token' in kwargs:
                logging.info("---- headers eval = auth_token ----")
                header["Authorization"] = "token {0}".format(kwargs['auth_token'])
            else:
                logging.info("---- headers eval = create basic_auth ----")
                header["Authorization"] = c42Lib.getAuthHeader(c42Lib.cp_username,c42Lib.cp_password)
        else:
            logging.info("---- headers eval = use current basic auth ----")
            header['Authorization'] = c42Lib.cp_authorization

        header["Content-Type"] = "application/json"

        # logging.info("-getRequestHeaders: " + str(header))
        return header

    #
    # getRequestUrl(cp_api):
    # Returns the full URL to execute an API call,
    # Params:
    # cp_api: what the context root will be following the host and port (global / class variables)
    # host (kwargs): host address to use when building request url. Uses global / class variables by default
    # port (kwargs): port to use when bulding request url. Uses global / class variables by default
    #
    @staticmethod
    def getRequestUrl(cp_api, **kwargs):
        host = ''
        port = ''

        if kwargs and 'host' in kwargs:
            host = kwargs['host']
        else:
            host = c42Lib.cp_host

        if kwargs and 'port' in kwargs:
            port = str(kwargs['port'])
        else:
            port = c42Lib.cp_port


        if port == '':           # Some customers have port forwarding and adding a port breaks the API calls
            url = host+ cp_api
        else:
            url = host + ":" + str(port) + cp_api

        return url

    #
    # executeRequest(type, cp_api, params, payload):
    # Executes the request to the server based on type of request
    # Params:
    # type: type of rest call: valid inputs: "get|delete|post|put" - returns None if not specified
    # cp_api: the context root to be appended after server:port when generating the URL
    # params: URL parameters to be passed along with the request
    # payload: json object to be sent in the body of the request
    # host (kwargs): host address to target request at. Uses global / class variables by default
    # port (kwargs): port to target request at. Uses global / class variables by default
    # auth_token (kwargs): auth type to use. Uses basic auth with global username and password by default
    # login_token (kwargs): token to use based on auth type. Unused by default.

    # Returns: the response object directly from the call to be parsed by other methods
    #

    @staticmethod
    def executeRequest(type, cp_api, params={}, payload={}, **kwargs):

        requests.packages.urllib3.disable_warnings()
        #logging.getLogger("urllib3").setLevel(logging.warning)
        
        header = c42Lib.getRequestHeaders(**kwargs)
        url = c42Lib.getRequestUrl(cp_api, **kwargs)

        # for our purposes, we always want this set for fileContent requests so that a restore record
        # is not stamped out on the server
        if cp_api == c42Lib.cp_api_fileContent:
            assert 'restoreRecordKey' in params and params['restoreRecordKey'] is cp_magic_restoreRecordKey

        try:
            if type == "get":
                logging.debug("Payload : " + str(payload))
                r = requests.get(url, params=params, data=json.dumps(payload), headers=header, verify=c42Lib.cp_verify_ssl)
                logging.debug(r.text)
                return r
            elif type == "delete":
                r = requests.delete(url, params=params, data=json.dumps(payload), headers=header, verify=c42Lib.cp_verify_ssl)
                logging.debug(r.text)
                return r
            elif type == "post":
                r = requests.post(url, params=params, data=json.dumps(payload), headers=header, verify=c42Lib.cp_verify_ssl)
                logging.debug(r.text)
                return r
            elif type == "put":
                r = requests.put(url, params=params, data=json.dumps(payload), headers=header, verify=c42Lib.cp_verify_ssl)
                logging.debug(r.text)
                return r
            else:
                return None
        except requests.exceptions.RequestException as e:
            return e


    #
    # getRequestHeaders:
    # Returns the dictionary object containing headers to pass along with all requests to the API,
    # Params: None
    # Uses global / class variables for username and password authentication
    #
    @staticmethod
    def getGenericRequestHeaders(username,password):
        header = {}
        header["Authorization"] = c42Lib.getAuthHeader(username,password)
        header["Content-Type"] = "application/json"

        # print header
        return header

    #
    # getRequestUrl(cp_api):
    # Returns the full URL to execute an API call,
    # Params:
    # cp_api: what the context root will be following the host and port (global / class variables)
    #

    @staticmethod
    def getGenericRequestUrl(url,port,apiCall):
        if port  == '':           # Some customers have port forwarding and adding a port breaks the API calls
            url = url + apiCall
        else: 
            url = url + ":" + str(port) + apiCall

        return url

    #
    # executeRequest(type, cp_api, params, payload):
    # Executes the request to the server based on type of request
    # Params:
    # type: type of rest call: valid inputs: "get|delete|post|put" - returns None if not specified
    # cp_api: the context root to be appended after server:port when generating the URL
    # params: URL parameters to be passed along with the request
    # payload: json object to be sent in the body of the request
    # Returns: the response object directly from the call to be parsed by other methods
    #

    @staticmethod
    def executeGenericRequest( username, password, type, api_URL, api_Port, apiCall ,params, payload):
        # logging.debug
        header = c42Lib.getGenericRequestHeaders(username,password)
        # print header
        url = c42Lib.getGenericRequestUrl(api_URL,api_Port,apiCall)
        # url = cp_host + ":" + cp_port + cp_api
        # payload = cp_payload
        #print url
        #raw_input()
        if type == "get":
            logging.debug("Payload : " + str(payload))
            r = requests.get(url, params=params, data=json.dumps(payload), headers=header, verify=False)
            #print r.text
            #raw_input()
            logging.debug(r.text)
            return r
        elif type == "delete":
            r = requests.delete(url, params=params, data=json.dumps(payload), headers=header, verify=False)
            logging.debug(r.text)
            return r
        elif type == "post":
            r = requests.post(url, params=params, data=json.dumps(payload), headers=header, verify=False)
            logging.debug(r.text)
            return r
        elif type == "put":
            # logging.debug(str(json.dumps(payload)))
            r = requests.put(url, params=params, data=json.dumps(payload), headers=header, verify=False)
            logging.debug(r.text)
            return r
        else:
            return None

        # content = r.content
        # binary = json.loads(content)
        # logging.debug(binary)


    # Validates User Credentials by trying to look up the user's own info based on their username.deviceList = c42Lib.getDevicesCustomParams(currentPage,params)

    @staticmethod
    def validateUserCredentials():

        # Check if username/password combination is valid

        isValidUser = False

        params = {}
        params['username'] = c42Lib.cp_username

        getUserInfo = c42Lib.getUser(params)

        if getUserInfo is not None:
            isValidUser = True

        return isValidUser

    #
    # KWARGS: cp_enterUserName - manually entered username & password,cp_userName - hardcoded username ,cp_useCustomerCredFile - use credentials file ,cp_credentialFile - name of credentials file
    # Returns: True once authentication parameters are entered.  Does not verify these are valid for the script.
    #
    @staticmethod
    def authenticateUser(**kwargs):

        logging.debug ("=========== Authenticate User")

        cp_enterUserName = False
        cp_useCustomerCredFile = False
        userInfoSet = False
        warningText = False
        userAuthType = 'Hardcoded'

        if not kwargs:
            kwargs = False

        if kwargs:
            
            # If no KWARGS it will use hardcoded values.
            
            if ('cp_userName' in kwargs):
                print "Entered Username..."
                c42Lib.cp_username = kwargs['cp_userName']
                cp_userName = kwargs['cp_userName']
                cp_enterUserName = True
                userAuthType = 'Manually Entered'
                warningText = ''
            else:
                print "Did not enter username..."
                cp_enterUserName = False
                warningText = 'Check Entered userName'
                # cp_userName = c42Lib.cp_username

            if ('cp_credentialFile' in kwargs):
                print "Using credentials file..."
                cp_credentialFile = kwargs['cp_credentialFile']
                cp_useCustomerCredFile = True
            else:
                warningText = ''

        # end if

        if cp_useCustomerCredFile: # If using a credentials file

            print "Looking for credentials file..."
            
            with open(str(c42Lib.getFilePath(cp_credentialFile))) as f:
                c42Lib.cp_username = base64.b64decode(f.readline().strip())
                c42Lib.cp_password = base64.b64decode(f.readline().strip())

            userAuthType = 'Credentials File'
            userInfoSet = True

        if cp_enterUserName:

            print ""
            c42Lib.cp_password = getpass.getpass('=========== Please enter the password for user ' + str(c42Lib.cp_username) + ' : ')
            c42Lib.cp_username = cp_userName

            userAuthType = 'Entered Password'
            userInfoSet= True

        if userAuthType == 'Hardcoded':

            if c42Lib.cp_username == 'admin':
                print ""
                print "Username is set to 'admin'!  If this is really your username you should change it."
                print ""
                raw_input("Please press 'Enter' to proceed.")
                print ""

            else:
                print "Username has been hardcoded to : " + c42Lib.cp_username

            if c42Lib.cp_password == 'admin':
                print ""
                print "Username is set to 'admin'!  If this is really your password you should change it."
                print ""
                raw_input("Please press 'Enter' to proceed.")
                print ""
            else:
                print "Password has been hardcoded.  Not shown."

            userInfoSet = True
            
        if warningText != '' and not userInfoSet:
            print ""
            print "**********"
            print "********** " + warningText
            print "**********"
            print ""

        if userInfoSet:
            return userAuthType
        else:
            return userInfoSet


    #
    # Params: cp_serverInfoFile,cp_serverInfoFileName,cp_serverEntryFlag,cp_serverHostURL,cp_serverHostPort
    # Returns: True once authentication parameters are entered.  Does not verify these are valid for the script.
    #
    @staticmethod
    def cpServerInfo(**kwargs):

        logging.debug ("=========== Set CP Server Info")

        serverInfoType     = 'Hardcoded'
        warningText        = ''
        cp_serverInfoFile  = False
        cp_serverEntryFlag = False 

        if kwargs:
            
            # If no KWARGS it will use 'admin'/'admin' and proceed.
            
            if ('cp_serverHostURL' in kwargs) and ('cp_serverHostPort' in kwargs):
                cp_serverHostURL  = kwargs['cp_serverHostURL']
                cp_serverHostPort = kwargs['cp_serverHostPort']
                cp_serverEntryFlag = True
            else:
                cp_serverEntryFlag = False
                warningText = 'Check Server URL & Port (no colon between URL & port)'
                cp_serverHostURL  = c42Lib.cp_host
                cp_serverHostPort = c42Lib.cp_port

            if ('cp_serverInfoFileName' in kwargs) and not cp_serverEntryFlag:
                cp_serverInfoFileName = kwargs['cp_serverInfoFileName']
                cp_serverInfoFile = True
            elif not cp_serverEntryFlag:
                cp_serverInfoFile = False
                warningText = 'Check Server File Info'
                cp_serverInfoFileName = ''

        # end if

        if cp_serverInfoFile: # If using a credentials file
            
            with open(str(c42Lib.getFilePath(cp_serverInfoFileName))) as f:
                c42Lib.cp_host = f.readline().strip()
                c42Lib.cp_port = f.readline().strip()

            serverInfoType = 'Server Info File'

        if cp_serverEntryFlag:

            print ""
            c42Lib.cp_host = cp_serverHostURL
            c42Lib.cp_port = cp_serverHostPort

            serverInfoType = 'Manually Entered'

        canConnect = False
        canConnect = c42Lib.reachableNetworkTest(c42Lib.cp_host)

        if not canConnect:
            serverInfoType = False
            warningText = 'Connection to ' + str(c42Lib.cp_host)+":"+str(c42Lib.cp_port)+" Failed."

        if warningText != '' and not serverInfoType:
            print ""
            print "**********"
            print "********** " + warningText
            print "**********"
            print ""
            sys.exit(1)

        return serverInfoType


    #
    # Params:
    # private address: address to check if reachbale
    # Returns: Check if address is reachable. None on failure
    #
    @staticmethod
    def URLPing(private_address):

        r = c42Lib.executeRequest("get", c42Lib.cp_api_ping, {}, {})

        contents = r.content.decode("UTF-8")
        binary = json.loads(contents)
        return binary['data'] if 'data' in binary else None

    #
    # Params:
    # private address: address to check if reachbale
    # Returns: Check if address is reachable. None on failure
    #
    @staticmethod
    def reachableNetworkTest(private_address, **kwargs):

        print ""
        print "Testing Connection to " + str(private_address)
        print ""

        connectionGood = False

        # strip off http or https if testing connectivity to URL that's more than a ping.
        if private_address[:5] == "https":
            private_address = private_address[8:]
        if private_address[:4] == "http":
            private_address = private_address[7:]

        payload = {
            "testType":"reachable",
            "address":private_address,
            "privateAddress":True
        }

        r = c42Lib.executeRequest("post", c42Lib.cp_api_networkTest, {}, payload, **kwargs)

        try:
            contents = r.content.decode("UTF-8")
            binary = json.loads(contents)
            binary['data'] if 'data' in binary else None

            print ""
            print "Connection to " + str(private_address) + " appears to be valid."
            print ""

            return binary

        except AttributeError:

            print ""
            print "Connection to " + str(private_address) + " does not appear to be valid."
            print ""

            return False


    # params:
    # 
    @staticmethod
    def requestLoginToken(**kwargs):
        logging.info("requestLoginToken: " + str(kwargs))
        payload = {}
        if kwargs and ('userId' in kwargs) and ('sourceGuid' in kwargs) and ('destinationGuid' in kwargs):
            payload['userId'] = str(kwargs['userId'])
            payload['sourceGuid'] = str(kwargs['sourceGuid'])
            payload['destinationGuid'] = str(kwargs['destinationGuid'])
        else:
            return None
        
        try:
            r = c42Lib.executeRequest("post", c42Lib.cp_api_loginToken, {}, payload, **kwargs)
            contents = r.content.decode("UTF-8")
            binary = json.loads(contents)
            logging.info("requestLoginToken Response: " + str(contents))
            return binary['data']['loginToken'] if 'data' in binary else None
        except KeyError:
            return None


    #
    # Params:
    # host (kwargs): host location to use
    # port (kwargs): port to use
    # login_token (kwargs): necessary for storage nodes
    # Returns: Auth token. None on failure
    #
    @staticmethod
    def requestAuthToken(**kwargs):
        logging.info("^^^^^^^^^^^ requestAuthToken: start" + str(kwargs))
        payload = {
            "sendCookieHeader":True
        }
        r = c42Lib.executeRequest("post", c42Lib.cp_api_authToken, {}, payload, **kwargs)
        if r.status_code != 200:
            logging.debug("Failed to get auth token")
            return None

        logging.info("requestAuthToken Response: " + r.content)
        return "-".join(json.loads(r.content.decode("UTF-8"))['data'])

    #
    # Params:
    # computer_Guid: guid to get datakey for
    # host (kwargs): host location to use
    # port (kwargs): port to use
    # auth_token (kwargs): auth_token to use
    # Returns: Datakey. None on failure
    #
    @staticmethod
    def getDataKeyToken(computerGuid, **kwargs):
        params = {}
        payload = {'computerGuid': computerGuid}
        r = c42Lib.executeRequest("post", c42Lib.cp_api_dataKeyToken, params, payload, **kwargs)
        # print "========== r below "
        # print r
        # print "========== binary below"
        if r.status_code != 200:
            return False
        else: 
            binary = json.loads(r.content.decode('UTF-8'))
            # print "========== end of get datakeytoken"
            return binary['data']['dataKeyToken'] if 'data' in binary else None

    #
    # Params:
    # computer_Guid: guid to start a session for
    # datakeytoken: data key token to use
    # host (kwargs): host location to use
    # port (kwargs): port to use
    # auth_token (kwargs): auth_token to use
    # Returns: Session information. None on failure
    #
    @staticmethod
    def startWebRestoreSession(computerGuid, dataKeyToken, **kwargs):
        payload = {
            "computerGuid":computerGuid,
            "dataKeyToken":dataKeyToken
        }
        r = c42Lib.executeRequest("post", c42Lib.cp_api_webRestoreSession, {}, payload, **kwargs)
        if r.status_code != 200:
            logging.debug("Failed to get web restore session")

            return None

        return json.loads(r.content.decode("UTF-8"))['data']

    #
    # Params:
    # session_id: sessionId to use for search
    # guid: guid to use for search
    # timestamp: timestamp to use for search
    # regex: regex to search for
    # host (kwargs): host location to use
    # port (kwargs): port to use
    # auth_token (kwargs): auth_token to use
    # Returns: Search results. None on failure
    #
    @staticmethod
    def requestWebRestoreSearch(session_id, guid, timestamp, regex, **kwargs):
        params = {}
        params['webRestoreSessionId'] = session_id
        params['guid'] = guid
        params['timestamp'] = timestamp
        params['regex'] = regex
        payload = {}
        r = c42Lib.executeRequest("get", c42Lib.cp_api_webRestoreSearch, params, payload, **kwargs)
        binary = json.loads(r.content.decode('UTF-8'))
        return binary['data'] if 'data' in binary else None

    #
    # Params:
    # planUid: plan to get auth token for
    # destinationGuid: destination to get auth token for
    # Returns: Storage auth token on success, None on failure
    #
    @staticmethod
    def requestStorageAuthToken(planUid, destinationGuid, **kwargs):
        payload = {
            "planUid":planUid,
            "destinationGuid":destinationGuid
        }

        r = c42Lib.executeRequest("post", c42Lib.cp_api_storageAuthToken, {}, payload, **kwargs)
        if r.status_code != 200:
            logging.debug("Failed to get storage auth token")
            return None

        return json.loads(r.content.decode("UTF-8"))['data']

    #
    # Params:
    # planUid: planUid to download from
    # filepath: path to download
    # host (kwargs): host location to use
    # port (kwargs): port to use
    # auth_token (kwargs): auth_token to use
    # Returns: File content. None on failure
    #
    @staticmethod
    def getFileContentByFilePath(planUid, filepath, **kwargs):
        params = {}
        params['path'] = filepath
        params['restoreRecordKey'] = c42Lib.cp_magic_restoreRecordKey
        params['zipFolderContents'] = True
        r = c42Lib.executeRequest("get", c42Lib.cp_api_fileContent + "/" + planUid, params, {}, **kwargs)
        if r.status_code != 200:
            return None
        return r.content


    #
    # Params:
    # planUid: planUid to metadata from
    # filepath: path to get metadata for
    # host (kwargs): host location to use
    # port (kwargs): port to use
    # auth_token (kwargs): auth_token to use
    # Returns: File content. None on failure
    #
    @staticmethod
    def getFileMetadataByFilePath(planUid, filepath, **kwargs):
        params = {}
        params['path'] = filepath
        r = c42Lib.executeRequest("get", c42Lib.cp_api_fileMetadata + "/" + planUid, params, {}, **kwargs)
        if r.status_code != 200:
            return None
        return r.content


    #
    # Params:
    # planUid: planUid to download from
    # fileid: fileId to download
    # host (kwargs): host location to use
    # port (kwargs): port to use
    # auth_token (kwargs): auth_token to use
    # Returns: File content. None on failure
    #
    @staticmethod
    def getFileContentByFileId(planUid, file_id, **kwargs):
        params = {}
        params['restoreRecordKey'] = c42Lib.cp_magic_restoreRecordKey
        params['zipFolderContents'] = True
        r = c42Lib.executeRequest("get", c42Lib.cp_api_fileContent + "/" + planUid + "/" + file_id, params, {}, **kwargs)
        if r.status_code != 200:
            return None
        return r.content

         #
    # Params:
    # planUid: planUid to metadata from
    # fileid: fileId to get metadata for
    # host (kwargs): host location to use
    # port (kwargs): port to use
    # auth_token (kwargs): auth_token to use
    # Returns: File content. None on failure
    #
    @staticmethod
    def getFileMetadataByFileId(planUid, file_id, **kwargs):
        r = c42Lib.executeRequest("get", c42Lib.cp_api_fileMetadata + "/" + planUid + "/" + file_id, {}, {}, **kwargs)
        binary = json.loads(r.content.decode("UTF-8"))
        if 'data' in binary:
            return binary['data']
        else:
            return None




    #
    # Params:
    # sourceComputerGuid: guid to get backup plans for
    # host (kwargs): host location to use
    # port (kwargs): port to use
    # auth_token (kwargs): auth_token to use
    # Returns: Backup plans for guid located at host:port. None on failure
    #
    @staticmethod
    def getBackupPlans(sourceComputerGUID, **kwargs):
        params = {
            "sourceComputerGuid":sourceComputerGUID,
            "planTypes":"BACKUP"
        }
        r = c42Lib.executeRequest("get", c42Lib.cp_api_plan, params, {}, **kwargs)
        binary = json.loads(r.content.decode("UTF-8"))
        if 'data' in binary:
            return binary['data']
        else:
            return None

    #
    #  Params:
    #  planUid: planUid to get storage information about
    #  Returns: storage information based on passed in planUid or None on failure
    #
    @staticmethod
    def getStorageInformationByPlanUid(planUid, **kwargs):
        r = c42Lib.executeRequest("get", c42Lib.cp_api_storage +"/"+planUid, {}, {}, **kwargs)
        binary = json.loads(r.content.decode("UTF-8"))
        if 'data' in binary:
            return binary['data']
        else:
            return None

    #
    #  Returns: destinations know by server or None on failure
    #
    @staticmethod
    def getDestinations(**kwargs):
        logging.info("getDestinations")
        r = c42Lib.executeRequest("get", c42Lib.cp_api_destination, {}, {}, **kwargs)
        logging.debug(r.text)
        content = r.content.decode("UTF-8")
        binary = json.loads(content)
        return binary['data']['destinations'] if 'data' in binary else None

    #
    #  Returns: destination know by server or None on failure
    #
    @staticmethod
    def getDestinationById(id, **kwargs):
        logging.info("getDestinationById")

        if not kwargs:
            params = {}
        else:
            params = kwargs['params']
            kwargs = {}


        r = c42Lib.executeRequest("get", c42Lib.cp_api_destination + "/" + str(id), params, {}, **kwargs)
        logging.debug(r.text)
        content = r.content.decode("UTF-8")
        binary = json.loads(content)
        return binary['data'] if 'data' in binary else None



    # getServersByDestinationId(destinationId, **kwargs):
    # returns the servers in a given destination
    # Note that the API uses 'nodeId' for serverId
    # params:
    # destinationId: id of destination
    #

    @staticmethod
    def getServersByDestinationId(destinationId, **kwargs):
        logging.info("getServers({0})".format(destinationId))
        params = {}
        params['destinationId'] = destinationId
        r = c42Lib.executeRequest("get", c42Lib.cp_api_server, params, {}, **kwargs)
        logging.debug(r.text)
        content = r.content.decode("UTF-8")
        binary = json.loads(content)
        return binary['data']['servers'] if 'data' in binary else None



    # getStorePointsByServerId(severId):
    # returns the storpoints on a given server
    # Note that the API uses 'nodeId' for serverId
    # params:
    # storePointId: id of storePoint
    #

    @staticmethod
    def getStorePointsByServerId(serverId):
        logging.info("getStorePointsByServerId-params:serverId[" + str(serverId) + "]")


        storePoint = ""
        params = {}
        payload = {}
        params['nodeId'] = serverId

        r = c42Lib.executeRequest("get", c42Lib.cp_api_storePoint, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        storePoint = binary['data']

        return storePoint if 'data' in binary else None

    @staticmethod
    def getUser(params):
        logging.info("getUser-params:params[" + str(params) + "]")

        if params:
            payload = {}

            r = c42Lib.executeRequest("get", c42Lib.cp_api_user, params, payload)

            logging.debug(r.text)
            content = r.content
            r.content
            binary = json.loads(content)

            logging.debug(binary)

            try:
                return binary['data']['users']

            except TypeError:
                
                return None

            # binary['data']['users'][0]['userUid']
        
        else:
        
            return None
        



#
    # getUserById(userId):
    # returns the user json object of the requested userId
    # params:
    # userId: the id of the user within the system's database
    #
    @staticmethod
    def getUserById(userId,**kwargs):
        logging.info("getUser-params:userId[" + str(userId) + "]")

        params = {}
        if kwargs:
            params = kwargs
        else:
            params['incAll'] = 'true'
            params['idType'] = 'uid' # Needed for the 4.x series and beyond

        payload = {}

        logging.debug("cp_api_user/" + str(userId)+"/"+str(params)+" [payload] : " + str(payload))
        r = c42Lib.executeRequest("get", c42Lib.cp_api_user + "/" + str(userId), params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        try:
            logging.debug("[data] : " + str(binary['data']))
            user = binary['data']
        except TypeError:

            logging.info("There was an error getting the user [ " + str(userId) + " ] ")
            logging.info("This is the returned response : ")
            logging.info( binary )

            user = False

        return binary

    @staticmethod
    def getUserByMy():
        logging.info("getUserByMy")

        r = c42Lib.executeRequest("get", c42Lib.cp_api_user + "/my", {}, {})

        logging.debug(r.text)
        content = r.content.decode("UTF-8")
        binary = json.loads(content)
        return binary['data'] if 'data' in binary else None
    #
    # getUserByUserName(username):
    # returns the user json object of the requested username
    # params:
    # username: the username of the user within the system's database
    #
    @staticmethod
    def getUserByUserName(username):
        logging.info("getUser-params:username[" + str(username) + "]")

        params = {}
        params['username'] = username
        params['incAll'] = 'true'
        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_user, params, payload)

        logging.debug(r.text)

        content = r.content

        r.content

        binary = json.loads(content)
        logging.debug(binary)

        user = binary['data']

        binary_length = binary['data']['totalCount'] # Gets the number of users results returned

        if binary_length > 0:

            user = binary['data']['users'][0] # Returns the user info

        else:

            user = None # Returns null if nothing

        return user

    @staticmethod
    def getRestoreRecordByRestoreJobID(restoreId):
        r = c42Lib.executeRequest("get", c42Lib.cp_api_restoreRecord + "/" + str(restoreId), {}, {})
        content = r.content.decode("UTF-8")
        binary = json.loads(content)
        return binary

    #
    # getUsersByOrgPaged
    # Returns a list of active users within an orgization by page,
    # Params:
    # orgId - integer, that is used to limit the users to an org. Can be set to 0 to return all users.
    # pgNum - page request for user list (starting with 1)
    #
    @staticmethod
    def getUsersByOrgPaged(orgId, pgNum):
        logging.info("getUsersByOrgPaged-params:orgId[" + str(orgId) + "]:pgNum[" + str(pgNum) + "]")

        # headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
        # url = cp_host + ":" + cp_port + cp_api_user
        params = {}
        params['orgId']        = orgId
        params['pgNum']        = str(pgNum)
        params['pgSize']       = str(c42Lib.MAX_PAGE_NUM)
        params['active']       = 'true'
        params['incChildOrgs'] = 'false'

        payload = {}
        logging.info(str(payload))
        # r = requests.get(url, params=payload, headers=headers)
        r = c42Lib.executeRequest("get", c42Lib.cp_api_user, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)


        users = binary['data']['users']
        return users

    #
    # getUsersPaged(pageNum):
    # Returns list of active users within the system based on page number
    # params:
    # pgNum - page request for user list (starting with 1)
    #
    @staticmethod
    def getUsersPaged(pgNum,params):
        logging.info("getUsersPaged-params:pgNum[" + str(pgNum) + "]")

        try:
            if not params['pgSize']:
                params['pgSize'] = str(c42Lib.MAX_PAGE_NUM)
        except:
            params['pgSize'] = str(c42Lib.MAX_PAGE_NUM)

        params['pgNum'] = str(pgNum)

        payload = {}

        # r = requests.get(url, params=payload, headers=headers)
        r = c42Lib.executeRequest("get", c42Lib.cp_api_user, params, payload)

        logging.debug(r.text)

        content = r.content.decode('UTF-8')
        binary = json.loads(content)
        logging.debug(binary)

        users = binary['data']['users']
        return users


    @staticmethod
    def getAllUsers():
        logging.info("getAllUsers")
        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.getUsersPaged(currentPage)
            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList

# getAllUsersActiveBackup():
# returns AllUser info + backup usage for active users
# - Jack Phinney

    @staticmethod
    def getAllUsersActiveBackup():
        logging.info("getAllUsersActiveBackup")
        currentPage = 1
        keepLooping = True
        fullList = []
        params={}
        params['incBackupUsage'] = True
        params['active'] = True
        while keepLooping:
            pagedList = c42Lib.getUsersPaged(currentPage,params)
            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    @staticmethod
    def generaticLoopUntilEmpty():
        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            # pagedList = c42Lib.getUsersPaged(currentPage)
            pagedList = c42Lib.getDevices(currentPage)
            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    @staticmethod
    def getAllUsersByOrg(orgId):
        logging.info("getAllUsersByOrg-params:orgId[" + str(orgId) + "]")
        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.getUsersByOrgPaged(orgId, currentPage)
            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList

    #
    # putUserUpdate(userId, idType payload):
    # updates a users information based on the payload passed
    # params:
    # userId - id for the user to update
    # idType - to specify idType for 4.2+ (uid is now the standard)
    # payload - json object containing name / value pairs for values to update
    # returns: user object after the update
    #

    @staticmethod
    def putUserUpdate(userId, idType, payload):
        logging.info("putUserUpdate-params:userId[" + str(userId) + "],payload[" + str(payload) + "]")

        if (payload is not None and payload != ""):
            params = {}
            params['idType'] = idType

            r = c42Lib.executeRequest("put", c42Lib.cp_api_user + "/" + str(userId), params, payload)
            logging.debug(str(r.status_code))
            content = r.content
            binary = json.loads(content)
            logging.debug(binary)
            user = binary['data']
            return user
            # if (r.status_code == 200):
                # return True
            # else:
                # return False
        else:
            logging.error("putUserUpdate param payload is null or empty")


    #
    # putUserDeactivate(userId, reactive):
    # Deactivates a user based in the userId passed
    # params:
    # userId - id for the user to update
    # deactivate - deactivates the user if true, re-activates if false
    # returns: user object after the update
    #

    @staticmethod
    def putUserDeactivate(userId, deactivate):
        logging.info("putUserDeactivate-params:userId[" + str(userId) + "],deactivate[" + str(deactivate) + "]")
        params = {}
        payload = {}
        if (userId is not None and userId != ""):
            if deactivate:
                r = c42Lib.executeRequest("put", c42Lib.cp_api_deactivateUser+"/"+str(userId), params, payload)
                logging.debug('Deactivate Call Status: '+str(r.status_code))
                if not (r.status_code == ""):
                    return True
                else:
                    return False
            else:
                r = c42Lib.executeRequest("delete", c42Lib.cp_api_deactivateUser+"/"+str(userId), params, payload)
                logging.debug('Deactivate Call Status: '+str(r.status_code))
                if not (r.status_code == ""):
                    return True
                else:
                    return False
        else:
            logging.error("putUserDeactivate has no userID to act on")


    #
    # postUserMoveProcess(userUid, orgUid):
    # posts request to move use into specified organization
    # params:
    # userUid - Uid of the user for the move request
    # orgUid - Uid of destination org for the user
    # returns: true if 204, respose object if 500, else false
    #
    # Changed from ids to uids in 4.3+

    @staticmethod
    def postUserMoveProcess(userUid, orgUid):
        logging.info("postUserMoveProcess-params:userUid[" + str(userUid) + "],orgUid[" + str(orgUid) + "]")

        params = {}
        payload = {}
        payload["userId"] = userUid
        payload["parentOrgId"] = orgUid

        r = c42Lib.executeRequest("post", c42Lib.cp_api_userMoveProcess, params, payload)
        logging.debug(r.status_code)

        if (r.status_code == 204):
            return True
        elif (r.status_code == 500):
            content = r.content
            binary = json.loads(content)
            logging.debug(binary)
            return False
        else:
            return False


    #
    # createOrg(newOrgInfo):
    # Creates a new orginization based on the information passed
    # params:
    # parentOrgId - id of the parent organization.  Will default to 2, which is assumed to be the default org
    # Returns:
    # 204?
    #

    @staticmethod
    def createOrg(params):
        logging.info("createOrg-params: a list of things")

        if params['parentOrgId'] is None:
            params['parentOrgId'] = "2"

        payload = {}

        r = c42Lib.executeRequest("post", c42Lib.cp_api_org + "/" + str(orgId), params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)
        
        if (r.status_code == 204):
            return True
        elif (r.status_code == 500):
            content = r.content
            binary = json.loads(content)
            logging.debug(binary)
            return False
        else:
            return False


    #
    # updateOrg(orgUid):
    # Updates Org values
    # params:
    # orgUid - id of the organization.
    # idType - should be orgUid, orgId is being deprecated

    @staticmethod
    def modifyOrg(**kwargs):
        logging.info("modifyOrg-orgId:" + str(kwargs))

        if kwargs:

            params  = {}
            payload = {}

            if kwargs['orgUid'] and kwargs['payload']:
                
                params['idType'] = 'orgUid'
                payload = {kwargs['payload']}

                r = c42Lib.executeRequest('put', c42Lib.cp_api_org + "/" + str(orgUid), params, payload)

                logging.debug(r.text)

                content = r.content
                binary = json.loads(content)
                logging.debug(binary)

                try:
                    orgData = binary['data']

                    return orgData

                except TypeError:

                    return int(r.status_code)

        else:

            return 500  # Didn't provide an action



    #
    # deactivateOrg(orgId):
    # Deactivates an orginization based orgId
    # params:
    # orgId - id of the organization.
    # Returns:
    # 201 - Deactivated?
    # 204 - Already Deactivated
    # 404 - Not Found

    @staticmethod
    def deactivateOrg(**kwargs):
        logging.info("deactivatedOrg-orgId:" + str(kwargs))

        params  = {}
        payload = {}

        action = ''

        if kwargs:
            if kwargs['action']:
                if kwargs['action'] =='reactivate':
                    action = 'delete'  # Reactivate org (or remove deactivation)

                if kwargs['action'] == 'deactivate':
                    action = 'put'     # Deactivate org

            if action == '':
                return 500 # No action was passed along so return error code 500

            if kwargs['orgId']:
                
                orgId = kwargs['orgId']

                r = c42Lib.executeRequest(action, c42Lib.cp_api_orgDeactivation + "/" + str(orgId), params, payload)

                logging.debug(r.text)

                content = r.content
                binary = json.loads(content)
                logging.debug(binary)
                
                return int(r.status_code)
                    # 201 - Deactivated?
                    # 204 - Already Deactivated
                    # 404 - Not Found

        else:

            return 500  # Didn't provide an action


    #
    # getOrg(orgId):
    # Returns all organization data for specified organization
    # params:
    # orgId - id of the organization you want to return
    # Returns:
    # json object
    #

    @staticmethod
    def getOrg(orgId,**kwargs):
        logging.info("getOrg-params:orgId[" + str(orgId) + "]")

        params = {}

        if not kwargs:
            params['incAll'] = 'true'
            params['idType'] = 'orgId'
        else:
            params = kwargs['params']

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_org + "/" + str(orgId), params, payload)

        logging.debug(r)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        try:
            if binary['data']:
                org = binary['data']

        except TypeError:

            org = None

        return org


    #
    # getOrgs(pgNum):
    # returns json list object of all users for the requested page number
    # params:
    # pgNum - page request for information (starting with 1)
    #

    @staticmethod
    def getOrgs(pgNum,**kwargs):
        logging.info("getOrgs-params:pgNum[" + str(pgNum) + "]")

        params = {}

        if kwargs:
            logging.info("getOrgs-params:kwargs[" + str(kwargs) + "]")

            if kwargs['params']:
                params = kwargs['params']

        params['pgNum'] = str(pgNum)
        params['pgSize'] = str(c42Lib.MAX_PAGE_NUM)

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_org, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        orgs = binary['data']
        return orgs


    #
    # getOrgsNew(**kwargs):
    # returns json list object of all users for the requested page number
    # params:
    # pgNum - page request for information (starting with 1)
    #

    @staticmethod
    def getOrgsNew(**kwargs):
        logging.info("getOrgs")

        params = {}

        if kwargs:
            logging.info("getOrgs-params:kwargs[" + str(kwargs) + "]")

            if kwargs['params']:
                params = kwargs['params']
            else:
                params['pgNum'] = 1

        params['pgSize'] = str(c42Lib.MAX_PAGE_NUM)

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_org, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        orgs = binary['data']
        return orgs


    #
    # getOrgPageCount():
    # returns number of pages of orgs within the system using MAX_PAGE_NUM
    # returns: integer
    #

    @staticmethod
    def getOrgPageCount():
        logging.info("getOrgPageCount")

        params = {}
        params['pgSize'] = '1'
        params['pgNum'] = '1'

        payload = {}
        r = c42Lib.executeRequest("get", c42Lib.cp_api_org, params, payload)

        logging.debug(r.text)
        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        orgs = binary['data']
        totalCount = orgs['totalCount']

        logging.info("getOrgPageCount:totalCount= " + str(totalCount))

        # num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
        numOfRequests = int(math.ceil(totalCount/c42Lib.MAX_PAGE_NUM)+1)

        logging.info("getOrgPageCount:numOfRequests= " + str(numOfRequests))

        return numOfRequests


    @staticmethod
    def getAllOrgs():
        logging.info("getAllOrgs")
        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.getOrgs(currentPage)
            if pagedList['orgs']:
                fullList.extend(pagedList['orgs'])
            else:
                keepLooping = False
            currentPage += 1
        return fullList

    #
    # getDeviceByGuid(guid):
    # returns device information based on guid
    # params:
    # guid - guid of device
    #

    @staticmethod
    def getDeviceByGuid(guid, **kwargs):
        logging.debug("getDeviceByGuid-params:guid[" + str(guid) + "]")

        if kwargs and 'params' in kwargs:
            params = kwargs['params']
        else:
            params = {}
        if kwargs and 'incBackupUsage' in kwargs:
                params["incBackupUsage"] = "{0}".format(kwargs['incBackupUsage'])
        params['idType'] = "guid"

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_computer + "/" + str(guid), params, payload)

        logging.debug(r.text)

        if r.text != '[{"name":"SYSTEM","description":"java.lang.NullPointerException"}]' and r.text != '[{"name":"SYSTEM","description":"ComputerId not found"}]':

            content = r.content

            binary = json.loads(content)

            logging.debug(binary)

            device = binary['data']

        else:

            device = None

        return device


    #
    # getDeviceById(computerId):
    # returns device information based on computerId
    # params:
    # computerId: computerId of device
    #

    @staticmethod
    def getDeviceById(computerId):
        logging.debug("getDeviceById-params:computerId[" + str(computerId) + "]")

        params = {}
        params['incAll'] = 'true'

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_computer + "/" + str(computerId), params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)

        logging.debug(binary)

        device = binary['data']
        return device

    #
    # getDeviceByParams(params):
    # returns device information based on custom parameters
    # params:
    # any of the device parameters
    #

    @staticmethod
    def getDeviceParams(**kwargs):
        logging.info("getDeviceParams-params: [" + str(kwargs))

        params = {}

        if kwargs['params']:
            params = kwargs['params']

            payload = {}

            r = c42Lib.executeRequest("get", c42Lib.cp_api_computer + "/", params, payload)

            logging.debug(r.text)

            content = r.content
            binary = json.loads(content)
            logging.debug(binary)

            binary_length = len(binary['data']['computers'])

            if binary_length > 0:

                device = binary['data']['computers'][0]

            else:

                device = None # If the result is null

        else:

            device = None

        return device



    #
    # getDeviceByName(deviceName):
    # returns device information based on computerId
    # params:
    # deviceName: name of device
    #

    @staticmethod
    def getDeviceByName(deviceName, **kwargs):
        logging.info("getDeviceByName-params:name[" + deviceName + "],  " + str(kwargs))

        params = {}

        if kwargs['params']:
            params = kwargs['params']

        params['q'] = deviceName     

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_computer + "/", params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        binary_length = len(binary['data']['computers'])

        if binary_length > 0:

            device = binary['data']['computers'][0]

        else:

            device = None # If the result is null

        return device

    #
    # getDeviceBackupReport(params):
    # returns the DeviceBackupReport
    # params:
    # params - These can be passed in to maximize the utility of the function.
    #          Report will page automatically.
    #

    @staticmethod
    def getDeviceBackupReport(params):
        logging.info("getDeviceBackupReport-params:[" + str(params) + "]")

        # set default params for paging and sorting if none passed in

        if not params['pgNum']:
            params['pgNum'] = 1              # Begin w/ Page 1
            params['pgSize'] = MAX_PAGE_NUM  # Limit page size to 250 per page

        if not params['srtKey']:
            params['srtKey'] = 'archiveBytes' # Sort on archiveBytes

        currentPage = params['pgNum']
        keepLooping = True
        fullList = []
        while keepLooping:
            logging.debug("getDeviceBackupReport-page:[" + str(currentPage) + "]")
            deviceList = c42Lib.getDeviceBackupReport(params)
            if deviceList:
                fullDeviceList.extend(deviceList)
            else:
                keepLooping = False
            currentPage += 1

        return fullDeviceList


    #
    # getDevicesPageCount():
    # returns number of pages it will take to return all of the devices based on MAX_PAGE_NUM
    # Returns: integer
    #


    #
    # getDevicesPageCountByOrg(orgId):
    # returns number of pages it will take to return devices by organization based on MAX_PAGE_NUM
    # Returns: integer


    #
    # getDevices(pgNum):
    # returns all devices in system for requested page number within a single json object
    #

    @staticmethod
    def getDevices(pgNum):
        logging.info("getDevices-params:pgNum[" + str(pgNum) + "]")

        # headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
        # url = cp_host + ":" + cp_port + cp_api_user
        params = {}
        params['pgNum'] = str(pgNum)
        params['pgSize'] = str(c42Lib.MAX_PAGE_NUM)
        params['active'] = 'true'
        params['incBackupUsage'] = 'true'
        params['incHistory'] = 'true'

        payload = {}

        # r = requests.get(url, params=payload, headers=headers)
        r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

        logging.debug(r.text)

        content = r.content.decode('UTF-8')
        binary = json.loads(content)
        logging.debug(binary)

        devices = binary['data']['computers']
        return devices

    #
    # getDevicesCustomParams(pgNum, parmas):
    # returns all devices in system for requested page number within a single json object
    #

    @staticmethod
    def getDevicesCustomParams(pgNum, params):
        logging.debug("getDevicesCustomParams-params:pgNum[" + str(pgNum) + "]:params[" + str(params) + "]")

        # headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
        # url = cp_host + ":" + cp_port + cp_api_user
        if not params and not isinstance(params, dict):
            params = {}

        params['pgNum'] = str(pgNum)
        payload = {}

        # r = requests.get(url, params=payload, headers=headers)
        r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        try:
            devices = binary['data']['computers']
        except TypeError:
            devices = False

        return devices
    #
    # getDevicesByOrgPaged(orgId, pgNum):
    # returns devices by organization for requested page number within a single json object
    #

    @staticmethod
    def getDevicesByOrgPaged(orgId, params):
        logging.info("getDevicesByOrgPaged-params:orgId[" + str(orgId) + "]:params[" + str(params) + "]")

        if not params:

            params = {}
            params['orgId'] = orgId
            params['pgNum'] = str(pgNum)
            params['pgSize'] = str(c42Lib.MAX_PAGE_NUM)
            params['active'] = 'true'
            params['incBackupUsage'] = 'true'
            params['incHistory'] = 'true'

        payload = {}

        # r = requests.get(url, params=payload, headers=headers)
        r = c42Lib.executeRequest("get", c42Lib.cp_api_computer, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        devices = binary['data']['computers']
        return devices


    #
    # getAllDevices():
    # returns all devices in system within single json object
    #

    @staticmethod
    def getAllDevices():
        logging.info("getAllDevices")
        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.getDevices(currentPage)
            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList



    @staticmethod
    def getAllDevicesCustomParams(params):
        logging.info("getAllDevicesCustomParams:params[" + str(params) + "]")
        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.getDevicesCustomParams(currentPage, params)
            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    @staticmethod
    def getAllDevicesByOrg(orgId):
        logging.info("getAllDevicesByOrg-params:orgId[" + str(orgId) + "]")
        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.getDevicesByOrgPaged(orgId, currentPage)
            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    @staticmethod
    def putDeviceSettings(computerId, payload):
        logging.info("putDeviceSettings-params:computerId[" + str(computerId) + "]:payload[" + str(payload) + "]")
        params = {}

        r = c42Lib.executeRequest("put", c42Lib.cp_api_computer + "/" + str(computerId), params, payload)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        device = binary['data']
        return device


    @staticmethod
    def putDeviceUpgrade(computerId):
        logging.info("putDeviceUpgrade-params:computerId[" + str(computerId) + "]")

        result = False

        params = {}
        payload = {}

        r = c42Lib.executeRequest("put", c42Lib.cp_api_deviceUpgrade + "/" + str(computerId), params, payload)

        logging.debug(r.text)
        logging.debug(r.status_code)

        if (r.status_code == 201):
            return True
        else:
            return False

    #
    # putDeviceDeactivate(computerId):
    # Deactivates a device based in the computerId passed
    # params:
    # computerId - id for the user to update
    # returns: user object after the update
    #

    @staticmethod
    def putDeviceDeactivate(computerId):
        logging.info("putDeviceDeactivate-params:computerId[" + str(computerId) + "]")

        if (computerId is not None and computerId != ""):
            r = c42Lib.executeRequest("put", c42Lib.cp_api_deacivateDevice+"/"+str(computerId),"","")
            logging.debug('Deactivate Device Call Status: '+str(r.status_code))
            if not (r.status_code == ""):
                return True
            else:
                return False
        else:
            logging.error("putDeviceDeactivate has no userID to act on")


    #
    # attempts to block device
    # PUT
    @staticmethod
    def blockDevice(computerId):
        logging.info("blockDevice-params: computerId[" + str(computerId) + "]")

        params = {}
        payload = {}

        r = c42Lib.executeRequest("put", c42Lib.cp_api_computerBlock + "/" + str(computerId), params, payload)

        logging.debug(r.text)
        logging.debug(r.status_code)

        return True

    #
    # attempts to unblock device
    # DELETE
    @staticmethod
    def unblockDevice(computerId):
        #error codes: USER_IS_BLOCKED, USER_IS_DEACTIVATED
        logging.info("unblockDevice-params: computerId[" + str(computerId) + "]")

        params = {}
        payload = {}

        r = c42Lib.executeRequest("delete", c42Lib.cp_api_computerBlock + "/" + str(computerId), params, payload)

        logging.debug(r.text)
        logging.debug(r.status_code)

        return r.text

    #
    # Adds the role to an individual user.
    # Note: attempts to add the role to a user even if it already exists.
    #
    @staticmethod
    def addUserRole(userId, roleName):
        logging.info("addUserRole-params: userId[" + userId + "]:roleName[" + roleName + "]")

        result = False
        if(userId!=1):
            # headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
            # url = cp_host + ":" + cp_port + cp_api_userRole
            params = {}

            payload = {}
            payload['userId'] = userId
            payload['roleName'] = roleName

            # r = requests.post(url, data=json.dumps(payload), headers=headers)

            r = c42Lib.executeRequest("post", c42Lib.cp_api_userRole, params, payload)

            logging.debug(r.text)
            logging.debug(r.status_code)
            if(r.status_code == 200):
                result = True
        else:
            logging.debug("user is the default admin user, skip adding the user role.")
            result = True
        # Post was successful with an HTTP return code of 200
        return result


    #
    # Adds a role for all users per org
    #
    @staticmethod
    def addAllUsersRoleByOrg(orgId, roleName):
        logging.info("addAllUsersRoleByOrg-params: orgId[" + str(orgId) + "]:userRole[" + roleName + "]")

        count = 0
        users = c42Lib.getAllUsersByOrg(orgId)
        for user in users['users']:
            userId = str(user['userId'])
            userName = user['username']
            if (c42Lib.addUserRole(userId, roleName)):
                count = count + 1
                logging.info("Success: userRole[" + roleName + "] added for userId[" + userId + "]:userName[" + userName + "]")
            else:
                logging.info("Fail: userRole[" + roleName + "] added for userId[" + userId + "]:userName[" + userName + "]")

        logging.info("Total Users affected: " + str(count))

    #
    # Adds a role for all users per org
    #
    @staticmethod
    def addAllUsersRole(roleName):
        logging.info("addAllUsersRole-params: roleName[" + roleName + "]")

        count = 0
        users = c42Lib.getAllUsers()
        for user in users['users']:
            userId = str(user['userId'])
            userName = user['username']
            if (c42Lib.addUserRole(userId, roleName)):
                count = count + 1
                logging.info("Success: userRole[" + userRole + "] added for userId[" + userId + "]:userName[" + userName + "]")
            else:
                logging.info("Fail: userRole[" + userRole + "] added for userId[" + userId + "]:userName[" + userName + "]")

        logging.info("Total Users affected: " + str(count))


    #
    # Remove the role from an individual user.
    # Note: attempts to remove the role from a user even if the role doesn't exist.
    #
    @staticmethod
    def removeUserRole(userId, roleName):
        logging.info("removeUserRole-params: userId[" + userId + "]:roleName[" + roleName + "]")

        # headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
        # url = cp_host + ":" + cp_port + cp_api_userRole
        params = {}
        params['userId'] = userId
        params['roleName'] = roleName

        payload = {}

        # r = requests.delete(url, data=json.dumps(payload), headers=headers)
        r = c42Lib.executeRequest("delete", c42Lib.cp_api_userRole, params, payload)

        logging.debug(r.text)
        logging.debug(r.status_code)

        # Delete was successful with an HTTP return code of 204
        return r.status_code == 204


    #
    # Removes the role for all users within an org
    #
    @staticmethod
    def removeAllUsersRoleByOrg(orgId, roleName):
        logging.info("removeAllUsersRoleByOrg-params:orgId[" + str(orgId) + "]:roleName[" + roleName + "]")

        count = 0
        users = c42Lib.getAllUsersByOrg(orgId)
        for user in users['users']:
            userId = str(user['userId'])
            userName = user['username']
            if (c42Lib.removeUserRole(userId, userRole)):
                count = count + 1
                logging.info("Success: userRole[" + userRole + "] removeal for userId[" + userId + "]:userName[" + userName + "]")
            else:
                logging.info("Fail: userRole[" + userRole + "] removal for userId[" + userId + "]:userName[" + userName + "]")

        logging.info("Total Users affected: " + str(count))


    #
    # Removes the role for all users
    #
    @staticmethod
    def removeAllUsersRole(roleName):
        logging.info("removeAllUsersRole-params:roleName[" + roleName + "]")

        count = 0
        users = c42Lib.getAllUsers()
        for user in users['users']:
            userId = str(user['userId'])
            userName = user['username']
            if (c42Lib.removeUserRole(userId, userRole)):
                count = count + 1
                logging.info("Success: userRole[" + userRole + "] removeal for userId[" + userId + "]:userName[" + userName + "]")
            else:
                logging.info("Fail: userRole[" + userRole + "] removal for userId[" + userId + "]:userName[" + userName + "]")

        logging.info("Total Users affected: " + str(count))

    #
    # getPlan(params):
    # returns destination information
    # params:
    # See API reference

    @staticmethod
    def getPlan(params):
        logging.debug("getPlan - params: [" + str(params) + "]")

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_plan, params, payload)

        logging.debug(r.text)

        if r.status_code == 200:

            content = r.content
            binary = json.loads(content)
            logging.debug(binary)

            plan = binary['data']

        return plan

    # get a user's legal hold membership info
    # Minimum argument is userUid    

    @staticmethod
    def getUserLegalHoldMemberships(**kwargs):
        logging.info("getUserLegalHoldMembership-kwargs:userUid[" + str(kwargs) + "]")

        params = {}

        if 'params' in kwargs:

            params = kwargs['params']
        
        if 'activeState' in kwargs:
            params ['activeState'] = kwargs['activeState']  #Specifiy only the inactive, active or all memberships

        if 'userUid' in kwargs:
            params ['userUid'] = kwargs['userUid']
        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_legalHoldMembership, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        if binary['data']['legalHoldMemberships']:

            legalHoldMembershipInfo = binary['data']['legalHoldMemberships']
            return legalHoldMembershipInfo

        else:

            return False


    
    #
    # legalHoldHinfo(legalHoldUid):
    # Returns the info available for a Legal Hold
    # params:
    # legalHoldUid - Uid of the LegalHold to get/put info
    # userUid - Uid of the user being added or removed
    # actionType - "add" or "put" depending on what you'd like to have happen
    # returns: returns a 204 if successfully removed
    #


    @staticmethod
    def legalHoldInfo(**kwargs):
  
        logging.info("legalHoldInfo-params: " + str(kwargs))

        legalHoldInfo = False

        payload = {}

        if 'legalHoldUid' in kwargs:
            params = {}
            params["legalHoldUid"] = kwargs['legalHoldUid']
        
        elif 'params' in kwargs:
            params = kwargs['params']
        else:
            params = {}


        r = c42Lib.executeRequest("get", c42Lib.cp_api_legaHold, params, payload)
        logging.debug(r.status_code)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        try:
            if binary['data']['legalHolds']:
                legalHoldInfo = binary['data']['legalHolds']
        except TypeError:
            legalHoldInfo = False   

        return legalHoldInfo


    #
    # Params: Uid/Guid/Id - currently the API wants the ID not the GUID or UID
    # destinationId (kwargs): get storage history for destination
    # serverId (kwargs): get storage history for server
    # orgId (kwargs): get storage history for org
    # userId (kwargs): get storage history for destination
    # Returns: 30 days of storage history for the given type
    #
    @staticmethod
    def getStoredBytesHistory(Uid, **kwargs):
        logging.info("getStoredBytesHistory-params:Uid[" + str(Uid) + "], kwargs " + str(kwargs))

        params  = {}
        payload = {}

        if kwargs['destination']:
            params['destinationId'] = str(Uid)

        if kwargs['server']:
            params['serverId'] = str(Uid)

        if kwargs['org']:
            params['orgId'] = str(Uid)

        if kwargs['user']:
            params['userId'] = str(Uid)

        r = c42Lib.executeRequest("get", c42Lib.cp_api_storedBytesHistory, params, payload)
        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        if binary['data']:
            actionResults = binary['data']

        else:

            actionResults = False

        return actionResults

    #
    # Get general legal hold info


    @staticmethod
    def getLegalHoldInfo(**kwargs):
        logging.info("getLegalHoldInfo-params:[" + str(kwargs) + "]")
        params = {}




        r = c42Lib.executeRequest("get", c42Lib.cp_api_legalHold, params, payload)

        logging.debug(r.status_code)
        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        if binary['data']:
            actionResults = binary['data']

        else:

            actionResults = False

        return actionResults




    # DO NOT USE, this api is un-paged and will cause performance issues
    # You've been warned
    # returns list of users in legal hold: active only
    #
    @staticmethod
    def getLegalHoldMembershipSummary(legalHoldUid):
        logging.info("getLegalHoldMembershipSummary-params:legalHoldUid[" + str(legalHoldUid) + "]")
        # Request URL:https://172.16.27.13:4285/api/legalHoldMembershipSummary/?legalHoldUid=741239804344030230&activeState=ALL
        # data.legalHoldMemberships.[0].user.username
        params = {}
        params['legalHoldUid'] = legalHoldUid
        params['activeState'] = "active"

        payload = {}
        # r = requests.get(url, params=payload, headers=headers)
        r = c42Lib.executeRequest("get", c42Lib.cp_api_legalHoldMembershipSummary, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)


        users = binary['data']['legalHoldMemberships']

        return users

    @staticmethod
    def getAllLegalHoldMemberships(legalHoldUid, **kwargs):
        logging.info("getAllLegalHoldMemberships-params:legalHoldUid[" + str(legalHoldUid) + "]")
        if kwargs:
            logging.info("kwargs params: " + str(kwargs))

        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.getAllLegalHoldMemberhipsPaged(legalHoldUid, currentPage, **kwargs)
            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    @staticmethod
    def getAllLegalHoldMemberhipsPaged(legalHoldUid, currentPage, **kwargs):
        logging.info("getAllLegalHoldMemberhipsPaged-params:legalHoldUid[" + str(legalHoldUid) + "]")
        if kwargs:
            logging.info("kwargs params: " + str(kwargs))
        logging.info("currentPage: " + str(currentPage))

        params = {}
        params['legalHoldUid'] = legalHoldUid
        params['pgNum'] = currentPage
        # default is 100... not sure if need to set
        # params['pgSize'] = "100"

        # spec says default is "Active", but not trusting it, so setting "Active" if no params inputted
        if kwargs and 'activeState' in kwargs:
            params['activeState'] = kwargs['activeState']
        else:
            params['activeState'] = "active"

        payload = {}
        r = c42Lib.executeRequest("get", c42Lib.cp_api_legalHoldMembership, params, payload)
        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        users = binary['data']['legalHoldMemberships']
        logging.info("number of users returned: " + str(len(users)))
        return users


    
    @staticmethod
    def addUserToLegalHold(legalHoldUid, userUid):
# {
#   "legalHoldUid":12938712892791283,
#   "userUid":"0cc175b9c0f1b6a8"
# }
        logging.info("addUserToLegalHold-params:legalHoldUid[" + str(legalHoldUid) + "]|userUid[" + str(userUid) + "]")
        params = {}

        payload = {}
        payload["legalHoldUid"] = legalHoldUid
        payload["userUid"] = userUid

        logging.info(str(payload))
        # r = requests.get(url, params=payload, headers=headers)
        r = c42Lib.executeRequest("post", c42Lib.cp_api_legalHoldMembership, params, payload)
        logging.debug(r.status_code)

        if (r.status_code == 201):
            logging.debug(r.text)

            content = r.content
            binary = json.loads(content)
            logging.debug(binary)


            response = binary['data']

            return response
        elif (r.status_code == 400):
            return False
        else:
            return False
        

    @staticmethod
    def deactivateUserFromLegalHoldMembership(legalHoldMembershipUid):
        logging.info("deactivateUserFromLegalHoldMembership-params:legalHoldMembershipUid[" + str(legalHoldMembershipUid) + "]")
        params = {}

        payload = {}
        payload["legalHoldMembershipUid"] = legalHoldMembershipUid

        logging.info(str(payload))
        # r = requests.get(url, params=payload, headers=headers)
        r = c42Lib.executeRequest("post", c42Lib.cp_api_legalHoldMembershipDeactivation, params, payload)
        logging.debug(r.status_code)


        if (r.status_code == 204):
            return True
        elif (r.status_code == 400):
            return False
        else:
            return False


    # Get an Archive

    @staticmethod
    def getArchive(**kwargs):
        logging.info("getArchive-params: " + str(kwargs))

        params = {}

        try:
            #If only a GUID is supplied, it's enough.

            guid = kwargs['guid']
            logging.info("getArchive-Guid:" + str(guid))

        except:

            try:
                params = kwargs['params']
                logging.info("getArchive-Params:" + str(params))

            except:

                logging.info("getArchive-No archiveGUID or Params provided.  Returning None.")
                return None

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        try:
            archive = binary['data']['archives']
        
        except TypeError:
                
            return None

        return archive

    #End getArchive

    # Get Archives by entering by userUid - entered in the Params

    @staticmethod
    def getArchivesByUserId(params):
        logging.info("getArchivesByUserId-params: " + str(params))


        # params = {type: str(id), 'pgSize': '1', 'pgNum': '1'}
        # payload = {}
        # r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)


        payload = {}

        archives = None

        if params and (('userId' in params) or ('userUid' in params)):

            r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)

            logging.debug(r.text)

            content = r.content
            binary = json.loads(content)
            logging.debug(binary)

            archives = binary['data']['archives']

        return archives


## TO BE DELETED
##========================================================================================



    @staticmethod
    def getArchiveByStorePointId(storePointId,params):
        logging.info("getArchiveByStorePointId-params:storePointId[" + str(storePointId) + "]")
        currentPage = 1
        keepLooping = True
        fullList = []
        # params = {}
        params['storePointId'] =  str(storePointId)
        while keepLooping:
            pagedList = c42Lib.getArchivesPaged(params,currentPage)
            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    @staticmethod
    def getArchivesByServerId(serverId):
        logging.info("getArchiveByServerId-params:serverId[" + str(serverId) + "]")
        currentPage = 1
        keepLooping = True
        fullList = []
        params = {}
        params['serverId'] = str(serverId)
        while keepLooping:
            pagedList = c42Lib.getArchivesPaged(params,currentPage)
            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    @staticmethod
    def getArchivesByDestinationId(destinationId):
        logging.info("getArchiveByDestinationId-params:destinationId[" + str(destinationId) + "]")
        currentPage = 1
        keepLooping = True
        fullList = []
        params = {}
        params['destinationId'] = str(destinationId)

        while keepLooping:
            pagedList = c42Lib.getArchivesPaged(params,currentPage)
            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    @staticmethod
    def getArchiveByGuidAndComputerId(guid, targetComputerId):
        logging.info("getArchiveByGuidAndComputerId-params:guid[" + str(guid) + "]:targetComputerId[" + str(targetComputerId) + "]")

        params = {}
        params['guid'] = str(guid)
        params['targetComputerId'] = str(targetComputerId)

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        archives = binary['data']['archives']

        return archives


    @staticmethod
    def getArchivesByUserId(userId):
        logging.info("getArchivesByUserId-params:userId[" + str(userId) + "]")


        # params = {type: str(id), 'pgSize': '1', 'pgNum': '1'}
        # payload = {}
        # r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)

        params = {}
        params['userId'] = str(userId)
        #params['idType'] = 'uid' # For 4.x series

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        archives = binary['data']['archives']

        return archives



    @staticmethod
    def getArchivesPaged(params, pgNum):
        logging.info("getArchivesPaged-params:params[" + str(params) + "]:pgNum[" + str(pgNum) + "]")

        params['pgSize'] = c42Lib.MAX_PAGE_NUM
        params['pgNum'] = pgNum
        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_archive, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        archives = binary['data']['archives']

        return archives








##===================================================================================================







    @staticmethod
    def getRestoreRecordPaged(params, pgNum):
        logging.info("getRestoreRecordPaged-params:params[" + str(params) + "]:pgNum[" + str(pgNum) + "]")

        params['pgSize'] = c42Lib.MAX_PAGE_NUM
        params['pgNum'] = pgNum

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_restoreRecord, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        archives = binary['data']['restoreRecords']

        return archives


    @staticmethod
    def getRestoreRecordAll():
        logging.info("getRestoreRecordAll")

        params = {}

        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.getRestoreRecordPaged(params,currentPage)

            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    # cp_api_restoreHistory = "/api/restoreHistory"
    #?pgNum=1&pgSize=50&srtKey=startDate&srtDir=desc&days=9999&orgId=35

    @staticmethod
    def getRestoreHistoryForOrgId(orgId):
        logging.info("getRestoreHistoryForOrgId-params:orgId[" + str(orgId) + "]")

        params = {}
        params['strKey'] = 'startDate'
        params['days'] = '9999'
        params['strDir'] = 'desc'
        params['orgId'] = str(orgId)

        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.getRestoreHistoryPaged(params,currentPage)

            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    @staticmethod
    def getRestoreHistoryForUserId(userId):
        logging.info("getRestoreHistoryForUserId-params:userId[" + str(userId) + "]")

        params = {}
        params['strKey'] = 'startDate'
        params['days'] = '9999'
        params['strDir'] = 'desc'
        params['userId'] = str(userId)
        params['idType'] = 'uid'

        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.getRestoreHistoryPaged(params,currentPage)

            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    @staticmethod
    def getRestoreHistoryForComputerId(computerId):
        logging.info("getRestoreHistoryForComputerId-params:computerId[" + str(computerId) + "]")

        params = {}
        params['strKey'] = 'startDate'
        params['days'] = '9999'
        params['strDir'] = 'desc'
        params['computerId'] = str(computerId)

        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.getRestoreHistoryPaged(params,currentPage)

            if pagedList:
                fullList.extend(pagedList)
            else:
                keepLooping = False
            currentPage += 1
        return fullList


    @staticmethod
    def getRestoreHistoryPaged(params, pgNum):
        logging.info("getRestoreHistoryPaged-params:params[" + str(params) + "]:pgNum[" + str(pgNum) + "]")

        #Let the page size be set in the params if it exists.

        try:
            if not params['pgSize']:
                params['pgSize'] = c42Lib.MAX_PAGE_NUM
        
        except TypeError:
            params['pgSize'] = params['pgSize']

        params['pgNum'] = pgNum

        payload = {}

        archives = False

        r = c42Lib.executeRequest("get", c42Lib.cp_api_restoreHistory, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        try:

            archives = binary['data']['restoreEvents']
        
        except TypeError:
        
            archives = False

        return archives


    # only 3.6.2.1 and greater - json errors in pervious versions
    # will return array of info for every file within given archive
    # performance is not expected to be great when looking at large archives - impacted by number of files in archive
    # guid is int, decrypt is boolean

    # saveToDisk - will write out the response to a .json file
    @staticmethod
    def getArchiveMetadata2(guid, dataKeyToken, decrypt, saveToDisk, **kwargs):
        logging.info("getArchiveMetadata-params:guid["+str(guid)+"]:decrypt["+str(decrypt)+"]")

        params = {}
        if (decrypt):
            params['decryptPaths'] = "true"
        # always stream the response - remove memory limitation on requests library
        params['stream'] = "True"
        params['dataKeyToken'] = dataKeyToken
        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_archiveMetadata + "/" + str(guid), params, payload, **kwargs)

        # logging.info("*******" + r.text + "*******")
        #null response on private passwords

        # http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
        if saveToDisk:
            # print r.text
            local_filename = "json/archiveMetadata_"+str(guid)+".json"
            with open(local_filename, 'wb') as f:
                counter = 0
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        counter += 1
                        f.write(chunk)
                        f.flush()
                        if counter % 100 == 0:
                            sys.stdout.write('.')
                            sys.stdout.flush()
                print ""
                return local_filename
            print ""
        else:
            if r.text:
                content = ""
                for chunk in r.iter_content(1024):
                    if chunk:
                        content = content + chunk
                binary = json.loads(content)
                del content
                # may be missing data by doing this call..
                # but this means the parcing failed and we can't extract the data
                if 'data' in binary:
                    
                    sys.stdout.write('*')
                    sys.stdout.flush()
                    print ""
                    
                    archiveMetadata = binary['data']
                    del binary
                    return archiveMetadata
                else:
                    return ""
            else:
                return ""

    @staticmethod
    def getArchiveMetadata(guid, dataKeyToken, decrypt, **kwargs):
        c42Lib.getArchiveMetadata2(guid, dataKeyToken, decrypt, False, **kwargs)
    #
    # getServers():
    # returns servers information
    # params:
    #

    @staticmethod
    def getServers():
        logging.info("getServers")

        params = {}
        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_server, params, payload)

        logging.debug(r.text)

        content = r.content.decode("UTF-8")
        binary = json.loads(content)
        logging.debug(binary)

        servers = binary['data']['servers']
        return servers


    #
    # getServer(serverId):
    # returns server information based on serverId
    # params: serverId
    #

    @staticmethod
    def getServer(serverId):
        logging.info("getServer-params:serverId["+str(serverId)+"]")

        params = {}
        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_server + "/" + str(serverId), params, payload)

        # logging.info("====server response : " + r.text + "====")

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        if binary['data']:
            server = binary['data']
        else:
            server = None

        return server

    #
    # getColdStorage(params):
    # Returns the cold storage archives using the supplied parameters
    # params:
    # returns: cold storage list for params
    #

    @staticmethod
    def getColdStorage(params):
        logging.info("getColdStorage - params [" + str(params)+ "]")

        
        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_coldStorage, params, payload)
            
        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        if binary['data']:
            
            return binary['data']

        else:
            
            return None



    #
    # getColdStorageByOrg(orgId):
    # Returns the cold storage archives in the supplied org
    # params:
    # orgId - id for the archive to update
    # returns: cold storage list for org object
    #

    @staticmethod
    def getColdStorageByOrg(orgId):
        logging.info("ColdStorageByOrg")

        params = {}
        params['pgSize'] = '250'
        params['pgNum'] = 1
        params['orgId'] = orgId
        params['srtKey'] = 'sourceUserName'
        params['srtDir'] = 'asc'
        params['active'] = 'true' # Only check against active orgs

        payload = {}

        currentPage = 1
        keepLooping = True
        fullList = []
        while keepLooping:
            pagedList = c42Lib.executeRequest("get", c42Lib.cp_api_coldStorage, params, payload)
            
            print 'Page :' + str(currentPage)
            content = pagedList.content
            binary = json.loads(content)
            list = binary['data']['coldStorageRows']
            
            if list:

                fullList.extend(list)
            else:
                keepLooping = False
            currentPage += 1
            params['pgNum'] = currentPage
            

        return fullList


    #
    # putColdStorageUpdate(archiveGuid, payload):
    # updates an archive's cold storage information based on the payload passed
    # params:
    # archiveId - id for the archive to update
    # payload - json object containing name / value pairs for values to update
    # returns: user object after the update
    #

    @staticmethod
    def putColdStorageUpdate(archiveGUID, payload):
        logging.info("putColdStorageUpdate-params:archiveGUID[" + str(archiveGUID) + "],payload[" + str(payload) + "]")

        params = {}
        params['idType'] = 'guid'

        if (payload is not None and payload != ""):
            r = c42Lib.executeRequest("put", c42Lib.cp_api_coldStorage + "/" + str(archiveGUID), params, payload)
            logging.debug(str(r.status_code))
            content = r.content
            binary = json.loads(content)
            logging.debug(binary)

            try:

                coldStorageArchive = binary['data']
                return coldStorageArchive
                logging.error("putColdStorageUpdate param payload is :" + str(coldStorageArchive))

            except TypeError:

                logging.error("putColdStorageUpdate returned nothing.")
                return None

            # if (r.status_code == 200):
                # return True
            # else:
                # return False
        else:
            logging.error("putColdStorageUpdate param payload is null or empty")
            return None


    @staticmethod
    def purgeColdStorage(guid,params):
        logging.debug("purgeColdStorage - guid: [" + str(guid) + "]")

        payload = {}
 
        r = c42Lib.executeRequest("delete", c42Lib.cp_api_coldStorage+"/"+str(guid), params, payload)

        logging.debug(r.text)

        coldStoragePurged = False

        if r.status_code == 200:

            content = r.content
            binary = json.loads(content)
            logging.debug(binary)

            coldStoragePurged = binary['data']

            #print coldStoragePurged
            #raw_input()

        return coldStoragePurged



    # getStorePoitnByStorePointId(storePointId):
    # returns store point information based on the storePointId
    # params:
    # storePointId: id of storePoint
    #

    @staticmethod
    def getStorePointByStorePointId(storePointId):
        logging.info("getStorePointByStorePointId-params:storePointId[" + str(storePointId) + "]")

        params = {}
        payload = {}

        storePoint = False

        r = c42Lib.executeRequest("get", c42Lib.cp_api_storePoint + "/" + str(storePointId), params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        try:
            storePoint = binary['data']

        except TypeError:

            storePoint = None


        return storePoint


    #EKR

    @staticmethod
    def ekr_jobCreate(userUid):
        logging.info("ekr_jobCreate-params:userUid[" + str(userUid) + "]")
        params = {}
        payload = {}

        r = c42lib.executeRequest("put", c42Lib.cp_api_ekr + "/" + str(userUid), params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        return binary


    @staticmethod
    def ekr_jobStatus(userUid, activeOnly):
        logging.info("ekr_jobStatus-params:userUid[" + str(userUid) + "] | activeOnly:[" + str(activeOnly) + "]")
        params = {}
        params['activeOnly'] = activeOnly
        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_ekr + "/" + str(userUid), params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        return binary


    @staticmethod
    def ekr_jobCancel(userUid):
        logging.info("ekr_jobCancel-params:userUid[" + str(userUid) + "]")
        params = {}
        payload = {}

        r = c42lib.executeRequest("delete", c42Lib.cp_api_ekr + "/" + str(userUid), params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        return binary

    @staticmethod
    def ekr_jobUpdate(userUid, command):
        # wakupJob
        # deleteBackupCopy
        logging.info("ekr_jobUpdate-params:userUid[" + str(userUid) + "] | command:[" + str(command) + "]")
        params = {}
        params['command'] = command
        payload = {}

        r = c42Lib.executeRequest("post", c42Lib.cp_api_ekr + "/" + str(userUid), params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        return binary


    # params:
    # 
    @staticmethod
    def smartsearch(**kwargs):
        logging.info("requestSmartSearch: " + str(kwargs))
        payload = {}
        if kwargs:
            params=kwargs['params']
        else:
            return None
        
        r = c42Lib.executeRequest("get", c42Lib.cp_api_smartsearch + "?", params, payload)
        contents = r.content.decode("UTF-8")
        binary = json.loads(contents)
        logging.info("requestSmartSearch Response: " + str(contents))
        return binary['data'] if 'data' in binary else None



    #
    # Compute base64 representation of the authentication token.
    #
    @staticmethod
    def getAuthHeader(u,p):

        format = '%s:%s' % (u,p)
        if isinstance(format, bytes):
            token = base64.b64encode(format).decode('UTF-8')
        else:
            token = base64.b64encode(bytes(format, 'UTF-8')).decode('UTF-8')

        return "Basic %s" % token

    #
    # Sets logger to file and console
    #
    @staticmethod
    def setLoggingLevel(**kwargs):
        # set up logging to file

        #print kwargs

        c42Lib.cp_logFileName = c42Lib.getFilePath(c42Lib.cp_logFileName)
        showInConsole = True

        if not kwargs:

            # Legacy Logging Setup
            if c42Lib.cp_logLevel == 'INFO':

                logging.basicConfig(
                                    level = logging.info,
                                    format='%(asctime)s [%(name)-8s] [ %(levelname)-6s ] %(message)s',
                                    datefmt='%m-%d %H:%M',
                                    # filename='EditUserRoles.log',
                                    filename = str(c42Lib.cp_logFileName),
                                    filemode='w')

            else:

                logging.basicConfig(
                                    level = logging.debug,
                                    format='%(asctime)s [%(name)-8s] [ %(levelname)-6s ] %(message)s',
                                    datefmt='%m-%d %H:%M',
                                    # filename='EditUserRoles.log',
                                    filename = str(c42Lib.cp_logFileName),
                                    filemode='w')

            # define a Handler which writes INFO messages or higher to the sys.stderr
            console = logging.StreamHandler()


            if(c42Lib.cp_logLevel=="DEBUG"):
                console.setLevel(logging.debug)
                # console.setLevel(logging.info)
            else:
                console.setLevel(logging.info)
           # set a format which is simpler for console use
            formatter = logging.Formatter('%(asctime)s [%(name)-8s] [ %(levelname)-6s ] %(message)s')
            # tell the handler to use this format
            console.setFormatter(formatter)
            # add the handler to the root logger
            logging.getLogger('').addHandler(console)

        else:

            # Fancy Split Logging - requires the use of KWARGS when calling the logging function.

            if kwargs:
                if 'showInConsole' in kwargs:
                    showInConsole = kwargs['showInConsole']  # Let's you turn off logging to the console if you like.
                if 'loggingLevel' in kwargs:
                    c42Lib.cp_logLevel = kwargs['loggingLevel']
                else:
                    kwargs['loggingLevel'] = c42Lib.cp_logLevel

            if c42Lib.cp_logLevel == 'INFO':

                logging.basicConfig(
                                    level=logging.info,
                                    format='%(asctime)s [%(name)-12s] [ %(levelname)-6s ] %(message)s',
                                    datefmt='%m-%d %H:%M',
                                    filename = str(c42Lib.cp_logFileName),
                                    filemode='w')

            if c42Lib.cp_logLevel == 'WARNING':

                print "\nSetting Logging Level to WARNING\n"

                logging.basicConfig(
                                    level=logging.warning,
                                    format='%(asctime)s [%(name)-12s] [ %(levelname)-6s ] %(message)s',
                                    datefmt='%m-%d %H:%M',
                                    filename = str(c42Lib.cp_logFileName),
                                    filemode='w')

            if c42Lib.cp_logLevel == 'DEBUG':

                print "\nSetting Logging Level to DEBUG\n"

                logging.basicConfig(
                                    level=logging.debug,
                                    format='%(asctime)s [%(name)-12s] [ %(levelname)-6s ] %(message)s',
                                    datefmt='%m-%d %H:%M',
                                    filename = str(c42Lib.cp_logFileName),
                                    filemode='w')

            if c42Lib.cp_logLevel == 'ERROR':

                print "\nSetting Logging Level to ERROR\n"

                logging.basicConfig(
                                    level=logging.error,
                                    format='%(asctime)s [%(name)-12s] [ %(levelname)-6s ] %(message)s',
                                    datefmt='%m-%d %H:%M',
                                    filename = str(c42Lib.cp_logFileName),
                                    filemode='w')

            if c42Lib.cp_logLevel == 'CRITICAL':

                print "\nSetting Logging Level to CRITICAL\n"

                logging.basicConfig(
                                    level=logging.critical,
                                    format='%(asctime)s [%(name)-12s] [ %(levelname)-6s ] %(message)s',
                                    datefmt='%m-%d %H:%M',
                                    filename = str(c42Lib.cp_logFileName),
                                    filemode='w')

            # Set log file format
            loggingFormatter = logging.Formatter('%(asctime)s [%(name)-12s] [ %(levelname)-6s ] %(message)s')
            logfile = logging.FileHandler(str(c42Lib.cp_logFileName))
            logfile.setFormatter(loggingFormatter)

            # set a format which is simpler for console use
            console = logging.StreamHandler()
            console.setFormatter(loggingFormatter)

            # add the handler to the root logger
            logging.getLogger('').addHandler(logfile)
            
        if not showInConsole: 

            logging.getLogger('').addHandler(console)

        else:
            print "Suppress Logging Output to Console"
            logging.getLogger('').removeHandler(console)

        if os.path.exists(c42Lib.getFilePath('deleteme.log')):

            logging.debug('setLoggingLevel: delete temporary log file : ' + str(c42Lib.getFilePath('deleteme.log')))
            
            try:
                os.remove(c42Lib.getFilePath('deleteme.log'))
            except OSError:

                print ""
                print "Could not delete : " + str(c42Lib.getFilePath('deleteme.log'))
                print ""

        logging.debug('end: setLoggingLevel ' + str(c42Lib.cp_logLevel))



    @staticmethod
    def executeCLICommand(payload):
        params = {}

        r = c42Lib.executeRequest("post", c42Lib.cp_api_cli, params, payload)

        logging.debug(r.text)
        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        return binary['data']

    #
    # credit: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    #
    @staticmethod
    def sizeof_fmt(num):
        for x in ['bytes','KiB','MiB','GiB']:
            if num < 1024.0 and num > -1024.0:
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TiB')



    @staticmethod
    def sizeof_fmt_si(num):
        for x in ['bytes','kB','MB','GB']:
            if num < 1000.0 and num > -1000.0:
                return "%3.1f%s" % (num, x)
            num /= 1000.0
        return "%3.1f%s" % (num, 'TB')




    @staticmethod
    def returnHostAndPortFromFullURL(url):
        p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        m = re.search(p, str(url))

        # address = [m.group('protocol') +''+ m.group('host'),m.group('port')]
        # m.group('host') # 'www.abc.com'
        # m.group('port') # '123'
        # address = [m.group('http')]
        # print address
        return address


    # Read a CSV file

    @staticmethod
    def readCSVfile(csvFileName):
        logging.info("readCSVfile:file - [" + csvFileName + "]")

        fileList = []

        csvFileName = c42Lib.getFilePath(csvFileName)

        csvfile = open(csvFileName, 'rU')

        if (',' in csvfile.read(1024)):
            csvfile.seek(0) # Return to beginning of file
            fileDialect = csv.Sniffer().sniff(csvfile.read(1024),'\n')
            csvfile.seek(0) # Return to beginning of file

            reader = csv.reader(csvfile, delimiter=fileDialect.delimiter,dialect=fileDialect)

        else:  # Use for single column without a delimiter
            csvfile.seek(0) # Return to beginning of file
            reader = csv.reader(csvfile)

        for row in reader:
            if len(row) != 0:  #Don't include the row if it's blank or empty
                fileList.append(row)

        return fileList

    # Read a CSV file

    @staticmethod
    def readCSVFiletoDictionary(csvFileName):
        logging.info("readCSVfile:file - [" + csvFileName + "]")


        csvFileName = c42Lib.getFilePath(csvFileName)

        fileList = {}

        with open (csvFileName,'r') as csvFile:
            row = csv.DictReader(csvFile)
            for value in row:
                fileList.setdefault(value['Key'],[]).append(value['Value'])

        newValueList = {}

        for key,value in fileList.items():
            newValueList[key] = value[0]
        
        return newValueList



    # CSV Write & Append Method
    # Will apped to a CSV with n number of elements.  Pass in a list and it writes the CSV.

    @staticmethod
    def writeCSVappend(listtowrite,filenametowrite,writeType):
        logging.info("writeCSVappend:file - [" + filenametowrite + "]")

        #Check the length of the list to write.  If more than one item, then iterate through the list

        filenametowrite = c42Lib.getFilePath(filenametowrite)

        if (not isinstance(listtowrite, basestring)): #More than 1 item in list?
            # Correctly append to a CSV file
            output = open(filenametowrite, writeType) # Open the file to append to it

            # stufftowrite = []

            writestring = ''
            itemstowrite = ''
            itemsToWriteeEncoded = ''

            for stufftowrite in listtowrite:
                if (isinstance (stufftowrite,(int)) or isinstance(stufftowrite,(float)) or isinstance(stufftowrite,(long)) or isinstance(stufftowrite,(datetime.date))):
                    itemsToWriteeEncoded = stufftowrite
            
                elif stufftowrite is not None: 
                    itemsToWriteeEncoded = stufftowrite.encode('utf8') # encoding protects against crashes
            
                else:
                    itemsToWriteeEncoded = stufftowrite
                writestring = writestring + str(itemsToWriteeEncoded) + ','
                logging.debug("writeCSVappend:file - [" + filenametowrite + "] - " + str(writestring))

            writestring = writestring[:-1] + "\n" # Remove an extra space at the end of the string and append a return
            output.write (writestring)
            output.close

        else: #What happens if there is only one item and not a list
            # Correctly append to a CSV file
            output = open(filenametowrite, writeType) # Open the file to append to it

            
            if (isinstance (listtowrite,(int)) or isinstance(listtowrite,(float)) or isinstance(stufftowrite,(long)) or isinstance(stufftowrite,(datetime.date))):
                itemsToWriteeEncoded = listtowrite # if the item is an integer, just add it to the list
            
            elif listtowrite is not None: 
                itemsToWriteeEncoded = listtowrite.encode
            
            else: #All other cases
                itemsToWriteeEncoded = listtowrite.encode('utf8') # encoding protects against crashes
            
            writestring = str(itemsToWriteeEncoded)
            logging.debug("writeCSVappend:file - [" + filenametowrite + "] - " + str(writestring))
            writestring = writestring + "\n" # Remove an extra space at the end of the string and append a return
            output.write (writestring)
            output.close
    
        return

    # CSV Creates files.  Single funciton that's used a lot to create output files in scripts.
    # params:   csvFileName - the base file name
    #           fileList - an array with a file name extension and the headers for the files to create
    #                       ['filetype':'whatisinthisfile','fileheaders':(header1,header2,header3,header4)]
    #           filedate - the timestamp for the files
    #           testMode - if anything except "execute" is passed to it the file

    @staticmethod
    def setupCSVFiles (csvFileName,fileList,fileDate,testMode,writeMode):
        logging.info("setupCSVFiles:base file name - [" + csvFileName + "]")

        # Add 'Test' to file name if a test
        fileNameTest = ''
        if testMode:
            fileNameTest = '-TEST'

        counter = 0
        fileNames = []

        for index, fileHeader in enumerate(fileList):

            counter += 1

            fileDesc       = fileHeader['fileDesc']
            fileHeaderNames = fileHeader['fileHeaders']

            fileName = str(counter).zfill(2) + '-' + csvFileName + '-' + fileDesc + '-' + fileDate + fileNameTest + '.csv'

            fileName = c42Lib.getFilePath(fileName)

            c42Lib.writeCSVappend (fileHeaderNames,fileName,writeMode)
            fileNames.append(fileName)


        logging.info ("---------- CSV Files Created --------------------------------")
        return fileNames

        #End setupCSVFiles


    # Print Text File Contents to Screen.
    # Prints to the contents of a (text) file to the screen.
    # Used for printing disclaimer text out in executable script builds

    @staticmethod
    def printFileToScreen (filename):

        logging.info("printFileToScreen: filename - [" + str(filename) + "]")

        filename = c42Lib.getFilePath(filename)

        try:

            fileToPrint = open(filename, 'r')
            contentsToPrint = fileToPrint.read()
            print (contentsToPrint)
            fileToPrint.close()

        except IOError:

            print ""
            print "**********"
            print "********** Error Reading File [ " + str(filename) + " ] "
            print "**********"
            print ""

        logging.debug("END OF printFileToScreen: filename - [" + str(filename) + "]")

    #End printFileToScreen


    @staticmethod
    def inputArguments (**kwargs):

        logging.info("inputArguments: [" + str(kwargs) + "]")

        arguments = {}
        noArguments = False
        hasArguments = False


        if kwargs:

            # Check if an arguments file exists

            if ('argumentsFile' in kwargs):

                fileName = kwargs['argumentsFile']

                fileName = c42Lib.getFilePath(fileName)

                if os.path.exists(fileName):
                    arguments = c42Lib.readCSVFiletoDictionary(fileName)
                    if len(arguments) > 0:
                        hasArguments = True

                else:
                    print ""
                    print "Manual Parameter Entry Required"
                    print ""

                    noArguments = True


            if 'argumentList' in kwargs and not hasArguments:

                    noArguments = False

                    argumentList = kwargs['argumentList']

                    for index, argument in enumerate (sorted(argumentList,key=argumentList.__getitem__)):

                        if argumentList[argument] is not None:
                            arguments[argument] = raw_input(argumentList[argument])
                        else:
                            arguments[argument] = None

            elif not hasArguments:

                noArguments = True

        if noArguments or len(arguments) < 1:
            print ""
            print "********** NO PARAMETERS PROVIDED"
            print ""
            print "********** EXITING"
            print ""
            sys.exit('System Exit: No Parameters Provided')

        return arguments

    @staticmethod
    def getFilePath(relativePath):
        logging.debug("getFilePath: [ " + str(relativePath) + " ]")

        try:
            base_path = sys._MEIPASS
            logging.debug("getFilePath - base_path :[ " + str(base_path) + " ]")

            # Get Platform Specific (mostly just Windows vs. the World)

            if str(os.name) != 'nt':
                # Find last directory slash

                logging.debug("getFilePath - os.name :[ " + str(os.name) + " ]")
                endOfPath = str(sys.executable).rfind('/')
                base_path = str(sys.executable)[:endOfPath+1]

                logging.debug("getFilePath - endOfPath :[ " + str(endOfPath) + " ]")
                logging.debug("getFilePath - base_path :[ " + str(base_path) + " ]")
            else:
                base_path = os.getcwd()
                logging.debug("getFilePath - base_path :[ " + str(base_path) + " ]")
        
        except Exception:
            
            base_path = os.path.abspath(".")
            logging.debug("getFilePath - base_path :[ " + str(base_path) + " ]")

        return os.path.join(base_path,relativePath)    

    @staticmethod
    def checkPathMakePath(filePath):

        try:

            os.makedirs(filePath)

        except OSError:

            if not os.path.isdir(filePath):

                # zero out file path if there is an issue
                filePath = ''

        return filePath
                

    # validateVersion method
    #
    # Inputs:
    #           version = version number #.#.# string - REQUIRED
    #           minorStrict = require the 2nd number to equal, otherwise must not be less than
    #           patchStrict = require the 3rd number to equal, otherwise must not be less than
    #
    # Output:
    #           True  if meets minimum version requirements
    #           False if does not meet minimum version requirements
    #
    # Note:
    #           Major version (1st #) must always be equal or greater than


    @staticmethod
    def validateVersion(**kwargs):

        versionOK   = True
        minorStrict = False
        patchStrict = False

        if 'version' in kwargs:
            scriptVersion = kwargs['version'].split('.')
            if len(scriptVersion) != 3:
                versionOK = False
        else:
            versionOK = False

        if 'majorStrict' in kwargs:
            majorStrict = kwargs['majorStrict']
        if 'minorStrict' in kwargs:
            minorStrict = kwargs['minorStrict']
        if 'patchStrict' in kwargs:
            patchStrict = kwargs['patchStrict']

        if majorStrict:
            if (scriptVersion[0] != c42Lib.cp_c42Lib_version[0]):
                versionOK = False
        elif (scriptVersion[0] < c42Lib.cp_c42Lib_version[0]):
            versionOK = False

        if minorStrict:
            if (scriptVersion[1] != c42Lib.cp_c42Lib_version[1]):
                versionOK = False
        elif (scriptVersion[1] < c42Lib.cp_c42Lib_version[1]):
            versionOK = False

        if patchStrict:
            if (scriptVersion[2] != c42Lib.cp_c42Lib_version[2]):
                versionOK = False
        elif (scriptVersion[2] < c42Lib.cp_c42Lib_version[2]):
            versionOK = False

        if not versionOK:
            print ""
            print "!!!!!!!!!! This script requires v" + str(requiredC42Lib) + " of the C42SharedLibary.py to run.\nPlease make sure you have the correct version of the shared library."
            print ""

        return versionOK

    @staticmethod
    def cls():
        os.system('cls' if os.name=='nt' else 'clear')



    @staticmethod
    def convertToBool(isItTrue):

        if isItTrue:
            isItTrue == str(isItTrue).lower()

            if isItTrue not in ('y','t','yes'):
                isItTrue == False
            else:
                isItTrue == True

        return isItTrue    

# class UserClass(object)


# class OrgClass(object)

# class DeviceClass(object)