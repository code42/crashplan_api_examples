package com.code42.demo.shareplan;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;
import com.code42.demo.RestInvoker;

/**
 * AddFileToPlan is an example of invoking CODE42 RESTful
 * calls to upload a single file to a specified SharePlan as
 * specified by the planGuid.  It calls com.code42.demo.RestInvoker 
 * to make REST calls 
 * The code is dependent on two external projects and assoicated libraries:
 * 	- JSON-Simple : https://code.google.com/p/json-simple/
 *  - Apache HttpComponents : https://hc.apache.org/httpcomponents-client-ga/
 *  Resulting in addition of the following jars to the classpath:
 *  	- json-simple-1.1.1.jar
 *  	- httpcore-4.4.jar
 *  	- httpclient-4.4.jar
 *  	- commons-logging-1.2.jar
 *  	- commons-codec-1.9.jar
 *  	- httpmime-4.4.jar
 *  
 * Date: 02/09/2014
 * 
 * @author amir.kader@code42.com
 * 
 *
 */


public class AddFileToPlan {
	private static String filePath;
	private static String planId;
	private static String  serverHost = "demo.code42.com";
	private static int serverPort = 4280;
	private static String username;
	private static String password;

	
	public static void main(String[] args) throws Exception {
		//
		 if(args != null && args.length < 1) {
			printHelp();
			System.exit(-1);
		 } else if(args.length == 1 && args[0].startsWith("-f"))
			 loadConfig("AddFileToPlan-config.properties");
		 else if(args.length > 5) {
			 filePath = args[0];
			 planId = args[1];
			 username = args[2];
			 password = args[3];
			 serverHost = args[4];
			 if(args[5]!=null & args[5].length() > 0) {
				serverPort = Integer.parseInt(args[5]);
			}
		 }
		 else {
			 printHelp();
			 System.exit(-1);
		 }
		 
		 RestInvoker restInv = new RestInvoker(serverHost, serverPort, username, password);
		 String dataKeyToken = (String) restInv.getAPI("/api/PlanDataKeyToken/" + planId).get("token");
		 System.out.println("dataKeyToken: " + dataKeyToken);
		 
		 String pArchiveSession = "{\"planUid\" : \"" + planId + "\", \"planDataKeyToken\": \"" + dataKeyToken + "\"}";   
		 String sessionId = (String) restInv.postAPI("/api/PlanArchiveSession", pArchiveSession).get("planSessionId");
		 System.out.println("sessionId: " + sessionId);
		 
		 File uploadFile = new File(filePath);
		 if(uploadFile.exists()) {
				int fileApiRespCode = restInv.postFileAPI(planId, sessionId, uploadFile);
				System.out.println("api/File upload resulted in response code: "+ fileApiRespCode);
			} else {
				System.out.println("file: " + filePath + " does not exist!");
			}
		 
	}
	 /**
	  * Utility method for loading the program arguments from a properties file.
	  * 
	  * 
	  * @param propFile
	  */
	 private static void loadConfig(String propFile) {
		 try {
			 FileInputStream fis = new FileInputStream(propFile);
			 Properties config = new Properties();
			 config.load(fis);
			 
			 if(config.getProperty("ServerHost")!= null && config.getProperty("ServerHost").length() > 0) 
				 serverHost = config.getProperty("ServerHost").trim();
			 
			 String sPort = config.getProperty("ServerPort").trim();
			 if(sPort!= null &sPort.length() > 0) 
				 serverPort = Integer.parseInt(sPort);	 
			 
			 String pId = config.getProperty("PlanId").trim();
			 if(pId != null && pId.length() > 0) 
				 planId= pId;
			 
			 String user = config.getProperty("User");
			 if(user != null && user.length() > 0)
				 username = user; 
			 
			 String pass = config.getProperty("Password");
			 if(pass != null && pass.length() > 0) 
				 password = pass;
			 String f = config.getProperty("File");
			 if(f != null && f.length() > 0)
				 filePath = f;
			 
		 } catch (IOException ioe) {
			 System.out.println("unable to load config file: " + propFile);
			 ioe.printStackTrace();
		 }
		
	 }
	 private static void printHelp(){
		 System.out.println("com.code42.demo.shareplan.AddFileToPlan adds a selected file to the root directory of SharePlan as specified by the Plan's GUID\n"
					+ "The program will take input parameters as command line arguments or load them from a config file.\n"
					+ "\tjava AddFileToPlan [filePath] [planID] [username] [password] [host] [port]\n"
					+ "\t\t[filePath] : is the full filePath and name of the file to upload to a SharePlan\n"
					+ "\t\t[planID] : is the GUID of the SharePlan you'd like to add the file to\n" 
					+ "\t\t[username] : is the account to make the calls as. The account must have contributor access to the Plan\n"
					+ "\t\t[paswword] : is the password for the username account specified\n"
					+ "\t\t[host] : is the serverhost to connect to\n"
					+ "\t\t[port] : is the port the application is running, default 4280");
		 System.out.println("\nThe program will load the above parameters from a properties file if you specify -f as the first command line argument"
		 		+ "\nIt will by defualt look for the config.properties file in the root directory that the java program is placed.\n" 
				+ "\nFor example:\n " 
		 		+ "\tcom.code42.demo.shareplan.AddFileToPlan -f");
		 
	 }

}
