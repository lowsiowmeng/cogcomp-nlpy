import unittest
import sys
import os
import six
import codecs

if six.PY2:
    import mock
else:
    import unittest.mock as mock

#sys.path.insert(0,'/path/to/mod_directory')
import sioux

test_config_folder = os.path.dirname(os.path.realpath(__file__))

class TestPipelineConfig(unittest.TestCase):

    def setUp(self):
        with codecs.open(test_config_folder+'/config.cfg',mode='w',encoding='utf-8') as f:
            f.write(
'''
[pipeline_setting]
use_pipeline_server = false

[views_setting]
POS = true
LEMMA = true
NER_CONLL = false
NER_ONTONOTES = false
QUANTITIES = false
SHALLOW_PARSE = false
SRL_VERB = false
DEPENDENCY_STANFORD = false
DEPENDENCY = false
PARSE_STANFORD = false
SRL_PREP = false

[pipeline_server]
api = http://austen.cs.illinois.edu:8080/annotate
''')
        

    @mock.patch('sioux.pipeline_config.download')
    def test_get_current_config(self, mock_dl):
        mock_dl.get_root_directory.return_value = test_config_folder
        mock_dl.get_model_path.return_value = test_config_folder
        config, models = sioux.pipeline_config.get_current_config()
        self.assertEqual(True, models)
        self.assertEqual(config['pipeline_setting']['use_pipeline_server'],'false')
        self.assertEqual(config['views_setting']['LEMMA'], 'true')

    @mock.patch('sioux.pipeline_config.download')
    def test_get_current_config_without_models(self, mock_dl):
        mock_dl.get_root_directory.return_value = test_config_folder
        mock_dl.get_model_path.return_value = 'not_exists_folder_path'
        config, models = sioux.pipeline_config.get_current_config()
        self.assertEqual(False, models)
        self.assertEqual(config['pipeline_setting']['use_pipeline_server'],'true')
        self.assertEqual(config['views_setting']['LEMMA'], 'false')

    # This test is no longer needed because the config file in root directory will be generated when user download the models
    '''
    @mock.patch('sioux.pipeline_config.download')
    def test_get_current_config_with_models(self, mock_dl):
        os.remove(test_config_folder+'/config.cfg')
        mock_dl.get_root_directory.return_value = test_config_folder
        mock_dl.get_model_path.return_value = test_config_folder
        config, models = sioux.pipeline_config.get_current_config()
        self.assertEqual(True, models)
        self.assertEqual(config['views_setting']['LEMMA'], 'false')
        self.assertEqual(config['pipeline_setting']['use_pipeline_server'],'false')
    '''

    @mock.patch('sioux.pipeline_config.download')
    def test_get_user_config(self, mock_dl):
        # such that will use package config if user provided file does not exist
        mock_dl.get_root_directory.return_value = test_config_folder
        mock_dl.get_model_path.return_value = 'not_exists_folder_path'
        config, models = sioux.pipeline_config.get_user_config(test_config_folder+'/config.cfg')
        self.assertEqual(False, models)
        self.assertEqual(config['views_setting']['LEMMA'], 'true')
        self.assertEqual(config['pipeline_setting']['use_pipeline_server'],'true')

        # try provided not exist file name
        config, pack = sioux.pipeline_config.get_user_config('super_strange_file_name')
        self.assertEqual(False, models)
        self.assertEqual(config['pipeline_setting']['use_pipeline_server'],'true')
        self.assertEqual(config['views_setting']['LEMMA'], 'false')

    # Following tests are performed based on the assumption that functions for reading config file is correct
    # And the later tests will depend on the correctness of prior tests
    @mock.patch('sioux.pipeline_config.download')
    def test_log_current_config(self, mock_dl):
        mock_dl.get_root_directory.return_value = test_config_folder
        mock_dl.get_model_path.return_value = test_config_folder

        config, models = sioux.pipeline_config.get_user_config(test_config_folder+'/config.cfg')
        list_of_views = sioux.pipeline_config.log_current_config(config)
        self.assertEqual(list_of_views, ['POS','LEMMA'])

        mock_dl.get_model_path.return_value = 'not_exists_folder_path'
        config, models = sioux.pipeline_config.get_user_config(test_config_folder+'/config.cfg')
        list_of_views = sioux.pipeline_config.log_current_config(config)
        self.assertEqual(list_of_views is None, True)

        config, models = sioux.pipeline_config.get_user_config('strang_config_file') 
        list_of_views = sioux.pipeline_config.log_current_config(config)
        self.assertEqual(list_of_views is None, True)

    @mock.patch('sioux.pipeline_config.download')
    def test_change_temporary_config(self,mock_dl):
        mock_dl.get_root_directory.return_value = test_config_folder
        mock_dl.get_model_path.return_value = test_config_folder

        config, models = sioux.pipeline_config.get_user_config(test_config_folder+'/config.cfg')
        list_of_views = sioux.pipeline_config.change_temporary_config(config, models, ['LEMMA','SRL_PREP'], ['LEMMA','POS'], False, None)
        self.assertEqual(list_of_views, ['LEMMA','SRL_PREP'])

        list_of_views = sioux.pipeline_config.change_temporary_config(config, models, [],[],True,None)
        self.assertEqual(list_of_views is None, True)

        # change on default config
        mock_dl.get_model_path.return_value = 'not_exists_folder_path'
        config, models = sioux.pipeline_config.get_user_config('strang_config_file')
        self.assertEqual(models, False)
        list_of_views = sioux.pipeline_config.change_temporary_config(config, models, ['LEMMA','SRL_PREP'], ['LEMMA','POS'], False, None)
        self.assertEqual(list_of_views is None, True)
        self.assertEqual(config['pipeline_setting']['use_pipeline_server'],'true')

    def tearDown(self):
        if os.path.exists(test_config_folder+'/pipeline_config.cfg'):
            os.remove(test_config_folder+'/pipeline_config.cfg')
