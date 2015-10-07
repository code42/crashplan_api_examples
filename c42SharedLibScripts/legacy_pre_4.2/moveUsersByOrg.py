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


c42Lib.cp_host = "http://aj-proappliance"
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
