import unittest
import os
import json
import time
import requests
import shutil
import re

from os import environ
from ConfigParser import ConfigParser
from pprint import pprint

from installed_clients.WorkspaceClient import Workspace as workspaceService
from installed_clients.GenomeFileUtilClient import GenomeFileUtil
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


    def getUPA_fromInfo (self,obj_info):
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        return '/'.join([str(obj_info[WSID_I]),
                         str(obj_info[OBJID_I]),
                         str(obj_info[VERSION_I])])

    
    def getGenomeInfo(self, genome_basename, item_i=0):
        if hasattr(self.__class__, 'genomeInfo_list'):
            try:
                info = self.__class__.genomeInfo_list[item_i]
                name = self.__class__.genomeName_list[item_i]
                if info != None:
                    if name != genome_basename:
                        self.__class__.genomeInfo_list[item_i] = None
                        self.__class__.genomeName_list[item_i] = None
                    else:
                        return info
            except:
                pass

        # 1) transform genbank to kbase genome object and upload to ws
        shared_dir = "/kb/module/work/tmp"
        genome_data_file = 'data/genomes/'+genome_basename+'.gbff.gz'
        genome_file = os.path.join(shared_dir, os.path.basename(genome_data_file))
        shutil.copy(genome_data_file, genome_file)

        SERVICE_VER = 'release'
        #SERVICE_VER = 'dev'
        GFU = GenomeFileUtil(os.environ['SDK_CALLBACK_URL'],
                             token=self.getContext()['token'],
                             service_ver=SERVICE_VER
                         )
        print ("UPLOADING genome: "+genome_basename+" to WORKSPACE "+self.getWsName()+" ...")
        genome_upload_result = GFU.genbank_to_genome({'file': {'path': genome_file },
                                                      'workspace_name': self.getWsName(),
                                                      'genome_name': genome_basename
                                                  })
