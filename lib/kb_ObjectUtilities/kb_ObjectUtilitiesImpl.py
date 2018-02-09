# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
import sys
import shutil
import hashlib
import subprocess
import requests
import re
import traceback
import uuid
from datetime import datetime
from pprint import pprint, pformat
import numpy as np
import gzip
import random

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import generic_protein
#from biokbase.workspace.client import Workspace as workspaceService                                                              
from Workspace.WorkspaceClient import Workspace as workspaceService
from requests_toolbelt import MultipartEncoder  # added                                                                           
from biokbase.AbstractHandle.Client import AbstractHandle as HandleService

# SDK Utils                                                                                                                       
from ReadsUtils.ReadsUtilsClient import ReadsUtils
from SetAPI.SetAPIServiceClient import SetAPI
from KBaseReport.KBaseReportClient import KBaseReport

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
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbaseapps/kb_ObjectUtilities"
    GIT_COMMIT_HASH = "b6c791d10b6c698642d2f3de450ffd3ed10d8e98"

    #BEGIN_CLASS_HEADER
    workspaceURL = None
    shockURL = None
    handleURL = None
    serviceWizardsURL = None
    callbackURL = None
    scratch = None


    # target is a list for collecting log messages                                                                                
    def log(self, target, message):
        # we should do something better here...                                                                                   
        if target is not None:
            target.append(message)
        print(message)
        sys.stdout.flush()
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.workspaceURL = config['workspace-url']
        self.shockURL = config['shock-url']
        self.handleURL = config['handle-service-url']
        self.serviceWizardURL = config['service-wizard-url']

        #self.callbackURL = os.environ['SDK_CALLBACK_URL'] if os.environ['SDK_CALLBACK_URL'] != None else 'https://kbase.us/services/njs_wrapper'  # DEBUG                                                                                                         
        self.callbackURL = os.environ.get('SDK_CALLBACK_URL')
#        if self.callbackURL == None:                                                                                             
#            self.callbackURL = os.environ['SDK_CALLBACK_URL']                                                                    
if self.callbackURL == None:
            raise ValueError ("SDK_CALLBACK_URL not set in environment")

self.scratch = os.path.abspath(config['scratch'])
        # HACK!! temporary hack for issue where megahit fails on mac because of silent named pipe error                           
        #self.host_scratch = self.scratch                                                                                         
        #self.scratch = os.path.join('/kb','module','local_scratch')                                                              
        # end hack                                                                                                                
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
                ws = workspaceService(self.workspaceURL, token=ctx['token'])
                #objects = ws.get_objects([{'ref': MSA_ref}])
                objects = ws.get_objects2({'objects':[{'ref': MSA_ref}]})['data']
                data = objects[0]['data']
                info = objects[0]['info']
                # Object Info Contents
                # absolute ref = info[6] + '/' + info[0] + '/' + info[4]
                # 0 - obj_id objid
                # 1 - obj_name name
                # 2 - type_string type
                # 3 - timestamp save_date
                # 4 - int version
                # 5 - username saved_by
                # 6 - ws_id wsid
                # 7 - ws_name workspace
                # 8 - string chsum
                # 9 - int size 
                # 10 - usermeta meta
                type_name = info[2].split('.')[1].split('-')[0]

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


        # load the method provenance from the context object
        #
        self.log(console,"SETTING PROVENANCE")  # DEBUG
        provenance = [{}]
        if 'provenance' in ctx:
            provenance = ctx['provenance']
        # add additional info to provenance here, in this case the input data object reference
        provenance[0]['input_ws_objects'] = []
        for MSA_ref in params['input_refs']:
            provenance[0]['input_ws_objects'].append(MSA_ref)
        provenance[0]['service'] = 'kb_ObjectUtilities'
        provenance[0]['method'] = 'KButil_Concat_MSAs'


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

                new_obj_info = ws.save_objects({
                            'workspace': params['workspace_name'],
                            'objects':[{
                                    'type': 'KBaseTrees.MSA',
                                    'data': output_MSA,
                                    'name': params['output_name'],
                                    'meta': {},
                                    'provenance': provenance
                                }]
                        })


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

        reportName = 'kb_ObjectUtilities_concat_msas_report_'+str(uuid.uuid4())
        ws = workspaceService(self.workspaceURL, token=ctx['token'])
        report_obj_info = ws.save_objects({
#                'id':info[6],
                'workspace':params['workspace_name'],
                'objects':[
                    {
                        'type':'KBaseReport.Report',
                        'data':reportObj,
                        'name':reportName,
                        'meta':{},
                        'hidden':1,
                        'provenance':provenance
                    }
                ]
            })[0]


        # Build report and return
        #
        self.log(console,"BUILDING RETURN OBJECT")
        returnVal = { 'report_name': reportName,
                      'report_ref': str(report_obj_info[6]) + '/' + str(report_obj_info[0]) + '/' + str(report_obj_info[4]),
                      }
        self.log(console,"KButil_Concat_MSAs DONE")
        #END KButil_Concat_MSAs

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method KButil_Concat_MSAs return value ' +
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
