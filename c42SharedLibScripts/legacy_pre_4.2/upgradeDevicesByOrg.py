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
#
# File: upgradeDevicesByOrg.py
# Author: AJ LaVenture, Code 42 Software
# Last Modified: 2-10-2014
#
# Specify organizaions and flag all devices to upgrade.
# 
"""upgradeDevicesByOrg Script

	Usage:
		upgradeDevicesByOrg.py  <orgId>


	Arguments:
		<orgId>		required id of the organizaion to send the upgrade to devices: 0 for all devices regardless of org.

	Options:
		-h --help     Show this screen.
		--version     Show version.

"""
from docopt import docopt
from c42SharedLibrary import c42Lib
import json
import logging
import requests
import getpass


if __name__ == '__main__':
    arguments = docopt(__doc__, version='upgradeDevicesByOrg 1.0')
    print(arguments)


c42Lib.cp_host = "http://aj-proappliance"
c42Lib.cp_port = "4280"
c42Lib.cp_username = "admin"
c42Lib.cp_password = getpass.getpass('Enter your CrashPlan console password: ') # You will be prompted for your password

c42Lib.cp_logLevel = "INFO"
c42Lib.cp_logFileName = "upgradeDevicesByOrg.log"
c42Lib.setLoggingLevel()


# ARG1 - Org ID
# cp_orgId = ""
# if len(sys.argv) > 1:
	# cp_orgId = str(sys.argv[1])


def performDeviceUpgradeByOrg(orgId):
	devices = ""
	if (orgId == "0"):
		#get devices for all orgs
		devices = c42Lib.getAllDevices()
	else:
		#run get devices
		devices = c42Lib.getAllDevicesByOrg(int(orgId))
	if (devices != "" and devices is not None):
		for index, device in enumerate(devices):
			#update device
			computerId = device['computerId']
			flaggedForUpgrade = c42Lib.putDeviceUpgrade(computerId)
			if flaggedForUpgrade:
				logging.info("computerId:[" + str(computerId) + "] flagged for upgrade")
			else:
				logging.info("computerId:[" + str(computerId) + "] failed to be flagged for upgrade")
	else:
		logging.info("No computers returned to flag for upgrade")

# get devices by org
# perform upgrade


# get all orgs
# get devices by org
# perform upgrade



def interpretParamsAndExecute():
	logging.info("upgradeDevicesByOrg Action")
	cp_orgId = arguments['<orgId>']
	if (cp_orgId is not None and cp_orgId != ""):
		orgToLog = cp_orgId
		if (orgToLog == "0"):
			orgToLog = "All Orgs"
		logging.info("Upgrading devices for OrgId: " + str(orgToLog))
		performDeviceUpgradeByOrg(cp_orgId)
	else:
		logging.error("Invalid first argument value. Please enter the orgId for Devices you wish to upgrade.")

interpretParamsAndExecute()
