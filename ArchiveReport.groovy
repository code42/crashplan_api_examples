
/**
 * @author Marc Johnson
 * (c) Code42 Software
 */
import groovy.json.JsonSlurper

import java.io.File;
import java.text.SimpleDateFormat

// Archive Report
class showArchiveReport {

	def scmd = new shellCmd()	
	def slurper = new JsonSlurper()
	def delim = "\t"
	
/* 
 * ShowArchiveReport example usage:
 * 
 * - All restores performed by User in date range
 * - All restores of User's archives in date range
 * - All restores of User's specific archive in date range
 * - All restores in date range	
 * 
 */
	def showArchiveReport(server, cred, userId, fromDate="", toDate="", devices="") {
		
		def json = exec(server, cred, "/api/RestoreRecord?userId="+userId)

		println "Initiated by (usename)"+delim+"Archive source"+delim+"Archive destination"+delim+"Type"+delim+"Size"+delim+"Count"+delim+"Finished"+delim+"Start"+delim+"End"+delim+"Problems Count"+delim+"Failed Checksums"
		
		json.data.each {
			
			def user = exec(server, cred, "/api/user/"+it.requestingUserId)
			
			print user.data.username + delim //+ " (" + user.data.firstName + " " + user.data.lastName + ")" 
			
			def sourceComputer = exec(server, cred, "/api/computer/"+it.sourceComputerId)
			
			print sourceComputer.data.name + delim
			
			def destComputer = exec(server, cred, "/api/computer/"+it.targetComputerId)
			
			print destComputer.data.name + delim
			
			print it.type + delim
			print it.numBytes + " bytes" + delim
			print it.numFiles + " file(s)" + delim
			print (it.canceled == true ? "Completed" : "Cancelled") + delim
			
			print new Date(it.startDate).toString() + delim
			print (it.completedDate != null ? new Date(it.completedDate) : new Date(it.startDate)).toString() + delim
			
			print (it.problemCount != null ? it.problemCount : "0").toString() + delim
			println (it.failedChecksumCount != null ? it.failedChecksumCount : 0).toString()

		} // each
	} // method
	def exec(server, cred, cmd, args="") {
		
		def curlcmd = "curl -ku "+ cred + " -H 'Content-Type: application/json'"
		def fullcmd = curlcmd + " " + args + " " + '"' + server + cmd + '"'
//		println fullcmd
		def text = scmd.executeOnShell(fullcmd)
		if (text.trim() != "") text = slurper.parseText(text)
		return (text)
		
	}
} // class
class shellCmd {

	// generic shell execution that works well with parameters (for curl)
	def executeOnShell(String command) {
		return executeOnShell(command, new File(System.properties.'user.dir'))
	}

	def executeOnShell(String command, File workingDir) {
	//	println command
		
		def outtext = ""
		try {
			ProcessBuilder pb = new ProcessBuilder(addShellPrefix(command));
			pb.directory(workingDir)
			pb.redirectErrorStream(false); 
				
			Process p = pb.start();
			InputStreamReader isr = new  InputStreamReader(p.getInputStream());
			BufferedReader br = new BufferedReader(isr);
		
			String lineRead;
			while ((lineRead = br.readLine()) != null) {
				outtext += lineRead
			}		
			int rc = p.waitFor();
			// TODO error handling for non-zero rc
		}
		catch (IOException e) {
			e.printStackTrace(); // or log it, or otherwise handle it
		}
		catch (InterruptedException ie) {
			ie.printStackTrace(); // or log it, or otherwise handle it
		}
		return outtext
	}
	// shell invocation (for curl)
	private def addShellPrefix(String command) {
		def commandArray = new String[3]
		commandArray[0] = "sh"
		commandArray[1] = "-c"
		commandArray[2] = command
		return commandArray
	}
}

new showArchiveReport("https://myserver:4285", "dev_498468@498468.com:mypassword", 130005)
