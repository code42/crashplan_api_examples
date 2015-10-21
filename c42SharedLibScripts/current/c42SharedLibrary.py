# File: c42SharedLibrary.py
# Author: AJ LaVenture
# Author: Paul Hirst
# Author: Hank Brekke
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

class c42Lib(object):

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
    cp_magic_restoreRecordKey = '987db1c5-8840-41f1-8c97-460d03347895'

    # REST API Calls
    cp_api_authToken = "/api/AuthToken"
    cp_api_storageAuthToken = "/api/StorageAuthToken"
    cp_api_loginToken = "/api/LoginToken"
    cp_api_networkTest = "/api/NetworkTest"
    cp_api_plan = "/api/Plan"
    cp_api_fileContent = "/api/FileContent"
    cp_api_fileMetadata = "/api/FileMetadata"
    cp_api_storage = "/api/Storage"
    cp_api_ping = "/api/Ping"
    cp_api_userRole = "/api/UserRole"
    cp_api_user = "/api/User"
    cp_api_org = "/api/Org"
    cp_api_orgSettings = "/api/OrgSettings"
    cp_api_archive = "/api/Archive"
    cp_api_deviceUpgrade = "/api/DeviceUpgrade"
    cp_api_computer = "/api/Computer"
    cp_api_destination = "/api/Destination"
    cp_api_computerBlock = "/api/ComputerBlock"
    cp_api_userMoveProcess = "/api/UserMoveProcess"
    cp_api_deactivateUser = "/api/UserDeactivation"
    cp_api_deacivateDevice = "/api/ComputerDeactivation"
    cp_api_cli = "/api/cli"
    # cp_api_restoreHistory = "/api/restoreHistory"
    #?pgNum=1&pgSize=50&srtKey=startDate&srtDir=desc&days=9999&orgId=35
    cp_api_restoreRecord = "/api/RestoreRecord"
    cp_api_archiveMetadata = "/api/ArchiveMetadata"
    cp_api_server = "/api/Server"
    cp_api_storePoint = "/api/StorePoint"
    cp_api_dataKeyToken = "/api/DataKeyToken"
    cp_api_webRestoreSession = "/api/WebRestoreSession"
    cp_api_pushRestoreJob = "/api/PushRestoreJob"
    cp_api_webRestoreSearch = "/api/WebRestoreSearch"
    cp_api_webRestoreJob = "/api/WebRestoreJob"
    cp_api_webRestoreTreeNode = "/api/WebRestoreTreeNode"
    cp_api_webRestoreJobResult = "/api/WebRestoreJobResult"

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
                header["Authorization"] = "login_token {0}".format(kwargs['login_token'])
            elif kwargs and 'auth_token' in kwargs:
                header["Authorization"] = "token {0}".format(kwargs['auth_token'])
            else:
                header["Authorization"] = c42Lib.getAuthHeader(c42Lib.cp_username,c42Lib.cp_password)
        else:
            header['Authorization'] = c42Lib.cp_authorization

        header["Content-Type"] = "application/json"

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
        header = c42Lib.getRequestHeaders(**kwargs)
        url = c42Lib.getRequestUrl(cp_api, **kwargs)

        # for our purposes, we always want this set for fileContent requests so that a restore record
        # is not stamped out on the server
        if cp_api == c42Lib.cp_api_fileContent:
            assert 'restoreRecordKey' in params and params['restoreRecordKey'] is cp_magic_restoreRecordKey

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

    #
    # Params:
    # private address: address to check if reachbale
    # Returns: Check if address is reachable. None on failure
    #
    @staticmethod
    def reachableNetworkTest(private_address, **kwargs):
        payload = {
            "testType":"reachable",
            "address":private_address,
            "privateAddress":True
        }

        r = c42Lib.executeRequest("post", c42Lib.cp_api_networkTest, {}, payload, **kwargs)
        contents = r.content.decode("UTF-8")
        binary = json.loads(contents)
        return binary['data'] if 'data' in binary else None

    #
    # Params:
    # host (kwargs): host location to use
    # port (kwargs): port to use
    # login_token (kwargs): necessary for storage nodes
    # Returns: Auth token. None on failure
    #
    @staticmethod
    def requestAuthToken(**kwargs):
        payload = {
            "sendCookieHeader":True
        }
        r = c42Lib.executeRequest("post", c42Lib.cp_api_authToken, {}, payload, **kwargs)
        if r.status_code != 200:
            logging.debug("Failed to get auth token")
            return None

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
        binary = json.loads(r.content.decode('UTF-8'))
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


    #
    # getUserById(userId):
    # returns the user json object of the requested userId
    # params:
    # userId: the id of the user within the system's database
    #
    @staticmethod
    def getUserById(userId):
        logging.info("getUser-params:userId[" + str(userId) + "]")

        params = {}
        params['incAll'] = 'true'
        # params['idType'] = 'uid' # Needed for the 4.x series and beyond
        payload = {}


        r = c42Lib.executeRequest("get", c42Lib.cp_api_user + "/" + str(userId), params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        user = binary['data']
        return user

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

        r = c42Lib.executeRequest("get", c42Lib.cp_api_user + "?" ,params, payload)

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
        params['orgId'] = orgId
        params['pgNum'] = str(pgNum)
        params['pgSize'] = str(c42Lib.MAX_PAGE_NUM)
        params['active'] = 'true'

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
    def getUsersPaged(pgNum,params = {}):
        logging.info("getUsersPaged-params:pgNum[" + str(pgNum) + "]")

        # headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
        # url = cp_host + ":" + cp_port + cp_api_user
        params['pgNum'] = str(pgNum)
        params['pgSize'] = str(c42Lib.MAX_PAGE_NUM)

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
    # putUserUpdate(userId, payload):
    # updates a users information based on the payload passed
    # params:
    # userId - id for the user to update
    # payload - json object containing name / value pairs for values to update
    # returns: user object after the update
    #

    @staticmethod
    def putUserUpdate(userId, payload):
        logging.info("putUserUpdate-params:userId[" + str(userId) + "],payload[" + str(payload) + "]")

        if (payload is not None and payload != ""):
            params = {}
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
        if (userId is not None and userId != ""):
            if deactivate:
                r = c42Lib.executeRequest("put", c42Lib.cp_api_deactivateUser+"/"+str(userId),"","")
                logging.debug('Deactivate Call Status: '+str(r.status_code))
                if not (r.status_code == ""):
                    return True
                else:
                    return False
            else:
                r = c42Lib.executeRequest("delete", c42Lib.cp_api_deactivateUser+"/"+str(userId),"","")
                logging.debug('Deactivate Call Status: '+str(r.status_code))
                if not (r.status_code == ""):
                    return True
                else:
                    return False
        else:
            logging.error("putUserDeactivate has no userID to act on")


    #
    # postUserMoveProcess(userId, orgId):
    # posts request to move use into specified organization
    # params:
    # userId - id of the user for the move request
    # orgId - destination org for the user
    # returns: true if 204, respose object if 500, else false
    #

    @staticmethod
    def postUserMoveProcess(userId, orgId):
        logging.info("postUserMoveProcess-params:userId[" + str(userId) + "],orgId[" + str(orgId) + "]")

        params = {}
        payload = {}
        payload["userId"] = userId
        payload["parentOrgId"] = orgId

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
    # getOrg(orgId):
    # Returns all organization data for specified organization
    # params:
    # orgId - id of the organization you want to return
    # Returns:
    # json object
    #

    @staticmethod
    def getOrg(orgId):
        logging.info("getOrg-params:orgId[" + str(orgId) + "]")

        params = {}
        params['incAll'] = 'true'
        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_org + "/" + str(orgId), params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        org = binary['data']
        return org

    #
    # getOrgs(pgNum):
    # returns json list object of all users for the requested page number
    # params:
    # pgNum - page request for information (starting with 1)
    #

    @staticmethod
    def getOrgs(pgNum):
        logging.info("getOrgs-params:pgNum[" + str(pgNum) + "]")

        params = {}
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

        params = {}
        if kwargs and 'incBackupUsage' in kwargs:
                params["incBackupUsage"] = "{0}".format(kwargs['incBackupUsage'])
        params['idType'] = "guid"

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_computer + "/" + str(guid), params, payload)

        logging.debug(r.text)

        if r.text != '[{"name":"SYSTEM","description":"java.lang.NullPointerException"}]':

            content = r.content

            binary = json.loads(content)

            logging.debug(binary)

            device = binary['data']

        else:

            device = 'NONE'

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
    # getDeviceByName(deviceName):
    # returns device information based on computerId
    # params:
    # deviceName: name of device
    #

    @staticmethod
    def getDeviceByName(deviceName, incAll):
        logging.info("getDeviceByName-params:name[" + deviceName + "]")

        params = {}
        params['q'] = deviceName
        params['incAll'] = incAll

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
        logging.info("getDevicesCustomParams-params:pgNum[" + str(pgNum) + "]:params[" + str(params) + "]")

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

        devices = binary['data']['computers']
        return devices
    #
    # getDevicesByOrgPaged(orgId, pgNum):
    # returns devices by organization for requested page number within a single json object
    #

    @staticmethod
    def getDevicesByOrgPaged(orgId, pgNum):
        logging.info("getDevicesByOrgPaged-params:orgId[" + str(orgId) + "]:pgNum[" + str(pgNum) + "]")

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






