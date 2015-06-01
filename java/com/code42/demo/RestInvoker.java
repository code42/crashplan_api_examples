package com.code42.demo;

import java.io.File;
import java.security.KeyManagementException;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.http.HttpEntity;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.conn.ssl.NoopHostnameVerifier;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.conn.ssl.TrustSelfSignedStrategy;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.apache.http.entity.mime.content.FileBody;
import org.apache.http.entity.mime.content.StringBody;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContextBuilder;
import org.apache.http.util.EntityUtils;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

import com.code42.demo.RestInvoker;

/**
 * RestInvoker is a generic utility class for invoking Code42 RESTful APIs.
 * It currently supports: httpGets, htttpPost and httpPostFile 
 * (see methods: getAPI, postAPI and postFileAPI for details)
 * 
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
 * Date: 02/22/2015
 * 
 * @author amir.kader@code42.com
 * 
 *	05/27/15: The code uses the SSLConnectionFactory but should still be modified 
 * 	for Production environments to properly import certifcates into the Java keystore.
 * 	The following items should be changed accordingly:      
 *  - TrustSelfSignedStrategy() in the instantiation of the SSLContextBuilder();
 *  - NoopHostnameVerifier.INSTANCE: HostNameVerification has been disabled in the SSLConnectionFactory
 */


public class RestInvoker {
	private static CredentialsProvider credsProvider;
	private static String ePoint; // protocol + host + port
	private static String sHost;
	private static int sPort;
	private static String uName;
	private static String pWord;
	private static Boolean ssl;
	SSLContextBuilder sslBuilder;
	SSLConnectionSocketFactory sslsf;

	private static final Log m_log = LogFactory.getLog(RestInvoker.class);
	
	public RestInvoker(String host, int hostPort, String userName, String password, Boolean useSSL) {
		sHost = host;
		sPort = hostPort;
		uName = userName;
		pWord = password;
		ssl = useSSL;
		if(!ssl) {
			ePoint = "http://" + sHost + ":" + sPort;
		} else {
			// use SSL
			ePoint = "https://" + sHost + ":" + sPort;
			sslBuilder = new SSLContextBuilder();
		    try {
				sslBuilder.loadTrustMaterial(null, new TrustSelfSignedStrategy());
			} catch (NoSuchAlgorithmException | KeyStoreException e) {
				// TODO Auto-generated catch block
				m_log.error("Unable to build trusted self signed cert");
				//m_log.debug(e.printStackTrace(), e);
			}
		   try {
			/* the NoopHostnameVerifier turns OFF host verification
			 * For Production environments you'll want to remove this.   
			 */
			sslsf = new SSLConnectionSocketFactory(sslBuilder.build(), NoopHostnameVerifier.INSTANCE);
		   } catch (KeyManagementException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		   } catch (NoSuchAlgorithmException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		   }
		}
		
		m_log.info("EndPoint set to: " + ePoint);
		credsProvider = new BasicCredentialsProvider();
		credsProvider.setCredentials(
					new AuthScope(sHost, sPort),
					new UsernamePasswordCredentials(uName, pWord));
		
	}
	
	/**
	 * Builds and executes HttpGet Request by appending the urlQuery parameter to the 
	 * serverHost:serverPort variables.  Returns the data payload response as a JSONObject. 
	 * 
	 * @param urlQuery
	 * @return org.json.simple.JSONObject
	 * @throws Exception
	 */
	public JSONObject getAPI(String urlQuery) throws Exception {
		HttpClientBuilder hcs;
		CloseableHttpClient httpClient;
		hcs = HttpClients.custom().setDefaultCredentialsProvider(credsProvider);
		if(ssl) {
			hcs.setSSLSocketFactory(sslsf);
		}
		httpClient = hcs.build();
		JSONObject data;
		try {
			HttpGet httpGet = new HttpGet(ePoint + urlQuery);
			m_log.info("Executing request: " + httpGet.getRequestLine());
			CloseableHttpResponse resp = httpClient.execute(httpGet);
			try {
				m_log.info("Respone: " + resp.getStatusLine());
				String jsonResponse = EntityUtils.toString(resp.getEntity()); // json response
				JSONParser jp = new JSONParser();
				JSONObject jObj = (JSONObject) jp.parse(jsonResponse);
				data = (JSONObject) jObj.get("data");
				m_log.debug(data);	
			} finally {
				resp.close();
			}
		} finally {
				httpClient.close();
			}
		return data;
	}
	
	/**
	 * Builds and executes an HttpPost Request by appending the urlQuery parameter to the 
	 * serverHost:serverPort variables and inserting the contents of the payload parameter.
	 * Returns the data payload response as a JSONObject. 
	 * 
	 * @param urlQuery
	 * @param payload
	 * @return org.json.simple.JSONObject
	 * @throws Exception
	 */
	 public JSONObject postAPI(String urlQuery, String payload) throws Exception {
		 HttpClientBuilder hcs;
		 CloseableHttpClient httpClient;
		 hcs = HttpClients.custom().setDefaultCredentialsProvider(credsProvider);
		 if(ssl) {
			hcs.setSSLSocketFactory(sslsf);
		 }
		 httpClient = hcs.build();
		 JSONObject data;
		 StringEntity payloadEntity = new StringEntity(payload, ContentType.APPLICATION_JSON);
		 try {
			 HttpPost httpPost = new HttpPost(ePoint + urlQuery);
			 m_log.info("Executing request : " + httpPost.getRequestLine());
			 m_log.debug("Payload : " + payload);
			 httpPost.setEntity(payloadEntity);
			 CloseableHttpResponse resp = httpClient.execute(httpPost);
			 try {
				 String jsonResponse = EntityUtils.toString(resp.getEntity());
				 JSONParser jp = new JSONParser();
				 JSONObject jObj = (JSONObject) jp.parse(jsonResponse);
				 data = (JSONObject) jObj.get("data");
				 m_log.debug(data);
			 
			 } finally {
				 resp.close();
			 }
		 } finally {
			 httpClient.close();
		 }
		 return data; 
	}
	
	 /**
	  * Execuites CODE42 api/File to upload a single file into the root directory of the specified planUid
	  * If the file is succesfully uploaded the response code of 204 is returned.
	  * 
	  * @param planUid 
	  * @param sessionId
	  * @param file
	  * @return HTTP Response code as int
	  * @throws Exception
	  */
	 
	 public int postFileAPI(String planUid, String sessionId, File file) throws Exception {
		 
		int respCode;
		HttpClientBuilder hcs;
		CloseableHttpClient httpClient;
		hcs = HttpClients.custom().setDefaultCredentialsProvider(credsProvider);
		if(ssl) {
			hcs.setSSLSocketFactory(sslsf);
		}
		httpClient = hcs.build();
		StringBody planId = new StringBody(planUid, ContentType.TEXT_PLAIN);
		StringBody sId = new StringBody(sessionId, ContentType.TEXT_PLAIN);
		
		try {
			HttpPost httpPost = new HttpPost(ePoint + "/api/File");
			FileBody fb = new FileBody(file);
			HttpEntity reqEntity = MultipartEntityBuilder.create().addPart("file", fb).addPart("planUid", planId).addPart("sessionId", sId).build();
			httpPost.setEntity(reqEntity);
			CloseableHttpResponse resp = httpClient.execute(httpPost);
			try {
				m_log.info("executing " + httpPost.getRequestLine());
				m_log.info(resp.getStatusLine());
				respCode = resp.getStatusLine().getStatusCode();
			} finally {
				resp.close();
			}
			
		} finally {
			httpClient.close();
		}
		
		return respCode;
	} 

}
