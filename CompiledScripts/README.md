# Code42 Compiled Scripts
Here you will find scripts you can download and use right away, they have all been compiled from their like-named python source in other folders.

### licenseAvailabilityReport_2_0_1.exe
Creates a list of users whose license usage will expire at a future date

        Usage:
                licenseAvailabilityReport.py [-l] [(u <username>) | (c <credentialfile>)] [(s <serverinfofile>) | m (<serverURL> <serverPort>)] [--filePath=<savefilepath>] [--orgId=<limitToOrgs>] [--logLevel=<logLevel>]

        Arguments:
                <username>              Add your username - you will be prompted for your password
                <credentialfile>                Enter a base64 encoded creditials file location
                <serverinfofile>                File to grab the host name & port
                <serverURL>                     Server URL
                <serverPort>            Server Port
                <savefilepath>          File Path for log and CSV files.  Must exist before running script.
                <logLevel>                      Logging Level - defaults to INFO.  Values are INFO, DEBUG and ERROR
                u               flag to enter username then be prompted for password
                c               flag to enter the name of a credentials file.
                s               flag to read server info from a file
                m               flag to manually enter server URL and Port


        Options:

                -f, --filePath=<savefilepath>           File Path for log and CSV files - optional. [default: '']
                -o, --orgId=<limitToOrgs>       Limit list to this comma separated list of orgs (no spaces)
                -e              Execute mode - otherwise defaults to test mode.
                -q              Quit processing after the days connected has been reached
                -l              Turn off logging to console
                -h, --help      Show this screen.
                --version       Show version.
