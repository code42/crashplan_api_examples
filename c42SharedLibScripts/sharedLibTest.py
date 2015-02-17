from c42SharedLibrary import c42Lib
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
import getpass

# Test values
c42Lib.cp_host = "http://localhost"
c42Lib.cp_port = "4280"
c42Lib.cp_username = "admin"
# c42Lib.cp_password = "admin"
c42Lib.cp_password = getpass.getpass('Enter your CrashPlan console password: ') # You will be prompted for your password
c42Lib.cp_logLevel = "DEBUG"
c42Lib.cp_logFileName = "sharedLibTest.log"
c42Lib.setLoggingLevel()


# users = c42Lib.generaticLoopUntilEmpty()
# servers = c42Lib.getServersByDestinationId(2)
# restoreList = c42Lib.getRestoreHistoryForOrgId(36)
# restoreList = c42Lib.getRestoreHistoryForUserId(3)
restoreList = c42Lib.getRestoreHistoryForComputerId(11)

print restoreList
# payload = {'orgId': '0', 'pgNum': str(1), 'pgSize': str(c42Lib.MAX_PAGE_NUM)}

# r = c42Lib.executeRequest("get", c42Lib.cp_api_user, payload)

# logging.debug(r.text)

# content = r.content
# binary = json.loads(content)
# logging.debug(binary)

# users = binary['data']
# print users

# print c42Lib.getAllUsers()
# c42Lib.getDevicesPageCountByOrg(3)
# users = c42Lib.getAllUsersByOrg(3)

# http://aj-proappliance:4280/api/User?orgId=3&pgNum=1&pgSize=250&active=true
# orgId = "35"
# pgNum = 1


# header = c42Lib.getRequestHeaders()
# url = c42Lib.getRequestUrl(c42Lib.cp_api_user)
# payload = {'orgId': orgId, 'pgNum': str(pgNum), 'pgSize': str(c42Lib.MAX_PAGE_NUM), 'active': 'true'}
# logging.info(str(payload))
# r = requests.get(url, params=payload, headers=header)
# content = r.content
# binary = json.loads(content)
# logging.debug(binary)


# users = binary['data']['users']

# users = c42Lib.getUsersByOrgPaged(35, 1)
# for user in users:
# 	userId = user["userId"]
# 	print "--------------"
# 	print userId

# c42Lib.getArchivesPageCount('serverId',3)
# c42Lib.getArchiveByServerId(3)
