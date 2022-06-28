/*
** A KBase module: kb_ObjectUtilities
**
** This module contains basic utility Apps for manipulating objects (other than Reads and Sets, which are found in kb_ReadsUtilities and kb_SetUtilities)
*/

module kb_ObjectUtilities {

    /* 
    ** The workspace object refs are of form:
    **
    **    objects = ws.get_objects([{'ref': params['workspace_id']+'/'+params['obj_name']}])
    **
    ** "ref" means the entire name combining the workspace id and the object name
    ** "id" is a numerical identifier of the workspace or object, and should just be used for workspace
    ** "name" is a string identifier of a workspace or object.  This is received from Narrative.
    */
    typedef string workspace_name;
    typedef string file_path;
    typedef string sequence;
    typedef string data_obj_name;
    typedef string data_obj_ref;
    typedef int    bool;


    /* KButil_Concat_MSAs()
    **
    **  Method for Concatenating MSAs into a combined MSA
    */
    typedef structure {
        workspace_name workspace_name;
	data_obj_ref   input_refs;
        data_obj_name  output_name;
	string         desc;
	bool           blanks_flag;
    } KButil_Concat_MSAs_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
    } KButil_Concat_MSAs_Output;

    funcdef KButil_Concat_MSAs (KButil_Concat_MSAs_Params params)  returns (KButil_Concat_MSAs_Output) authentication required;


    /* KButil_count_ws_objects()
    **
    **  Method for counting number of workspace objects when data panel fails
    */
    typedef structure {
        workspace_name workspace_name;
	list<string>   object_types;
	bool           verbose;
    } KButil_count_ws_objects_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
	mapping<string,list<data_obj_ref>> ws_obj_refs;
    } KButil_count_ws_objects_Output;

    funcdef KButil_count_ws_objects(KButil_count_ws_objects_Params params)  returns (KButil_count_ws_objects_Output) authentication required;
    

    /* KButil_update_genome_species_name()
    **
    **  Method for adding/changing Genome objects species names
    */
    typedef structure {
        workspace_name     workspace_name;
	list<data_obj_ref> input_refs;
	string             species_names;
    } KButil_update_genome_species_name_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
	list<data_obj_ref> updated_object_refs;
    } KButil_update_genome_species_name_Output;

    funcdef KButil_update_genome_species_name(KButil_update_genome_species_name_Params params)  returns (KButil_update_genome_species_name_Output) authentication required;

    
    /* KButil_update_genome_fields_from_files()
    **
    **  Method for adding/changing values in Genome object fields, from files
    */
    typedef structure {
        workspace_name workspace_name;
	/*list<data_obj_ref>  input_refs;*/
	file_path  target_list_file;
	file_path  object_newname_file;
	file_path  species_name_file;
	file_path  source_file;
	file_path  domain_file;
	file_path  genome_type_file;
	file_path  release_file;
	file_path  taxonomy_hierarchy_file;
	file_path  taxonomy_ncbi_id_file;
	file_path  genome_qual_scores_file;
	file_path  gene_functions_file;
	bool       keep_spoofed_mRNAs;
    } KButil_update_genome_fields_from_files_Params;

    typedef structure {
	list<data_obj_ref> updated_object_refs;
    } KButil_update_genome_fields_from_files_Output;

    funcdef KButil_update_genome_fields_from_files(KButil_update_genome_fields_from_files_Params params)  returns (KButil_update_genome_fields_from_files_Output) authentication required;
    
};

