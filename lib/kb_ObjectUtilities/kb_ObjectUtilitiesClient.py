# -*- coding: utf-8 -*-
############################################################
#
# Autogenerated by the KBase type compiler -
# any changes made here will be overwritten
#
############################################################

from __future__ import print_function
# the following is a hack to get the baseclient to import whether we're in a
# package or not. This makes pep8 unhappy hence the annotations.
try:
    # baseclient and this client are in a package
    from .baseclient import BaseClient as _BaseClient  # @UnusedImport
except ImportError:
    # no they aren't
    from baseclient import BaseClient as _BaseClient  # @Reimport


class kb_ObjectUtilities(object):

    def __init__(
            self, url=None, timeout=30 * 60, user_id=None,
            password=None, token=None, ignore_authrc=False,
            trust_all_ssl_certificates=False,
            auth_svc='https://ci.kbase.us/services/auth/api/legacy/KBase/Sessions/Login'):
        if url is None:
            raise ValueError('A url is required')
        self._service_ver = None
        self._client = _BaseClient(
            url, timeout=timeout, user_id=user_id, password=password,
            token=token, ignore_authrc=ignore_authrc,
            trust_all_ssl_certificates=trust_all_ssl_certificates,
            auth_svc=auth_svc)

    def KButil_Concat_MSAs(self, params, context=None):
        """
        :param params: instance of type "KButil_Concat_MSAs_Params"
           (KButil_Concat_MSAs() ** **  Method for Concatenating MSAs into a
           combined MSA) -> structure: parameter "workspace_name" of type
           "workspace_name" (** The workspace object refs are of form: ** ** 
           objects = ws.get_objects([{'ref':
           params['workspace_id']+'/'+params['obj_name']}]) ** ** "ref" means
           the entire name combining the workspace id and the object name **
           "id" is a numerical identifier of the workspace or object, and
           should just be used for workspace ** "name" is a string identifier
           of a workspace or object.  This is received from Narrative.),
           parameter "input_refs" of type "data_obj_ref", parameter
           "output_name" of type "data_obj_name", parameter "desc" of String,
           parameter "blanks_flag" of type "bool"
        :returns: instance of type "KButil_Concat_MSAs_Output" -> structure:
           parameter "report_name" of type "data_obj_name", parameter
           "report_ref" of type "data_obj_ref"
        """
        return self._client.call_method('kb_ObjectUtilities.KButil_Concat_MSAs',
                                        [params], self._service_ver, context)

    def KButil_count_ws_objects(self, params, context=None):
        """
        :param params: instance of type "KButil_count_ws_objects_Params"
           (KButil_count_ws_objects() ** **  Method for counting number of
           workspace objects when data panel fails) -> structure: parameter
           "workspace_name" of type "workspace_name" (** The workspace object
           refs are of form: ** **    objects = ws.get_objects([{'ref':
           params['workspace_id']+'/'+params['obj_name']}]) ** ** "ref" means
           the entire name combining the workspace id and the object name **
           "id" is a numerical identifier of the workspace or object, and
           should just be used for workspace ** "name" is a string identifier
           of a workspace or object.  This is received from Narrative.),
           parameter "object_types" of list of String
        :returns: instance of type "KButil_count_ws_objects_Output" ->
           structure: parameter "report_name" of type "data_obj_name",
           parameter "report_ref" of type "data_obj_ref", parameter
           "ws_obj_refs" of mapping from String to list of type "data_obj_ref"
        """
        return self._client.call_method('kb_ObjectUtilities.KButil_count_ws_objects',
                                        [params], self._service_ver, context)

    def KButil_update_genome_species_name(self, params, context=None):
        """
        :param params: instance of type
           "KButil_update_genome_species_name_Params"
           (KButil_update_genome_species_name() ** **  Method for
           adding/changing Genome objects species names) -> structure:
           parameter "workspace_name" of type "workspace_name" (** The
           workspace object refs are of form: ** **    objects =
           ws.get_objects([{'ref':
           params['workspace_id']+'/'+params['obj_name']}]) ** ** "ref" means
           the entire name combining the workspace id and the object name **
           "id" is a numerical identifier of the workspace or object, and
           should just be used for workspace ** "name" is a string identifier
           of a workspace or object.  This is received from Narrative.),
           parameter "input_refs" of list of type "data_obj_ref", parameter
           "species_names" of String
        :returns: instance of type "KButil_update_genome_species_name_Output"
           -> structure: parameter "report_name" of type "data_obj_name",
           parameter "report_ref" of type "data_obj_ref", parameter
           "updated_object_refs" of list of type "data_obj_ref"
        """
        return self._client.call_method('kb_ObjectUtilities.KButil_update_genome_species_name',
                                        [params], self._service_ver, context)

    def KButil_update_genome_fields_from_files(self, params, context=None):
        """
        :param params: instance of type
           "KButil_update_genome_fields_from_files_Params"
           (KButil_update_genome_fields_from_files() ** **  Method for
           adding/changing values in Genome object fields, from files) ->
           structure: parameter "workspace_name" of type "workspace_name" (**
           The workspace object refs are of form: ** **    objects =
           ws.get_objects([{'ref':
           params['workspace_id']+'/'+params['obj_name']}]) ** ** "ref" means
           the entire name combining the workspace id and the object name **
           "id" is a numerical identifier of the workspace or object, and
           should just be used for workspace ** "name" is a string identifier
           of a workspace or object.  This is received from Narrative.),
           parameter "target_list_file" of type "file_path", parameter
           "object_newname_file" of type "file_path", parameter
           "species_name_file" of type "file_path", parameter "source_file"
           of type "file_path", parameter "domain_file" of type "file_path",
           parameter "genome_type_file" of type "file_path", parameter
           "release_file" of type "file_path", parameter
           "taxonomy_hierarchy_file" of type "file_path", parameter
           "taxonomy_ncbi_id_file" of type "file_path", parameter
           "genome_qual_scores_file" of type "file_path", parameter
           "gene_functions_file" of type "file_path", parameter
           "keep_spoofed_mRNAs" of type "bool"
        :returns: instance of type
           "KButil_update_genome_fields_from_files_Output" -> structure:
           parameter "updated_object_refs" of list of type "data_obj_ref"
        """
        return self._client.call_method('kb_ObjectUtilities.KButil_update_genome_fields_from_files',
                                        [params], self._service_ver, context)

    def status(self, context=None):
        return self._client.call_method('kb_ObjectUtilities.status',
                                        [], self._service_ver, context)
