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

# Test values
c42Lib.cp_host = "http://aj-proappliance"
c42Lib.cp_port = "4280"
c42Lib.cp_username = "admin"
c42Lib.cp_password = "admin"
c42Lib.cp_logLevel = "INFO"
c42Lib.cp_logFileName = "sharedLibTest.log"
c42Lib.setLoggingLevel()

payload = {'orgId': '0', 'pgNum': str(1), 'pgSize': str(c42Lib.MAX_PAGE_NUM)}

r = c42Lib.executeRequest("get", c42Lib.cp_api_user, payload)

logging.debug(r.text)

content = r.content
binary = json.loads(content)
logging.debug(binary)

users = binary['data']
print users
