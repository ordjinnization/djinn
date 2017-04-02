from unittest import TestCase

from betamax import Betamax
from betamax_serializers import pretty_json

from djinn import DJenkins


class TestDjenkins(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jenkins = DJenkins(url='http://admin:103b194e4c57eeda91333e6e51c4f40e@localhost:8080')
        betamaxopts = {'serialize_with': 'prettyjson',
                       'record_mode': 'once',
                       'match_requests_on': ['uri', 'method', 'body', 'headers']}
        cls.recorder = Betamax(session=cls.jenkins.session, cassette_library_dir='cassettes',
                               default_cassette_options=betamaxopts)
        cls.recorder.register_serializer(pretty_json.PrettyJSONSerializer)

    def test_http_url_with_basic_auth_is_valid(self):
        url = 'http://admin:apitoken@localhost'
        self.assertTrue(self.jenkins.check_for_valid_url(url))

    def test_https_url_with_basic_auth_is_valid(self):
        url = 'https://admin:apitoken@localhost'
        self.assertTrue(self.jenkins.check_for_valid_url(url))

    def test_http_url_without_basic_auth_raises_error(self):
        url = 'http://localhost'
        self.assertRaises(ValueError, self.jenkins.check_for_valid_url, url)

    def test_url_without_protocol_raises_error(self):
        url = 'admin:apitoken@localhost'
        self.assertRaises(ValueError, self.jenkins.check_for_valid_url, url)

    def test_get_organizational_folders(self):
        with self.recorder.use_cassette('org_folder'):
            folders = self.jenkins.get_organizational_folders()
            self.assertListEqual(['TEST'], folders)

    def test_get_repos_in_test_folder(self):
        with self.recorder.use_cassette('repos_in_folder'):
            repos = self.jenkins.get_repos_in_folder(foldername='TEST')
            self.assertListEqual(['jenkinsfile-test'], repos)

    def test_get_history_for_repo(self):
        expected = [{'status': u'SUCCESS', 'success': True, 'repository': 'jenkinsfile-test', 'run_id': u'7',
                     'timestamp': 1491143071036L, 'project': 'TEST', 'id': 'jenkinsfile-test7'},
                    {'status': u'FAILED', 'error_type': u'hudson.AbortException', 'success': False,
                     'repository': 'jenkinsfile-test', 'run_id': u'6', 'timestamp': 1491143013685L,
                     'error_message': u'Oops.', 'stage_failed': u'Setup', 'project': 'TEST', 'id': 'jenkinsfile-test6'}]
        with self.recorder.use_cassette('test_repo_history'):
            history = self.jenkins.get_pipeline_history_for_repo(projectname='TEST', reponame='jenkinsfile-test',
                                                                 pipelinebranch='master')
            self.assertItemsEqual(expected_seq=expected, actual_seq=history)
