/*
** A KBase module: kb_ObjectUtilities
**
** This module contains basic utility Apps for manipulating objects (other than Reads and Sets, which are found in kb_ReadsUtilities and kb_SetUtilities)
*/

module kb_util_dylan {

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

};

