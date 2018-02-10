import unittest
import os
import json
import time
import requests
import shutil

from os import environ
from ConfigParser import ConfigParser
from requests_toolbelt import MultipartEncoder
from pprint import pprint

from Workspace.WorkspaceClient import Workspace as workspaceService
from biokbase.AbstractHandle.Client import AbstractHandle as HandleService
from kb_ObjectUtilities.kb_ObjectUtilitiesImpl import kb_ObjectUtilities


class kb_ObjectUtilitiesTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        cls.token = token
        cls.ctx = {'token': token, 'provenance': [{'service': 'kb_ObjectUtilities',
            'method': 'please_never_use_it_in_production', 'method_params': []}],
            'authenticated': 1}
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_ObjectUtilities'):
            print(nameval[0] + '=' + nameval[1])
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        cls.shockURL = cls.cfg['shock-url']
        cls.handleURL = cls.cfg['handle-service-url']
        cls.serviceWizardURL = cls.cfg['service-wizard-url']
        cls.callbackURL = os.environ['SDK_CALLBACK_URL']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = kb_ObjectUtilities(cls.cfg)
        cls.scratch = os.path.abspath(cls.cfg['scratch'])
        if not os.path.exists(cls.scratch):
            os.makedirs(cls.scratch)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')
        if hasattr(cls, 'shock_ids'):
            for shock_id in cls.shock_ids:
                print('Deleting SHOCK node: '+str(shock_id))
                cls.delete_shock_node(shock_id)

    @classmethod
    def delete_shock_node(cls, node_id):
        header = {'Authorization': 'Oauth {0}'.format(cls.token)}
        requests.delete(cls.shockURL + '/node/' + node_id, headers=header,
                        allow_redirects=True)
        print('Deleted shock node ' + node_id)

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_kb_ObjectUtilities_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx


    # call this method to get the WS object info of a Single End Library (will
    # upload the example data if this is the first time the method is called during tests)
    def getSingleEndLibInfo(self, read_lib_basename, lib_i=0):
        if hasattr(self.__class__, 'singleEndLibInfo_list'):
            try:
                info = self.__class__.singleEndLibInfo_list[lib_i]
                name = self.__class__.singleEndLibName_list[lib_i]
                if info != None:
                    if name != read_lib_basename:
                        self.__class__.singleEndLibInfo_list[lib_i] = None
                        self.__class__.singleEndLibName_list[lib_i] = None
                    else:
                        return info
            except:
                pass

        # 1) upload files to shock
        shared_dir = "/kb/module/work/tmp"
        forward_data_file = 'data/'+read_lib_basename+'.fwd.fq'
        forward_file = os.path.join(shared_dir, os.path.basename(forward_data_file))
        shutil.copy(forward_data_file, forward_file)

        ru = ReadsUtils(os.environ['SDK_CALLBACK_URL'])
        single_end_ref = ru.upload_reads({'fwd_file': forward_file,
                                          'sequencing_tech': 'artificial reads',
                                          'wsname': self.getWsName(),
                                          'name': 'test-'+str(lib_i)+'.se.reads'})['obj_ref']

        new_obj_info = self.getWsClient().get_object_info_new({'objects': [{'ref': single_end_ref}]})[0]

        # store it
        if not hasattr(self.__class__, 'singleEndLibInfo_list'):
            self.__class__.singleEndLibInfo_list = []
            self.__class__.singleEndLibName_list = []
        for i in range(lib_i+1):
            try:
                assigned = self.__class__.singleEndLibInfo_list[i]
            except:
                self.__class__.singleEndLibInfo_list.append(None)
                self.__class__.singleEndLibName_list.append(None)

        self.__class__.singleEndLibInfo_list[lib_i] = new_obj_info
        self.__class__.singleEndLibName_list[lib_i] = read_lib_basename
        return new_obj_info


    # call this method to get the WS object info of a Paired End Library (will
    # upload the example data if this is the first time the method is called during tests)
    def getPairedEndLibInfo(self, read_lib_basename, lib_i=0):
        if hasattr(self.__class__, 'pairedEndLibInfo_list'):
            try:
                info = self.__class__.pairedEndLibInfo_list[lib_i]
                name = self.__class__.pairedEndLibName_list[lib_i]
                if info != None:
                    if name != read_lib_basename:
                        self.__class__.pairedEndLibInfo_list[lib_i] = None
                        self.__class__.pairedEndLibName_list[lib_i] = None
                    else:
                        return info
            except:
                pass

        # 1) upload files to shock
        shared_dir = "/kb/module/work/tmp"
        forward_data_file = 'data/'+read_lib_basename+'.fwd.fq'
        forward_file = os.path.join(shared_dir, os.path.basename(forward_data_file))
        shutil.copy(forward_data_file, forward_file)
        reverse_data_file = 'data/'+read_lib_basename+'.rev.fq'
        reverse_file = os.path.join(shared_dir, os.path.basename(reverse_data_file))
        shutil.copy(reverse_data_file, reverse_file)

        ru = ReadsUtils(os.environ['SDK_CALLBACK_URL'])
        paired_end_ref = ru.upload_reads({'fwd_file': forward_file, 'rev_file': reverse_file,
                                          'sequencing_tech': 'artificial reads',
                                          'interleaved': 0, 'wsname': self.getWsName(),
                                          'name': 'test-'+str(lib_i)+'.pe.reads'})['obj_ref']

        new_obj_info = self.getWsClient().get_object_info_new({'objects': [{'ref': paired_end_ref}]})[0]

        # store it
        if not hasattr(self.__class__, 'pairedEndLibInfo_list'):
            self.__class__.pairedEndLibInfo_list = []
            self.__class__.pairedEndLibName_list = []
        for i in range(lib_i+1):
            try:
                assigned = self.__class__.pairedEndLibInfo_list[i]
            except:
                self.__class__.pairedEndLibInfo_list.append(None)
                self.__class__.pairedEndLibName_list.append(None)

        self.__class__.pairedEndLibInfo_list[lib_i] = new_obj_info
        self.__class__.pairedEndLibName_list[lib_i] = read_lib_basename
        return new_obj_info


    # call this method to get the WS object info of a Single End Library Set (will
    # upload the example data if this is the first time the method is called during tests)
    def getSingleEndLib_SetInfo(self, read_libs_basename_list, refresh=False):
        if hasattr(self.__class__, 'singleEndLib_SetInfo'):
            try:
                info = self.__class__.singleEndLib_SetInfo
                if info != None:
                    if refresh:
                        self.__class__.singleEndLib_SetInfo = None
                    else:
                        return info
            except:
                pass

        # build items and save each SingleEndLib
        items = []
        for lib_i,read_lib_basename in enumerate (read_libs_basename_list):
            label    = read_lib_basename
            lib_info = self.getSingleEndLibInfo (read_lib_basename, lib_i)
            lib_ref  = str(lib_info[6])+'/'+str(lib_info[0])+'/'+str(lib_info[4])
            print ("LIB_REF["+str(lib_i)+"]: "+lib_ref+" "+read_lib_basename)  # DEBUG

            items.append({'ref': lib_ref,
                          'label': label
                          #'data_attachment': ,
                          #'info':
                         })

        # save readsset
        desc = 'test ReadsSet'
        readsSet_obj = { 'description': desc,
                         'items': items
                       }
        name = 'TEST_READSET'

        new_obj_set_info = self.wsClient.save_objects({
                        'workspace':self.getWsName(),
                        'objects':[
                            {
                                'type':'KBaseSets.ReadsSet',
                                'data':readsSet_obj,
                                'name':name,
                                'meta':{},
                                'provenance':[
                                    {
                                        'service':'kb_ObjectUtilities',
                                        'method':'test_kb_ObjectUtilities'
                                    }
                                ]
                            }]
                        })[0]

        # store it
        self.__class__.singleEndLib_SetInfo = new_obj_set_info
        return new_obj_set_info


    # call this method to get the WS object info of a Paired End Library Set (will
    # upload the example data if this is the first time the method is called during tests)
    def getPairedEndLib_SetInfo(self, read_libs_basename_list, refresh=False):
        if hasattr(self.__class__, 'pairedEndLib_SetInfo'):
            try:
                info = self.__class__.pairedEndLib_SetInfo
                if info != None:
                    if refresh:
                        self.__class__.pairedEndLib_SetInfo = None
                    else:
                        return info
            except:
                pass

        # build items and save each PairedEndLib
        items = []
        for lib_i,read_lib_basename in enumerate (read_libs_basename_list):
            label    = read_lib_basename
            lib_info = self.getPairedEndLibInfo (read_lib_basename, lib_i)
            lib_ref  = str(lib_info[6])+'/'+str(lib_info[0])+'/'+str(lib_info[4])
            lib_type = str(lib_info[2])
            print ("LIB_REF["+str(lib_i)+"]: "+lib_ref+" "+read_lib_basename)  # DEBUG
            print ("LIB_TYPE["+str(lib_i)+"]: "+lib_type+" "+read_lib_basename)  # DEBUG

            items.append({'ref': lib_ref,
                          'label': label
                          #'data_attachment': ,
                          #'info':
                         })

        # save readsset
        desc = 'test ReadsSet'
        readsSet_obj = { 'description': desc,
                         'items': items
                       }
        name = 'TEST_READSET'

        new_obj_set_info = self.wsClient.save_objects({
                        'workspace':self.getWsName(),
                        'objects':[
                            {
                                'type':'KBaseSets.ReadsSet',
                                'data':readsSet_obj,
                                'name':name,
                                'meta':{},
                                'provenance':[
                                    {
                                        'service':'kb_ObjectUtilities',
                                        'method':'test_kb_ObjectUtilities'
                                    }
                                ]
                            }]
                        })[0]

        # store it
        self.__class__.pairedEndLib_SetInfo = new_obj_set_info
        return new_obj_set_info


    ##############
    # UNIT TESTS #
    ##############


    #### test_KButil_Concat_MSAs():
    ##
    def test_KButil_Concat_MSAs (self):
        method = 'KButil_Concat_MSAs'

        print ("\n\nRUNNING: test_KButil_Concat_MSAs()")
        print ("==================================\n\n")

        # MSA
        MSA_json_file = os.path.join('data', 'DsrA.MSA.json')
        with open (MSA_json_file, 'r', 0) as MSA_json_fh:
            MSA_obj = json.load(MSA_json_fh)
        provenance = [{}]
        MSA_info_list = self.getWsClient().save_objects({
            'workspace': self.getWsName(), 
            'objects': [
                {
                    'type': 'KBaseTrees.MSA',
                    'data': MSA_obj,
                    'name': 'test_MSA_1',
                    'meta': {},
                    'provenance': provenance
                },
                {
                    'type': 'KBaseTrees.MSA',
                    'data': MSA_obj,
                    'name': 'test_MSA_2',
                    'meta': {},
                    'provenance': provenance
                },
                {
                    'type': 'KBaseTrees.MSA',
                    'data': MSA_obj,
                    'name': 'test_MSA_3',
                    'meta': {},
                    'provenance': provenance
                }
            ]})
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        MSA_ref_1 = str(MSA_info_list[0][WSID_I])+'/'+str(MSA_info_list[0][OBJID_I])+'/'+str(MSA_info_list[0][VERSION_I])
        MSA_ref_2 = str(MSA_info_list[1][WSID_I])+'/'+str(MSA_info_list[1][OBJID_I])+'/'+str(MSA_info_list[1][VERSION_I])
        MSA_ref_3 = str(MSA_info_list[2][WSID_I])+'/'+str(MSA_info_list[2][OBJID_I])+'/'+str(MSA_info_list[2][VERSION_I])

        # run method
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': [MSA_ref_1, MSA_ref_2, MSA_ref_3],
            'output_name': base_output_name,
            'desc': 'test'
        }
        result = self.getImpl().KButil_Concat_MSAs(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseTrees.MSA'
        output_ref = self.getWsName()+'/'+output_name
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
        self.assertEqual(len(info_list),1)
        output_info = info_list[0]
        self.assertEqual(output_info[1],output_name)
        self.assertEqual(output_info[2].split('-')[0],output_type)
        output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
        self.assertEqual(len(output_obj['row_order']), len(MSA_obj['row_order']))
        self.assertEqual(output_obj['alignment_length'], 3*MSA_obj['alignment_length'])
        pass
