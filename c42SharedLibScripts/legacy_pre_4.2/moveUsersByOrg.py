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
# File: moveUsersByOrg.py
# Author: AJ LaVenture, Code 42 Software
# Last Modified: 2-10-2014
#
# Specify source and destination organizaions and move all users
# 
"""moveUsersByOrg Script

	Usage:
		moveUsersByOrg.py  <src_orgId> <dest_orgId>


	Arguments:
		<src_orgId>		required id of the organizaion from which all users will be moved FROM.
		<dest_orgId>	required id of the organizaion for which all users in the src will be moved TO.

	Options:
		-h --help     Show this screen.
		--version     Show version.

"""
from docopt import docopt
from c42SharedLibrary import c42Lib
import json
import csv
import logging
import requests
import getpass


if __name__ == '__main__':
    arguments = docopt(__doc__, version='moveUsersByOrg 1.0')
    print(arguments)


c42Lib.cp_host = "http://aj-proserver"
c42Lib.cp_port = "4280"
c42Lib.cp_username = "admin"
c42Lib.cp_password = getpass.getpass('Enter your CrashPlan console password: ') # You will be prompted for your password

c42Lib.cp_logLevel = "INFO"
c42Lib.cp_logFileName = "moveUsersByOrg.log"
c42Lib.setLoggingLevel()



# ARG1 - Source Org ID
# ARG2 - Destination Org ID
# cp_src_orgId = ""
# cp_dest_orgId = ""
# if len(sys.argv) == 3:
# 	cp_src_orgId = str(sys.argv[1])
# 	cp_dest_orgId = str(sys.argv[2])

def performUserMove(src_orgId, dest_orgId):
	logging.info("performUserMove-params:src_orgId["+src_orgId+"],dest_orgId["+dest_orgId+"]")
	
	users = c42Lib.getAllUsersByOrg(src_orgId)
	# logging.info(users)

	for index, user in enumerate(users):
		userId = user["userId"]
		
		userMoved = c42Lib.postUserMoveProcess(userId, dest_orgId)
		if (userMoved):
			logging.info("user["+str(userId)+"] moved")
		else:
			logging.info("user["+str(userId)+"] NOT moved - " + str(userMoved))



def interpretParamsAndExecute():
	logging.info("moveUsersByOrg Action")

	cp_src_orgId = arguments['<src_orgId>']
	cp_dest_orgId = arguments['<dest_orgId>']

	if (cp_src_orgId is not None and cp_src_orgId != "") and (cp_dest_orgId is not None and cp_dest_orgId != ""):
		if (cp_src_orgId != cp_dest_orgId):
			logging.info("Source orgId:[" + str(cp_src_orgId) + "]")
			logging.info("Destination orgId:[" + str(cp_dest_orgId) + "]")
			performUserMove(cp_src_orgId, cp_dest_orgId)
		else:
			logging.error("Source and Destination orgs cannot be the same value.")
	else:
		logging.error("Invalid arguments value. Please enter the Source Org Id first and the Destination Org Id second to move users.")

interpretParamsAndExecute()