## TO BE DELETED
##========================================================================================



    @staticmethod
    def getArchiveByStorePointId(storePointId):
        logging.info("getArchiveByStorePointId-params:storePointId[" + str(storePointId) + "]")
        currentPage = 1
        keepLooping = True
        fullList = []
        params = {}
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


    # @staticmethod
    # def getAllArchives():







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

        params['pgSize'] = c42Lib.MAX_PAGE_NUM
        params['pgNum'] = pgNum

        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_restoreHistory, params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        archives = binary['data']['restoreEvents']

        return archives


    # only 3.6.2.1 and greater - json errors in pervious versions
    # will return array of info for every file within given archive
    # performance is not expected to be great when looking at large archives - impacted by number of files in archive
    # guid is int, decrypt is boolean

    # saveToDisk - will write out the response to a .json file
    @staticmethod
    def getArchiveMetadata2(guid, decrypt, saveToDisk):
        logging.info("getArchiveMetadata-params:guid["+str(guid)+"]:decrypt["+str(decrypt)+"]")

        params = {}
        if (decrypt):
            params['decryptPaths'] = "true"
        # always stream the response - remove memory limitation on requests library
        params['stream'] = "True"
        payload = {}

        r = c42Lib.executeRequest("get", c42Lib.cp_api_archiveMetadata + "/" + str(guid), params, payload)

        # logging.debug(r.text)
        #null response on private passwords

        # http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
        if saveToDisk:
            # print r.text
            local_filename = "json/archiveMetadata_"+str(guid)+".json"
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
                return local_filename
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
                    archiveMetadata = binary['data']
                    del binary
                    return archiveMetadata
                else:
                    return ""
            else:
                return ""

    @staticmethod
    def getArchiveMetadata(guid, decrypt):
        c42Lib.getArchiveMetadata2(guid, decrypt, False)
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

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        server = binary['data']
        return server

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

        r = c42Lib.executeRequest("get", c42Lib.cp_api_storePoint + "/" + str(storePointId), params, payload)

        logging.debug(r.text)

        content = r.content
        binary = json.loads(content)
        logging.debug(binary)

        storePoint = binary['data']
        return storePoint


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
    def setLoggingLevel():
        # set up logging to file
        logging.basicConfig(
                            #level=logging.DEBUG,
                            level = logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            # filename='EditUserRoles.log',
                            filename = str(c42Lib.cp_logFileName),
                            filemode='w')
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()

        if(c42Lib.cp_logLevel=="DEBUG"):
            console.setLevel(logging.DEBUG)
            # console.setLevel(logging.INFO)
        else:
            console.setLevel(logging.INFO)

        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)


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

        csvfile = open(csvFileName, 'rU')
        reader = csv.reader(csvfile, dialect=csv.excel_tab)
        for row in reader:
            fileList.append(row)

        return fileList


    # CSV Write & Append Method
    # Will apped to a CSV with n number of elements.  Pass in a list and it writes the CSV.

    @staticmethod
    def writeCSVappend(listtowrite,filenametowrite,writeType):
        logging.debug("writeCSVappend:file - [" + filenametowrite + "]")

        #Check the length of the list to write.  If more than one item, then iterate through the list

        if (not isinstance(listtowrite, basestring)): #More than 1 item in list?
            # Correctly append to a CSV file
            output = open(filenametowrite, writeType) # Open the file to append to it

            # stufftowrite = []

            writestring = ''
            itemstowrite = ''
            itemsToWriteeEncoded = ''

            for stufftowrite in listtowrite:
                if (isinstance (stufftowrite,(int)) or isinstance(stufftowrite,(float))):
                    itemsToWriteeEncoded = stufftowrite
            
                elif stufftowrite is not None: 
                    itemsToWriteeEncoded = stufftowrite.encode('utf8') # encoding protects against crashes
            
                else:
                    itemsToWriteeEncoded = stufftowrite
                writestring = writestring + str(itemsToWriteeEncoded) + ','

            writestring = writestring[:-1] + "\n" # Remove an extra space at the end of the string and append a return
            output.write (writestring)
            output.close

        else: #What happens if there is only one item and not a list
            # Correctly append to a CSV file
            output = open(filenametowrite, writeType) # Open the file to append to it

            
            if (isinstance (listtowrite,(int)) or isinstance(listtowrite,(float))):
                itemsToWriteeEncoded = listtowrite # if the item is an integer, just add it to the list
            
            elif listtowrite is not None: 
                itemsToWriteeEncoded = listtowrite.encode
            
            else: #All other cases
                itemsToWriteeEncoded = listtowrite.encode('utf8') # encoding protects against crashes
            
            writestring = str(itemsToWriteeEncoded)
            writestring = writestring + "\n" # Remove an extra space at the end of the string and append a return
            output.write (writestring)
            output.close
    
        return


# class UserClass(object)


# class OrgClass(object)

# class DeviceClass(object)
