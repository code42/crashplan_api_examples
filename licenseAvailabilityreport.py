# This script lists the "free up" date licenses based on their cold storage expiration date.
# Only users with all of their devices in cold storage are eligible to release a license.
# python licenseAvailabilityreport.py verbose 
# python licenseAvailabilityreport.py noverbose
		logging.info('Total Storepoints with Cold Storage Archives: ' + str(len(storepointList)))
	logging.info('Get a count of devices for the list of users with active devices.')
	logging.info('There are ' + str(len(activeUsercount)) + ' users with at least one active device.')
						computerNamedecoded = computerName.encode('utf-8')		