#                                                  })[0]
        pprint(genome_upload_result)
        genome_ref = genome_upload_result['genome_ref']
        new_obj_info = self.getWsClient().get_object_info_new({'objects': [{'ref': genome_ref}]})[0]

        # 2) store it
        if not hasattr(self.__class__, 'genomeInfo_list'):
            self.__class__.genomeInfo_list = []
            self.__class__.genomeName_list = []
        for i in range(item_i+1):
            try:
                assigned = self.__class__.genomeInfo_list[i]
            except:
                self.__class__.genomeInfo_list.append(None)
                self.__class__.genomeName_list.append(None)

        self.__class__.genomeInfo_list[item_i] = new_obj_info
        self.__class__.genomeName_list[item_i] = genome_basename
        return new_obj_info

    
    ##############
    # UNIT TESTS #
    ##############


    #### test_KButil_Concat_MSAs():
    ##
    # HIDE @unittest.skip("skipped test_KButil_Concat_MSAs")
    def test_KButil_Concat_MSAs (self):
        method = 'KButil_Concat_MSAs'

        print ("\n\nRUNNING: test_KButil_Concat_MSAs()")
        print ("==================================\n\n")

        # MSA
        MSA_json_file = os.path.join('data', 'MSAs', 'DsrA.MSA.json')
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
        MSA_ref_1 = self.getUPA_fromInfo (MSA_info_list[0])
        MSA_ref_2 = self.getUPA_fromInfo (MSA_info_list[1])
        MSA_ref_3 = self.getUPA_fromInfo (MSA_info_list[2])

        # run method
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': [MSA_ref_1, MSA_ref_2, MSA_ref_3],
            'output_name': base_output_name,
            'desc': 'test'
        }
        result = self.getImpl().KButil_Concat_MSAs(self.getContext(),params)[0]
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


    #### test_KButil_update_genome_species_name():
    ##
    # HIDE @unittest.skip("skipped test_KButil_update_genome_species_name")
    def test_KButil_update_genome_species_name (self):
        method = 'KButil_update_genome_species_names'

        print ("\n\nRUNNING: {}".format(method))
        print ("==================================\n\n")


        # upload test genomes
        genomeInfo_0 = self.getGenomeInfo('GCF_000287295.1_ASM28729v1_genomic', 0)  # Candidatus Carsonella ruddii HT isolate Thao2000
        genomeInfo_1 = self.getGenomeInfo('GCF_000306885.1_ASM30688v1_genomic', 1)  # Wolbachia endosymbiont of Onchocerca ochengi
        genomeInfo_2 = self.getGenomeInfo('GCF_001439985.1_wTPRE_1.0_genomic',  2)  # Wolbachia endosymbiont of Trichogramma pretiosum
        #genomeInfo_3 = self.getGenomeInfo('GCF_000022285.1_ASM2228v1_genomic',  3)  # Wolbachia sp. wRi

        genome_refs = [ self.getUPA_fromInfo (genomeInfo_0),
                        self.getUPA_fromInfo (genomeInfo_1),
                        self.getUPA_fromInfo (genomeInfo_2)]
        output_names = ['Carsonella rudii', 'Wolbachia endo of Oo', 'Wolbachia endo of Tp']
        
        
        # run method
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': genome_refs,
            'species_names': ",\n".join(output_names)
        }
        result = self.getImpl().KButil_update_genome_species_name(self.getContext(),params)[0]
        print('RESULT:')
        pprint(result)

        # check the output
        output_refs = result['updated_object_refs']
        for output_i,output_ref in enumerate(output_refs):
            output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
            self.assertEqual(output_obj['scientific_name'], output_names[output_i])
        pass

    
    #### test_KButil_count_ws_objects():
    ##
    # HIDE @unittest.skip("skipped test_KButil_count_ws_objects")
    def test_KButil_count_ws_objects (self):
        method = 'KButil_count_ws_objects'
        print ("\n\nRUNNING: {}".format(method))
        print ("==================================\n\n")
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple

        obj_types =  ['KBaseGenomeAnnotations.Assembly','KBaseGenomes.Genome']
        #obj_types =  ['KBaseGenomes.Genome']  # DEBUG
        expected_count = {'KBaseGenomeAnnotations.Assembly': 3,
                          'KBaseGenomes.Genome': 3
                          }

        # DEBUG
        # upload test genomes
        genomeInfo_0 = self.getGenomeInfo('GCF_000287295.1_ASM28729v1_genomic', 0)  # Candidatus Carsonella ruddii HT isolate Thao2000
        genomeInfo_1 = self.getGenomeInfo('GCF_000306885.1_ASM30688v1_genomic', 1)  # Wolbachia endosymbiont of Onchocerca ochengi
        genomeInfo_2 = self.getGenomeInfo('GCF_001439985.1_wTPRE_1.0_genomic',  2)  # Wolbachia endosymbiont of Trichogramma pretiosum
        #genomeInfo_3 = self.getGenomeInfo('GCF_000022285.1_ASM2228v1_genomic',  3)  # Wolbachia sp. wRi
        
        # run method
        params = {
            #'workspace_name': 'dylan:narrative_1653154121485',  # DEBUG
            #'workspace_name': 'dylan:narrative_1653154144334',  # DEBUG
            'workspace_name': self.getWsName(),
            'object_types': obj_types,
            'verbose': 1
        }
        result = self.getImpl().KButil_count_ws_objects(self.getContext(),params)[0]
        #print('RESULT:')
        #pprint(result)

        # DEBUG
        # check the output
        obj_refs_by_type = result['ws_obj_refs']
        for obj_type in obj_types:
            obj_refs = obj_refs_by_type[obj_type]
            print ("TESTING OBJ_TYPE: {} NUM_OBJS: {}".format(obj_type,len(obj_refs)))
            self.assertEqual(len(obj_refs),expected_count[obj_type])
            for obj_ref in obj_refs:
                obj_info = self.getWsClient().get_object_info_new({'objects': [{'ref': obj_ref}]})[0]
                self.assertEqual(obj_info[TYPE_I].split('-')[0],obj_type)
        pass

    
    #### test_KButil_update_genome_fields_from_files():
    ##
    # HIDE @unittest.skip("skipped test_KButil_update_genome_fields_from_files")
    def test_KButil_update_genome_fields_from_files (self):
        method = 'KButil_update_genome_fields_from_files'

        print ("\n\nRUNNING: {}".format(method))
        print ("==================================\n\n")

        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple


        # config
        keep_mRNAs = 0
        
        # upload test genomes
        genomeInfo_0 = self.getGenomeInfo('GCF_000287295.1_ASM28729v1_genomic', 0)  # Candidatus Carsonella ruddii HT isolate Thao2000
        genomeInfo_1 = self.getGenomeInfo('GCF_000306885.1_ASM30688v1_genomic', 1)  # Wolbachia endosymbiont of Onchocerca ochengi
        genomeInfo_2 = self.getGenomeInfo('GCF_001439985.1_wTPRE_1.0_genomic',  2)  # Wolbachia endosymbiont of Trichogramma pretiosum
        #genomeInfo_3 = self.getGenomeInfo('GCF_000022285.1_ASM2228v1_genomic',  3)  # Wolbachia sp. wRi

        # copy mapping files to shared mount
        shared_dir = "/kb/module/work/tmp"
        map_files = {
            'target_list': 'targets.list',
            'obj_name': 'obj_name.map',
            'species_name': 'species_name.map',
            'source': 'source.map',
            'domain': 'domains.map',
            'genome_type': 'genome_type.map',
            'release': 'release.map',
            'tax_hierarchy': 'tax_hierarchy.map',
            'ncbi_tax_id': 'ncbi_tax_id.map',
            'genome_qual_scores': 'genome_qual_scores.map'
            #'gene_functions': 'gene_functions.map'
            }
        
        dst_map_paths = dict()
        for map_type in map_files.keys():
            src_map_path = os.path.join('data','maps', map_files[map_type])
            dst_map_paths[map_type] = os.path.join(shared_dir, map_files[map_type])
            shutil.copy (src_map_path, dst_map_paths[map_type])


        # read expected values
        maps = dict()
        for map_type in map_files.keys():
            if map_type == 'target_list':
                continue
            maps[map_type] = dict()
            with open (dst_map_paths[map_type], 'r') as map_h:
                for map_line in map_h:
                    map_line = map_line.rstrip()
                    [genome_id, field_val] = map_line.split("\t")
                    maps[map_type][genome_id] = field_val
            
        # run method
        params = {
            'workspace_name': self.getWsName(),
            'target_list_file': dst_map_paths['target_list'],
            'object_newname_file': dst_map_paths['obj_name'],
            'species_name_file': dst_map_paths['species_name'],
            'source_file': dst_map_paths['source'],
            'domain_file': dst_map_paths['domain'],
            'genome_type_file': dst_map_paths['genome_type'],
            'release_file': dst_map_paths['release'],
            'taxonomy_hierarchy_file': dst_map_paths['tax_hierarchy'],
            'taxonomy_ncbi_id_file': dst_map_paths['ncbi_tax_id'],
            'genome_qual_scores_file': dst_map_paths['genome_qual_scores'],
            #'gene_functions_file': dst_map_paths['gene_functions'],
            'keep_spoofed_mRNAs': keep_mRNAs
        }
        result = self.getImpl().KButil_update_genome_fields_from_files(self.getContext(),params)[0]
        print('RESULT:')
        pprint(result)

        # check the output
        output_refs = result['updated_object_refs']
        for output_i,output_ref in enumerate(output_refs):
            output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]
            output_obj_info = output_obj['info']
            output_obj_data = output_obj['data']

            output_obj_name = output_obj_info[NAME_I]
            genome_id = re.sub('.Genome$', '', output_obj_name, flags=re.IGNORECASE)
            genome_id = re.sub('__$', '', genome_id)
            genome_id = re.sub('^GTDB_Arc-', '', genome_id, flags=re.IGNORECASE)
            genome_id = re.sub('^GTDB_Bac-', '', genome_id, flags=re.IGNORECASE)
            genome_id = re.sub(r'^(GC[AF]_\d{9}\.\d).*$', r'\1', genome_id)
            print ("GENOME_ID: {}".format(genome_id))

            # test field vals
            #maps[map_type][genome_id] = field_val
            self.assertEqual(output_obj_name, maps['obj_name'][genome_id])
            self.assertEqual(output_obj_data['scientific_name'], maps['species_name'][genome_id])
            self.assertEqual(output_obj_data['source'], maps['source'][genome_id])
            self.assertEqual(output_obj_data['domain'], maps['domain'][genome_id])
            self.assertEqual(output_obj_data['genome_type'], maps['genome_type'][genome_id])
            self.assertEqual(output_obj_data['release'], maps['release'][genome_id])
            self.assertEqual(output_obj_data['taxonomy'], maps['tax_hierarchy'][genome_id])
            self.assertEqual(output_obj_data['taxon_assignments']['ncbi'], maps['ncbi_tax_id'][genome_id])
            self.assertEqual(output_obj_data['taxon_assignments']['gtdb_r207'], maps['tax_hierarchy'][genome_id])
            if keep_mRNAs == 0:
                self.assertEqual(len(output_obj_data['mrnas']),0)

            # test genome_qual_scores
            target_scores = []
            for score_group in maps['genome_qual_scores'][genome_id].split(';'):
                score_dict = {}
                for score_kv in score_group.split(','):
                    [key, val] = score_kv.split('=')
		    score_dict[key] = val
                target_scores.append(score_dict)
            for score_group_i,target_score in enumerate(target_scores):
                for field in ['method', 'method_version', 'score', 'score_interpretation', 'timestamp']:
                    self.assertEqual(output_obj_data['quality_scores'][score_group_i][field], target_score[field])
                

            #'gene_functions': 'gene_functions.map'
        pass

    
