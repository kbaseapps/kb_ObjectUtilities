package us.kbase.kbobjectutilities;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import us.kbase.auth.AuthToken;
import us.kbase.common.service.JsonClientCaller;
import us.kbase.common.service.JsonClientException;
import us.kbase.common.service.RpcContext;
import us.kbase.common.service.UnauthorizedException;

/**
 * <p>Original spec-file module name: kb_ObjectUtilities</p>
 * <pre>
 * ** A KBase module: kb_ObjectUtilities
 * **
 * ** This module contains basic utility Apps for manipulating objects (other than Reads and Sets, which are found in kb_ReadsUtilities and kb_SetUtilities)
 * </pre>
 */
public class KbObjectUtilitiesClient {
    private JsonClientCaller caller;
    private String serviceVersion = null;


    /** Constructs a client with a custom URL and no user credentials.
     * @param url the URL of the service.
     */
    public KbObjectUtilitiesClient(URL url) {
        caller = new JsonClientCaller(url);
    }
    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param token the user's authorization token.
     * @throws UnauthorizedException if the token is not valid.
     * @throws IOException if an IOException occurs when checking the token's
     * validity.
     */
    public KbObjectUtilitiesClient(URL url, AuthToken token) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, token);
    }

    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param user the user name.
     * @param password the password for the user name.
     * @throws UnauthorizedException if the credentials are not valid.
     * @throws IOException if an IOException occurs when checking the user's
     * credentials.
     */
    public KbObjectUtilitiesClient(URL url, String user, String password) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, user, password);
    }

    /** Constructs a client with a custom URL
     * and a custom authorization service URL.
     * @param url the URL of the service.
     * @param user the user name.
     * @param password the password for the user name.
     * @param auth the URL of the authorization server.
     * @throws UnauthorizedException if the credentials are not valid.
     * @throws IOException if an IOException occurs when checking the user's
     * credentials.
     */
    public KbObjectUtilitiesClient(URL url, String user, String password, URL auth) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, user, password, auth);
    }

    /** Get the token this client uses to communicate with the server.
     * @return the authorization token.
     */
    public AuthToken getToken() {
        return caller.getToken();
    }

    /** Get the URL of the service with which this client communicates.
     * @return the service URL.
     */
    public URL getURL() {
        return caller.getURL();
    }

    /** Set the timeout between establishing a connection to a server and
     * receiving a response. A value of zero or null implies no timeout.
     * @param milliseconds the milliseconds to wait before timing out when
     * attempting to read from a server.
     */
    public void setConnectionReadTimeOut(Integer milliseconds) {
        this.caller.setConnectionReadTimeOut(milliseconds);
    }

    /** Check if this client allows insecure http (vs https) connections.
     * @return true if insecure connections are allowed.
     */
    public boolean isInsecureHttpConnectionAllowed() {
        return caller.isInsecureHttpConnectionAllowed();
    }

    /** Deprecated. Use isInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public boolean isAuthAllowedForHttp() {
        return caller.isAuthAllowedForHttp();
    }

    /** Set whether insecure http (vs https) connections should be allowed by
     * this client.
     * @param allowed true to allow insecure connections. Default false
     */
    public void setIsInsecureHttpConnectionAllowed(boolean allowed) {
        caller.setInsecureHttpConnectionAllowed(allowed);
    }

    /** Deprecated. Use setIsInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public void setAuthAllowedForHttp(boolean isAuthAllowedForHttp) {
        caller.setAuthAllowedForHttp(isAuthAllowedForHttp);
    }

    /** Set whether all SSL certificates, including self-signed certificates,
     * should be trusted.
     * @param trustAll true to trust all certificates. Default false.
     */
    public void setAllSSLCertificatesTrusted(final boolean trustAll) {
        caller.setAllSSLCertificatesTrusted(trustAll);
    }
    
    /** Check if this client trusts all SSL certificates, including
     * self-signed certificates.
     * @return true if all certificates are trusted.
     */
    public boolean isAllSSLCertificatesTrusted() {
        return caller.isAllSSLCertificatesTrusted();
    }
    /** Sets streaming mode on. In this case, the data will be streamed to
     * the server in chunks as it is read from disk rather than buffered in
     * memory. Many servers are not compatible with this feature.
     * @param streamRequest true to set streaming mode on, false otherwise.
     */
    public void setStreamingModeOn(boolean streamRequest) {
        caller.setStreamingModeOn(streamRequest);
    }

    /** Returns true if streaming mode is on.
     * @return true if streaming mode is on.
     */
    public boolean isStreamingModeOn() {
        return caller.isStreamingModeOn();
    }

    public void _setFileForNextRpcResponse(File f) {
        caller.setFileForNextRpcResponse(f);
    }

    public String getServiceVersion() {
        return this.serviceVersion;
    }

    public void setServiceVersion(String newValue) {
        this.serviceVersion = newValue;
    }

    /**
     * <p>Original spec-file function name: KButil_Concat_MSAs</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.kbobjectutilities.KButilConcatMSAsParams KButilConcatMSAsParams} (original type "KButil_Concat_MSAs_Params")
     * @return   instance of type {@link us.kbase.kbobjectutilities.KButilConcatMSAsOutput KButilConcatMSAsOutput} (original type "KButil_Concat_MSAs_Output")
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public KButilConcatMSAsOutput kButilConcatMSAs(KButilConcatMSAsParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<KButilConcatMSAsOutput>> retType = new TypeReference<List<KButilConcatMSAsOutput>>() {};
        List<KButilConcatMSAsOutput> res = caller.jsonrpcCall("kb_ObjectUtilities.KButil_Concat_MSAs", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: KButil_count_ws_objects</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.kbobjectutilities.KButilCountWsObjectsParams KButilCountWsObjectsParams} (original type "KButil_count_ws_objects_Params")
     * @return   instance of type {@link us.kbase.kbobjectutilities.KButilCountWsObjectsOutput KButilCountWsObjectsOutput} (original type "KButil_count_ws_objects_Output")
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public KButilCountWsObjectsOutput kButilCountWsObjects(KButilCountWsObjectsParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<KButilCountWsObjectsOutput>> retType = new TypeReference<List<KButilCountWsObjectsOutput>>() {};
        List<KButilCountWsObjectsOutput> res = caller.jsonrpcCall("kb_ObjectUtilities.KButil_count_ws_objects", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: KButil_delete_ws_objects</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.kbobjectutilities.KButilDeleteWsObjectsParams KButilDeleteWsObjectsParams} (original type "KButil_delete_ws_objects_Params")
     * @return   instance of type {@link us.kbase.kbobjectutilities.KButilDeleteWsObjectsOutput KButilDeleteWsObjectsOutput} (original type "KButil_delete_ws_objects_Output")
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public KButilDeleteWsObjectsOutput kButilDeleteWsObjects(KButilDeleteWsObjectsParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<KButilDeleteWsObjectsOutput>> retType = new TypeReference<List<KButilDeleteWsObjectsOutput>>() {};
        List<KButilDeleteWsObjectsOutput> res = caller.jsonrpcCall("kb_ObjectUtilities.KButil_delete_ws_objects", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: KButil_update_genome_species_name</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.kbobjectutilities.KButilUpdateGenomeSpeciesNameParams KButilUpdateGenomeSpeciesNameParams} (original type "KButil_update_genome_species_name_Params")
     * @return   instance of type {@link us.kbase.kbobjectutilities.KButilUpdateGenomeSpeciesNameOutput KButilUpdateGenomeSpeciesNameOutput} (original type "KButil_update_genome_species_name_Output")
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public KButilUpdateGenomeSpeciesNameOutput kButilUpdateGenomeSpeciesName(KButilUpdateGenomeSpeciesNameParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<KButilUpdateGenomeSpeciesNameOutput>> retType = new TypeReference<List<KButilUpdateGenomeSpeciesNameOutput>>() {};
        List<KButilUpdateGenomeSpeciesNameOutput> res = caller.jsonrpcCall("kb_ObjectUtilities.KButil_update_genome_species_name", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: KButil_update_genome_fields_from_files</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.kbobjectutilities.KButilUpdateGenomeFieldsFromFilesParams KButilUpdateGenomeFieldsFromFilesParams} (original type "KButil_update_genome_fields_from_files_Params")
     * @return   instance of type {@link us.kbase.kbobjectutilities.KButilUpdateGenomeFieldsFromFilesOutput KButilUpdateGenomeFieldsFromFilesOutput} (original type "KButil_update_genome_fields_from_files_Output")
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public KButilUpdateGenomeFieldsFromFilesOutput kButilUpdateGenomeFieldsFromFiles(KButilUpdateGenomeFieldsFromFilesParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<KButilUpdateGenomeFieldsFromFilesOutput>> retType = new TypeReference<List<KButilUpdateGenomeFieldsFromFilesOutput>>() {};
        List<KButilUpdateGenomeFieldsFromFilesOutput> res = caller.jsonrpcCall("kb_ObjectUtilities.KButil_update_genome_fields_from_files", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: KButil_update_genome_features_from_file</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.kbobjectutilities.KButilUpdateGenomeFeaturesFromFileParams KButilUpdateGenomeFeaturesFromFileParams} (original type "KButil_update_genome_features_from_file_Params")
     * @return   instance of type {@link us.kbase.kbobjectutilities.KButilUpdateGenomeFeaturesFromFileOutput KButilUpdateGenomeFeaturesFromFileOutput} (original type "KButil_update_genome_features_from_file_Output")
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public KButilUpdateGenomeFeaturesFromFileOutput kButilUpdateGenomeFeaturesFromFile(KButilUpdateGenomeFeaturesFromFileParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<KButilUpdateGenomeFeaturesFromFileOutput>> retType = new TypeReference<List<KButilUpdateGenomeFeaturesFromFileOutput>>() {};
        List<KButilUpdateGenomeFeaturesFromFileOutput> res = caller.jsonrpcCall("kb_ObjectUtilities.KButil_update_genome_features_from_file", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    public Map<String, Object> status(RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        TypeReference<List<Map<String, Object>>> retType = new TypeReference<List<Map<String, Object>>>() {};
        List<Map<String, Object>> res = caller.jsonrpcCall("kb_ObjectUtilities.status", args, retType, true, false, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }
}
