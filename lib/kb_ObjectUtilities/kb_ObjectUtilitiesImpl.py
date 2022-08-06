# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
import sys
import shutil
import hashlib
import subprocess
import requests
import re
import json
import traceback
import uuid
from datetime import datetime
from pprint import pprint, pformat
import numpy as np
import gzip
import random

from installed_clients.WorkspaceClient import Workspace as workspaceService
from installed_clients.DataFileUtilClient import DataFileUtil


# SDK Utils
#from installed_clients.SetAPIServiceClient import SetAPI
from installed_clients.KBaseReportClient import KBaseReport

# silence whining
import requests
requests.packages.urllib3.disable_warnings()
#END_HEADER


class kb_ObjectUtilities:
    '''
    Module Name:
    kb_ObjectUtilities

    Module Description:
    ** A KBase module: kb_ObjectUtilities
**
** This module contains basic utility Apps for manipulating objects (other than Reads and Sets, which are found in kb_ReadsUtilities and kb_SetUtilities)
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "1.1.0"
    GIT_URL = "https://github.com/kbaseapps/kb_ObjectUtilities"
    GIT_COMMIT_HASH = "a7cc8a3c3230b3ceab0f1270e62b9868b00124be"

    #BEGIN_CLASS_HEADER
    workspaceURL = None
    shockURL = None
    handleURL = None
    serviceWizardsURL = None
    callbackURL = None
    scratch = None

    def now_ISO(self):
        now_timestamp = datetime.now()
        now_secs_from_epoch = (now_timestamp - datetime(1970,1,1)).total_seconds()
        now_timestamp_in_iso = datetime.fromtimestamp(int(now_secs_from_epoch)).strftime('%Y-%m-%d_%T')
        return now_timestamp_in_iso

    def log(self, target, message):
        message = '['+self.now_ISO()+'] '+message
        if target is not None:
            target.append(message)
        print(message)
        sys.stdout.flush()

    def getUPA_fromInfo (self,obj_info):
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        return '/'.join([str(obj_info[WSID_I]),
                         str(obj_info[OBJID_I]),
                         str(obj_info[VERSION_I])])

    def gaAPI_get_all_AMA_features(self, features_handle_ref):
        output_dir = os.path.join(self.scratch, 'output_'+self.now_ISO())
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        json_features_file_path = os.path.join (output_dir, features_handle_ref+".json")
        if (not os.path.exists(json_features_file_path) \
            or os.path.getsize(json_features_file_path) == 0):
            try:
                self.dfuClient.shock_to_file({'handle_id': features_handle_ref,
                                              'file_path': json_features_file_path+'.gz',
                                              'unpack': 'uncompress'
                })
            except Exception as e:
                raise ValueError('Unable to fetch AnnotatedMetagenomeAssembly features from SHOCK: ' + str(e))                    

        # read file into json structure
        with open(json_features_file_path, 'r') as f:
            features_json = json.load(f)
        return features_json

    def gaAPI_save_AMA_features(self, obj_name, features):
        features_handle_ref = None
        output_dir = os.path.join(self.scratch, 'output_'+self.now_ISO())
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        features_path = os.path.join(output_dir, obj_name+'.features')
        with open(features_path, 'w') as features_h:
            json.dump(features, features_h)
        
        features_save_info = self.dfuClient.file_to_shock({'file_path': features_path,
                                                           'make_handle': 1,
                                                           'pack': 'gzip'})

        print ("FEATURES_SAVE_INFO:")
        print (pformat(features_save_info))
        features_handle_ref = features_save_info['handle']['hid']
        return features_handle_ref
    
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.token = os.environ['KB_AUTH_TOKEN']
        self.workspaceURL = config['workspace-url']
        self.shockURL = config['shock-url']
        self.handleURL = config['handle-service-url']
        self.serviceWizardURL = config['service-wizard-url']
        self.callbackURL = os.environ.get('SDK_CALLBACK_URL')
        if self.callbackURL == None:
            raise ValueError ("SDK_CALLBACK_URL not set in environment")

        self.SERVICE_VER = 'release'
        try:
            self.wsClient = workspaceService(self.workspaceURL, token=self.token)
        except:
            raise ValueError ("unable to connect to workspace client")
        try:
            self.dfuClient = DataFileUtil(url=self.callbackURL, token=self.token, service_ver=self.SERVICE_VER)
        except:
            raise ValueError ("unable to connect to DataFileUtil client")
        try:
            self.reportClient = KBaseReport(url=self.callbackURL, token=self.token, service_ver=self.SERVICE_VER)
        except:
            raise ValueError ("unable to connect to KBaseReport client")

        self.scratch = os.path.abspath(config['scratch'])
        if not os.path.exists(self.scratch):
            os.makedirs(self.scratch)
        #END_CONSTRUCTOR
        pass


    def KButil_Concat_MSAs(self, ctx, params):
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
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN KButil_Concat_MSAs
        console = []
        invalid_msgs = []
        self.log(console,'Running KButil_Concat_MSAs with params=')
        self.log(console, "\n"+pformat(params))
        report = ''
#        report = 'Running KButil_Concat_MSAs with params='
#        report += "\n"+pformat(params)
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple

        
        #### do some basic checks
        #
        if 'workspace_name' not in params:
            raise ValueError('workspace_name parameter is required')
        if 'desc' not in params:
            raise ValueError('desc parameter is required')
        if 'input_refs' not in params:
            raise ValueError('input_refs parameter is required')
        if 'output_name' not in params:
            raise ValueError('output_name parameter is required')

        # get ws_id
        ws_id = self.dfuClient.ws_name_to_id(params['workspace_name'])

        # clean input_refs
        clean_input_refs = []
        for ref in params['input_refs']:
            if ref != None and ref != '':
                clean_input_refs.append(ref)
        params['input_refs'] = clean_input_refs
            
        if len(params['input_refs']) < 2:
            self.log(console,"Must provide at least two MSAs")
            self.log(invalid_msgs,"Must provide at least two MSAs")


        # Build FeatureSet
        #
        row_order = []
        alignment = {}
        curr_pos = 0
        MSA_seen = {}
        discard_set = {}
        sequence_type = None
        for MSA_i,MSA_ref in enumerate(params['input_refs']):
            if len(params['input_refs']) < 2:  # too lazy to reindent the block
                continue

            if not MSA_ref in MSA_seen.keys():
                MSA_seen[MSA_ref] = True
            else:
                self.log(console,"repeat MSA_ref: '"+MSA_ref+"'")
                self.log(invalid_msgs,"repeat MSA_ref: '"+MSA_ref+"'")
                continue

            try:
                objects = self.dfuClient.get_objects({'object_refs':[MSA_ref]})['data']
                data = objects[0]['data']
                info = objects[0]['info']
                type_name = info[TYPE_I].split('.')[1].split('-')[0]

            except Exception as e:
                raise ValueError('Unable to fetch input_ref object from workspace: ' + str(e))
                #to get the full stack trace: traceback.format_exc()

            if type_name != 'MSA':
                raise ValueError("Bad Type:  Should be MSA instead of '"+type_name+"'")

            this_MSA = data
            this_genomes_seen = {}

            # set sequence_type
            try:
                this_sequence_type = this_MSA['sequence_type']
                if sequence_type == None:
                    sequence_type = this_sequence_type
                elif this_sequence_type != sequence_type:
                    self.log(invalid_msgs,"inconsistent sequence type for MSA "+MSA_ref+" '"+this_sequence_type+"' doesn't match '"+sequence_type+"'")
                    continue
            except:
                pass

            # build row_order
            this_row_order = []
            if 'row_order' in this_MSA.keys():
                #self.log(console,"IN row_order A")  # DEBUG
                this_row_order = this_MSA['row_order']
            else:
                #self.log(console,"IN row_order B")  # DEBUG
                this_row_order = sorted(this_MSA['alignment'].keys())

            # DEBUG
            #for row_id in this_row_order:
            #    self.log(console,"ROW_ORDER_ID: '"+row_id+"'")
            #for row_id in sorted(this_MSA['alignment']):
            #    self.log(console,"ALIGNMENT_ID: '"+row_id+"'")


            # concat alignments using base genome_id to unify (input rows are probably gene ids)
            this_aln_len = len(this_MSA['alignment'][this_row_order[0]])
            genome_row_ids_updated = {}
            for row_id in this_row_order:
                id_pieces = re.split('\.', row_id)
                if len(id_pieces) >= 2:
                    genome_id = ".".join(id_pieces[0:2])  # just want genome_id
                else:
                    genome_id = row_id

                # can't have repeat genome_ids (i.e. no paralogs allowed)
                try:
                    genome_id_seen = this_genomes_seen[genome_id]
                    self.log(console,"only one feature per genome permitted in a given MSA.  MSA: "+MSA_ref+" genome_id: "+genome_id+" row_id: "+row_id)
                    self.log(invalid_msgs,"only one feature per genome permitted in a given MSA.  MSA: "+MSA_ref+" genome_id: "+genome_id+" row_id: "+row_id)
                    continue
                except:
                    this_genomes_seen[genome_id] = True

                this_row_len = len(this_MSA['alignment'][row_id])
                if this_row_len != this_aln_len:
                    self.log(invalid_msgs,"inconsistent alignment len in "+MSA_ref+": first_row_len="+str(this_aln_len)+" != "+str(this_row_len)+" ("+row_id+")")
                    continue

                # create new rows
                if genome_id not in alignment.keys():
                    row_order.append(genome_id)
                    alignment[genome_id] = ''
                    if MSA_i > 0:
                        #self.log(console,"NOT IN OLD MSA: "+genome_id)  # DEBUG
                        discard_set[genome_id] = True
                        alignment[genome_id] += ''.join(['-' for s in range(curr_pos)])
                #else:  # DEBUG
                    #self.log(console,"SEEN IN MSA: "+genome_id)  # DEBUG

                # add new 
                genome_row_ids_updated[genome_id] = True
                alignment[genome_id] += this_MSA['alignment'][row_id]

            # append blanks for rows that weren't in new MSA
            if MSA_i > 0:
                for genome_id in alignment.keys():
                    try:
                        updated = genome_row_ids_updated[genome_id]
                    except:
                        #self.log(console,"NOT IN NEW MSA: "+genome_id)  # DEBUG
                        discard_set[genome_id] = True
                        alignment[genome_id] += ''.join(['-' for s in range(this_aln_len)])
            # update curr_pos
            curr_pos += this_aln_len
            
            # report
            if len(invalid_msgs) == 0:
                report += 'num rows in input set '+MSA_ref+': '+str(len(this_row_order))+" "+str(this_row_order)+"\n"
                self.log(console,'num rows in input set '+MSA_ref+': '+str(len(this_row_order)))
                self.log(console,'row_ids in input set '+MSA_ref+': '+str(this_row_order))

        # report which are incomplete rows (regardless of whether discarding)
        if len(invalid_msgs) == 0:
            for genome_id in row_order:
                try:
                    discard = discard_set[genome_id]
                    self.log(console,'incomplete row: '+genome_id)
                    report += 'incomplete row: '+genome_id+"\n"
                except:
                    self.log(console,'complete row: '+genome_id)
                    report += 'complete row: '+genome_id+"\n"
        

            # remove incomplete rows if not adding blanks
            if 'blanks_flag' in params and params['blanks_flag'] != None and params['blanks_flag'] == 0:
                new_row_order = []
                new_alignment = {}
                for genome_id in row_order:
                    try:
                        discard = discard_set[genome_id]
                        self.log(console,'discarding row: '+genome_id+"\n")
                        report += 'discarding row: '+genome_id
                    except:
                        new_row_order.append(genome_id)
                        new_alignment[genome_id] = alignment[genome_id]
                    row_order = new_row_order
                    alignment = new_alignment

            # report which rows are retained
            for genome_id in row_order:
                self.log(console,'output MSA contains row: '+genome_id)
                report += 'output MSA contains row: '+genome_id+"\n"


        # DEBUG: check alignment and row_order
        #for genome_id in row_order:
        #    self.log(console,"AFTER ROW_ORDER: "+genome_id)
        #for genome_id in alignment.keys():
        #    self.log(console,"AFTER ALIGNMENT: "+genome_id+",\t"+alignment[genome_id])


        # Store output object
        #
        if len(invalid_msgs) == 0:
            self.log(console,"SAVING OUTPUT MSA")  # DEBUG
            output_MSA = {
                       'name': params['output_name'],
                       'description': params['desc'],
                       'row_order': row_order,
                       'alignment': alignment,
                       'alignment_length': len(alignment[row_order[0]])
                     }
            if sequence_type != None:
                output_MSA['sequence_type'] = sequence_type

            new_obj_info = self.dfuClient.save_objects({
                'id': ws_id,
                'objects':[{
                    'type': 'KBaseTrees.MSA',
                    'data': output_MSA,
                    'name': params['output_name'],
                    'meta': {},
                    'extra_provenance_input_refs': params['input_refs']
                }]
            })[0]

                
        # build output report object
        #
        self.log(console,"BUILDING REPORT")  # DEBUG
        if len(invalid_msgs) == 0:
            self.log(console,"rows in output MSA "+params['output_name']+": "+str(len(row_order)))
            report += 'rows in output MSA '+params['output_name']+': '+str(len(row_order))+"\n"
            reportObj = {
                'objects_created':[{'ref':params['workspace_name']+'/'+params['output_name'], 'description':'KButil_Concat_MSAs'}],
                'text_message':report
                }
        else:
            report += "FAILURE:\n\n"+"\n".join(invalid_msgs)+"\n"
            reportObj = {
                'objects_created':[],
                'text_message':report
                }

        report_info = self.reportClient.create({
            'workspace_name':params['workspace_name'],
            'report': reportObj
        })

        # Return report
        returnVal = { 'report_name': report_info['name'],
                      'report_ref': report_info['ref']
        }
        self.log(console,"KButil_Concat_MSAs DONE")
        #END KButil_Concat_MSAs

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method KButil_Concat_MSAs return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def KButil_count_ws_objects(self, ctx, params):
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
           parameter "object_types" of list of String, parameter "verbose" of
           type "bool"
        :returns: instance of type "KButil_count_ws_objects_Output" ->
           structure: parameter "report_name" of type "data_obj_name",
           parameter "report_ref" of type "data_obj_ref", parameter
           "ws_obj_refs" of mapping from String to list of type "data_obj_ref"
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN KButil_count_ws_objects
        console = []
        invalid_msgs = []
        updated_object_refs = []
        self.log(console,'Running KButil_count_ws_objects')
        self.log(console, "\n"+pformat(params))
        report = ''
        #report = 'Running KButil_count_ws_objects params='
        #report += "\n"+pformat(params)
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple

        
        #### do some basic checks
        #
        required_params = ['workspace_name', 'object_types']
        for req_param in required_params:
            if not params.get(req_param):
                raise ValueError('{} parameter is required'.format(req_param))

        # get ws_id
        ws_id = self.dfuClient.ws_name_to_id(params['workspace_name'])

        # read objects in workspace (OBJID limit is chunk_size*top_iter)
        chunk_size = 2000
        top_iter = 1000
        ws_obj_refs = dict()
        for obj_type in params['object_types']:
            ws_obj_refs[obj_type] = []
            total_objs = 0
            obj_name_to_ref = dict()
            for chunk_i in range(0,top_iter):
                minObjectID = chunk_i * chunk_size
                maxObjectID = (chunk_i+1) * chunk_size - 1
    
                obj_info_list = self.wsClient.list_objects({
                    'ids':[ws_id],
                    'type':obj_type,
                    'minObjectID': minObjectID,
                    'maxObjectID': maxObjectID
                })
                num_objs = len(obj_info_list)
                if num_objs < 1:
                    break
                print ("obj_type: {} num objs: {}".format(obj_type, num_objs))
                # DEBUG to specify version
                """
                new_obj_info_list = []
                #target_version = 1
                target_version = 2
                for obj_info in obj_info_list:
                    if int(obj_info[VERSION_I]) == target_version:
                        new_obj_info_list.append(obj_info)
                obj_info_list = new_obj_info_list
                num_objs = len(obj_info_list)
                """
                # END DEBUG
                total_objs += num_objs

                for obj_info in obj_info_list:
                    obj_name_to_ref[obj_info[NAME_I]] = self.getUPA_fromInfo(obj_info)
            # log and store
            self.log(console, "OBJ_TYPE: {}".format(obj_type))
            for obj_name in sorted(obj_name_to_ref.keys()):
                if int(params.get('verbose','0')) == 1:
                    self.log(console,"{} -> {}".format(obj_name, obj_name_to_ref[obj_name]))
                ws_obj_refs[obj_type].append(obj_name_to_ref[obj_name])
            msg = "OBJ_TYPE: {} TOTAL OBJS: {}\n".format(obj_type,total_objs)
            report += msg
            self.log(console, msg)

            
        # Delete extra assemblies
        """
        for ass_obj_name in ['GCF_000632025.1', 'GCF_003013395.1', 'GCF_900102145.1']:
            full_ass_obj_name = 'GTDB_Bac-'+ass_obj_name+"__.assembly"
            if full_ass_obj_name not in obj_name_to_ref:
                raise ValueError ("missing {}".format(full_ass_obj_name))
            ass_ref = obj_name_to_ref[full_ass_obj_name]
            print ("DELETING {} -> {}".format(full_ass_obj_name, ass_ref))
            self.wsClient.delete_objects([{'ref':ass_ref}])
        """

        # create report
        report_info = self.reportClient.create({
            'workspace_name':params['workspace_name'],
            'report': {
                'objects_created':[],
                'text_message':report
            }
        })
                
        # Return report and updated_object_refs
        returnVal = { 'report_name': report_info['name'],
                      'report_ref': report_info['ref'],
                      'ws_obj_refs': ws_obj_refs
        }
        #END KButil_count_ws_objects

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method KButil_count_ws_objects return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def KButil_update_genome_species_name(self, ctx, params):
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
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN KButil_update_genome_species_name
        console = []
        invalid_msgs = []
        self.log(console,'Running KButil_update_genome_species_name with params=')
        self.log(console, "\n"+pformat(params))
        report = ''
        #report = 'Running KButil_update_genome_species_name with params='
        #report += "\n"+pformat(params)
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple

        
        #### do some basic checks
        #
        if not params.get('workspace_name'):
            raise ValueError('workspace_name parameter is required')
        if not params.get('input_refs'):
            raise ValueError('input_refs parameter is required')
        if not params.get('species_names'):
            raise ValueError('species_names parameter is required')

        # get ws_id
        ws_id = self.dfuClient.ws_name_to_id(params['workspace_name'])
        
        # clean input_refs
        clean_input_refs = []
        for ref in params['input_refs']:
            if ref != None and ref != '':
                clean_input_refs.append(ref)
        params['input_refs'] = clean_input_refs

        # new species names
        species_names = params['species_names'].split(',')
        if len(species_names) == 1:
            species_names = params['species_names'].split("\n")
        if len(species_names) != len(params['input_refs']):
            raise ValueError ("unequal number of input genomes and new species names.  num genomes: {}, num new species names: {}.  Exiting.".format(len(species_names),len(params['input_refs'])))

        # iterate through genomes
        objects_created = []
        updated_object_refs = []
        for genome_i,input_ref in enumerate(params['input_refs']):
            new_species_name = species_names[genome_i].strip()
            if new_species_name.startswith('"') and new_species_name.endswith('"'):
                new_species_name.strip('"')

            this_genome_obj = self.dfuClient.get_objects({'object_refs':[input_ref]})['data'][0]
            this_genome_info = this_genome_obj['info']
            this_genome_data = this_genome_obj['data']

            this_genome_data['scientific_name'] = new_species_name
            
            self.log(console,"{} saving genome {} ".format(genome_i+1,this_genome_info[NAME_I]))

            new_obj_info = self.dfuClient.save_objects({
                'id': ws_id,
                'objects':[{
                    'type': 'KBaseGenomes.Genome',
                    'data': this_genome_data,
                    'name': this_genome_info[NAME_I],
                    'meta': {},
                }]
            })[0]

            this_ref = self.getUPA_fromInfo(new_obj_info)
            updated_object_refs.append(this_ref)
            objects_created.append({'ref': this_ref,
                                    'description': new_species_name})
                
        # build output report object
        #
        self.log(console,"BUILDING REPORT")  # DEBUG
        if len(invalid_msgs) == 0:
            report += "num genomes processed: {}".format(len(updated_object_refs))
            reportObj = {
                'objects_created':objects_created,
                'text_message':report
                }
        else:
            report += "FAILURE:\n\n"+"\n".join(invalid_msgs)+"\n"
            reportObj = {
                'objects_created':[],
                'text_message':report
                }
        report_info = self.reportClient.create({
            'workspace_name':params['workspace_name'],
            'report': reportObj
        })

        # Return report and updated_object_refs
        returnVal = { 'report_name': report_info['name'],
                      'report_ref': report_info['ref'],
                      'updated_object_refs': updated_object_refs
        }
        self.log(console,"KButil_update_genome_species_name DONE")
        #END KButil_update_genome_species_name

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method KButil_update_genome_species_name return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def KButil_update_genome_fields_from_files(self, ctx, params):
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
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN KButil_update_genome_fields_from_files
        console = []
        invalid_msgs = []
        updated_object_refs = []
        self.log(console,'Running KButil_update_gemome_fields_from_files with params=')
        self.log(console, "\n"+pformat(params))
        report = ''
        #report = 'Running KButil_update_genome_species_name with params='
        #report += "\n"+pformat(params)
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple

        
        #### do some basic checks
        #
        required_params = ['workspace_name', 'target_list_file']
        at_least_one_params = ['object_newname_file',
                               'species_name_file',
                               'source_file',
                               'domain_file',
                               'genome_type_file',
                               'release_file',
                               'taxonomy_hierarchy_file',
                               'taxonomy_ncbi_id_file',
                               'genome_qual_scores_file',
                               #'gene_functions_file'
                              ]
        for req_param in required_params:
            if not params.get(req_param):
                raise ValueError('{} parameter is required'.format(req_param))
        at_least_one_found = False
        for optional_param in at_least_one_params:
            if params.get(optional_param):
                at_least_one_found = True
        if not at_least_one_found:
            raise ValueError('at least one of {} parameter is required'.format(",".join(at_least_one_param)))


        # read targets and new vals
        targets = dict()
        with open (params['target_list_file'], 'r') as targets_h:
            for targets_line in targets_h:
                genome_id = targets_line.rstrip()
                targets[genome_id] = True

        map_files = {
            'obj_name': params.get('object_newname_file'),
            'species_name': params.get('species_name_file'),
            'source': params.get('source_file'),
            'domain': params.get('domain_file'),
            'genome_type': params.get('genome_type_file'),
            'release': params.get('release_file'),
            'tax_hierarchy': params.get('taxonomy_hierarchy_file'),
            'ncbi_tax_id': params.get('taxonomy_ncbi_id_file'),
            'genome_qual_scores': params.get('genome_qual_scores_file')
            #'gene_functions': params.get('gene_functions_file')
        }

        maps = dict()
        for map_type in map_files.keys():
            if map_files[map_type]:
                maps[map_type] = dict()
                with open (map_files[map_type], 'r') as map_h:
                    for map_line in map_h:
                        map_line = map_line.rstrip()
                        [genome_id, field_val] = map_line.split("\t")
                        if targets.get(genome_id):
                            maps[map_type][genome_id] = field_val        
                        
        # get ws_id
        ws_id = self.dfuClient.ws_name_to_id(params['workspace_name'])

        # read genome objects in workspace
        chunk_size = 2000
        total_genomes = 0
        genome_id_to_ref = dict()
        genome_id_to_oldname = dict()
        for chunk_i in range(0,1000):
            minObjectID = chunk_i * chunk_size
            maxObjectID = (chunk_i+1) * chunk_size - 1
    
            genome_info_list = self.wsClient.list_objects({'ids':[ws_id],
                                    #'type':'KBaseGenomeAnnotations.Assembly', 
                                                'type':'KBaseGenomes.Genome', 
                                                'minObjectID': minObjectID,
                                                'maxObjectID': maxObjectID
            })
            num_genomes = len(genome_info_list)
            if num_genomes < 1:
                break
            print ("num genomes: {}".format(num_genomes))
            total_genomes += num_genomes

            for genome_info in genome_info_list:
                obj_name = genome_info[NAME_I]
                obj_ref = self.getUPA_fromInfo(genome_info)
                genome_id = re.sub('.Genome$', '', obj_name, flags=re.IGNORECASE)
                genome_id = re.sub('__$', '', genome_id)
                genome_id = re.sub('^GTDB_Arc-', '', genome_id, flags=re.IGNORECASE)
                genome_id = re.sub('^GTDB_Bac-', '', genome_id, flags=re.IGNORECASE)
                genome_id = re.sub(r'^(GC[AF]_\d{9}\.\d).*$', r'\1', genome_id)
                
                if targets.get(genome_id):
                    genome_id_to_ref[genome_id] = obj_ref
                    genome_id_to_oldname[genome_id] = obj_name
                

        # adjust target genome objects
        genome_cnt = 0
        for genome_id in sorted(genome_id_to_ref.keys()):
            genome_cnt += 1
            genome_ref = genome_id_to_ref[genome_id]
            genome_oldname = genome_id_to_oldname[genome_id]

            self.log(console, "")
            self.log(console, "===================================================")
            self.log(console, "GETTING genome {} genome ID {}".format(genome_cnt, genome_id))
            self.log(console, "===================================================\n")
            genome_obj = self.dfuClient.get_objects({'object_refs':[genome_ref]})['data'][0]
            genome_info = genome_obj['info']
            genome_data = genome_obj['data']

            # species name
            if maps.get('species_name'):
                genome_data['scientific_name'] = maps['species_name'][genome_id]
            # source
            if maps.get('source'):
                genome_data['source'] = maps['source'][genome_id]

            # domain
            if maps.get('domain'):
                genome_data['domain'] = maps['domain'][genome_id]

            # genome_type
            if maps.get('genome_type'):
                genome_data['genome_type'] = maps['genome_type'][genome_id]

            # release
            if maps.get('release'):
                genome_data['release'] = maps['release'][genome_id]

            # taxonomy
            if maps.get('tax_hierarchy'):
                genome_data['taxonomy'] = maps['tax_hierarchy'][genome_id]
                if not genome_data.get('taxon_assignments'):
                    genome_data['taxon_assignments'] = dict()
                genome_data['taxon_assignments']['gtdb_r207'] = maps['tax_hierarchy'][genome_id]

            # ncbi tax id
            if maps.get('ncbi_tax_id'):
                if not genome_data.get('taxon_assignments'):
                    genome_data['taxon_assignments'] = dict()
                genome_data['taxon_assignments']['ncbi'] = maps['ncbi_tax_id'][genome_id]
                
            # genome qual scores
            if maps.get('genome_qual_scores'):
                if not genome_data.get('quality_scores'):
                    genome_data['quality_scores'] = []
                for score_group in maps['genome_qual_scores'][genome_id].split(';'):
                    score_dict = {}
                    for score_kv in score_group.split(','):
                        [key, val] = score_kv.split('=')
                        score_dict[key] = val
                    genome_data['quality_scores'].append(score_dict)

            # keep spoofed mRNAs
            if not params.get('keep_spoofed_mRNAs'):
                if genome_data.get('mrnas'):
                    print ("genome_id: {} had an 'mrnas' substruct of length: {}".format(genome_id, len(genome_data['mrnas'])))
                    genome_data.pop('mrnas')
                else:
                    print ("genome_id: {} doesn't have an 'mrnas' substruct".format(genome_id))
                
            
            #if maps.get('gene_functions'):

            # obj_name
            if maps.get('obj_name') and genome_oldname != maps['obj_name'][genome_id]:
                obj_name = maps['obj_name'][genome_id]
                self.wsClient.rename_object({'obj':{'ref':genome_ref}, 'new_name':obj_name})
            else:
                obj_name = genome_oldname

            self.log(console, "")
            self.log(console, "===================================================")
            self.log(console, "SAVING genome {} genome ID {}".format(genome_cnt, genome_id))
            self.log(console, "===================================================\n")
            new_info = self.dfuClient.save_objects({'id': ws_id,
                                                    'objects': [
                                                        {'type': 'KBaseGenomes.Genome',
                                                         'name': obj_name,
                                                         'data': genome_data
                                                        }]
                                                   })[0]
            new_ref = self.getUPA_fromInfo(new_info)
            updated_object_refs.append(new_ref)
            
            
        # Return report and updated_object_refs
        returnVal = { 'updated_object_refs': updated_object_refs }
        self.log(console,"KButil_update_genome_fields_from_files DONE")
        #END KButil_update_genome_fields_from_files

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method KButil_update_genome_fields_from_files return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def KButil_update_genome_features_from_file(self, ctx, params):
        """
        :param params: instance of type
           "KButil_update_genome_features_from_file_Params"
           (KButil_update_genome_features_from_file() ** **  Method for
           adding values to Genome object features, from file) -> structure:
           parameter "feature_update_file" of type "file_path", parameter
           "test_genome_ref_map" of mapping from String to String
        :returns: instance of type
           "KButil_update_genome_features_from_file_Output" -> structure:
           parameter "updated_object_refs" of list of type "data_obj_ref"
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN KButil_update_genome_features_from_file
        console = []
        invalid_msgs = []
        updated_object_refs = []
        self.log(console,'Running KButil_update_gemome_fields_from_files with params=')
        self.log(console, "\n"+pformat(params))
        report = ''
        #report = 'Running KButil_update_genome_species_name with params='
        #report += "\n"+pformat(params)
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple

        
        #### do some basic checks
        #
        required_params = ['feature_update_file']
        for req_param in required_params:
            if not params.get(req_param):
                raise ValueError('{} parameter is required'.format(req_param))

        test_genome_ref_map = None
        if params.get('test_genome_ref_map'):
            test_genome_ref_map = params['test_genome_ref_map']
            
        # read targets and new vals
        targets = dict()
        features_update = dict()
        with open (params['feature_update_file'], 'r') as features_h:
            for features_line in features_h:
                [genome_id, fid, aliases_str, functions_str] = features_line.split("\t")

                if test_genome_ref_map and genome_id in test_genome_ref_map:
                    genome_id = test_genome_ref_map[genome_id]
                targets[genome_id] = True
                if len(genome_id.split('/')) != 3:
                    raise ValueError ("need to add genome_id to genome_ref_mapping")
                else:
                    genome_ref = genome_id
                
                if genome_ref not in features_update:
                    features_update[genome_ref] = dict()
                if fid not in features_update[genome_ref]:
                    features_update[genome_ref][fid] = dict()

                aliases_str = aliases_str.replace('"aliases":', '', 1)
                functions_str = functions_str.replace('"functions":', '', 1)
                features_update[genome_ref][fid]['aliases'] = json.loads(aliases_str)
                features_update[genome_ref][fid]['functions'] = json.loads(functions_str)
                
        # adjust target genome objects
        genome_cnt = 0
        updated_object_refs = []
        for genome_ref in sorted(targets.keys()):
            genome_cnt += 1

            genome_ref_noVER = '/'.join(genome_ref.split('/')[0:2])
            
            self.log(console, "")
            self.log(console, "===================================================")
            self.log(console, "GETTING genome {} genome ref {}".format(genome_cnt, genome_ref_noVER))
            self.log(console, "===================================================\n")

            genome_obj = self.dfuClient.get_objects({'object_refs':[genome_ref_noVER]})['data'][0]
            genome_info = genome_obj['info']
            genome_data = genome_obj['data']

            genome_ws_id = genome_ref.split('/')[0]
            genome_obj_name = genome_info[NAME_I]
            genome_obj_type = genome_info[TYPE_I].split('-')[0]

            # get original features
            if genome_obj_type == 'KBaseGenomes.Genome':
                features = genome_data['features']
            elif genome_obj_type == 'KBaseMetagenomes.AnnotatedMetagenomeAssembly':
                features_handle_ref = genome_obj['data']['features_handle_ref']
                features = self.gaAPI_get_all_AMA_features(features_handle_ref)
            else:
                raise ValueError ("obj type not supported: {} is type {}".format(genome_obj_name, genome_obj_type))

            # add updates
            new_features = []
            found_update = False
            for feature in features:
                fid = feature['id']

                # updated annotation may be on cds
                found_cds_id = None
                if 'cdss' in feature:
                    cds_ids = feature['cdss']
                    for cds_id in cds_ids:
                        if cds_id in features_update[genome_ref]:
                            found_cds_id = cds_id
                            break
                        
                if found_cds_id or fid in features_update[genome_ref]:
                    lookup_fid = fid
                    if found_cds_id:
                        lookup_fid = found_cds_id
                    
                    # aliases
                    aliases_seen = dict()
                    new_aliases = []
                    if 'aliases' in feature:  # may not be in AMA
                        for alias_tuple in feature['aliases']:
                            alias_str = '["'+alias_tuple[0]+'","'+alias_tuple[1]+'"]'
                            if alias_str not in aliases_seen:
                                aliases_seen[alias_str] = True
                                new_aliases.append(alias_tuple)
                    if 'aliases' in features_update[genome_ref][lookup_fid]:
                        for alias_tuple in features_update[genome_ref][lookup_fid]['aliases']:
                            alias_str = '["'+alias_tuple[0]+'","'+alias_tuple[1]+'"]'
                            if alias_str not in aliases_seen:
                                found_update = True
                                aliases_seen[alias_str] = True
                                new_aliases.append(alias_tuple)
                    feature['aliases'] = new_aliases

                    # functions
                    functions_seen = dict()
                    new_functions = []
                    if 'functions' in feature:  # may not be in AMA
                        for function_str in feature['functions']:
                            if function_str not in functions_seen:
                                functions_seen[function_str] = True
                                new_functions.append(function_str)
                    if 'functions' in features_update[genome_ref][lookup_fid]:
                        for function_str in features_update[genome_ref][lookup_fid]['functions']:
                            if function_str not in functions_seen:
                                found_update = True
                                functions_seen[function_str] = True
                                new_functions.append(function_str)
                    feature['functions'] = new_functions
                new_features.append(feature)

            if not found_update:  # only save if there's new feature updates
                continue
                
            # save new features
            if genome_obj_type == 'KBaseGenomes.Genome':
                genome_data['features'] = new_features
            elif genome_obj_type == 'KBaseMetagenomes.AnnotatedMetagenomeAssembly':
                new_features_handle_ref = self.gaAPI_save_AMA_features(genome_obj_name, new_features)
                genome_obj['data']['features_handle_ref'] = new_features_handle_ref
            
            # save updated object
            self.log(console, "")
            self.log(console, "===================================================")
            self.log(console, "SAVING genome {} name {} ref {}".format(genome_cnt, genome_obj_name, genome_ref))
            self.log(console, "===================================================\n")
            new_info = self.dfuClient.save_objects({'id': genome_ws_id,
                                                    'objects': [
                                                        {'type': genome_obj_type,
                                                         'name': genome_obj_name,
                                                         'data': genome_data
                                                        }]
                                                   })[0]
            new_ref = self.getUPA_fromInfo(new_info)
            updated_object_refs.append(new_ref)
            
            
        # Return report and updated_object_refs
        returnVal = { 'updated_object_refs': updated_object_refs }
        self.log(console,"KButil_update_genome_features_from_files DONE")
        #END KButil_update_genome_features_from_file

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method KButil_update_genome_features_from_file return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
