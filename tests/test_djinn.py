import os

from falcon import testing

from djinn import Djinn


class TestDjinn(testing.TestCase):
    basefolder = os.path.dirname(os.path.realpath(__file__))
    mock_results = [{'status': u'SUCCESS', 'success': True, 'repository': 'jenkinsfile-test', 'run_id': u'7',
                     'timestamp': '1491143071036', 'project': 'TEST', 'id': 'jenkinsfile-test7'},
                    {'status': u'FAILED', 'error_type': u'hudson.AbortException', 'success': False,
                     'repository': 'jenkinsfile-test', 'run_id': u'6', 'timestamp': '1491143013685',
                     'error_message': u'Oops.', 'stage_failed': u'Setup', 'project': 'TEST',
                     'id': 'jenkinsfile-test6'},
                    {'status': u'FAILED', 'error_type': u'hudson.AbortException', 'success': False,
                     'repository': 'jenkinsfile-test', 'run_id': u'5', 'timestamp': '1491143013620',
                     'error_message': u'Oops.', 'stage_failed': u'Deploy', 'project': 'TEST',
                     'id': 'jenkinsfile-test5'}]

    @classmethod
    def setUpClass(cls):
        cls.djinn = Djinn(dburl='sqlite:///')
        cls.djinn.db.insert_result_batch(results=cls.mock_results)

    def setUp(self):
        super(TestDjinn, self).setUp()
        self.app = self.djinn.create_api()

    def test_heatmap(self):
        expected_heatmap = {u'x': [u'Setup', u'Deploy'], u'y': [u'TEST'], u'z': [[1, 1]]}
        result = self.simulate_get('/heatmap/')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, expected_heatmap)

    def test_heatmap_for_project(self):
        """
        Unimplemented, will break once implemented.
        """
        result = self.simulate_get('/heatmap/TEST/')
        self.assertEqual(result.status_code, 501)

    def test_results(self):
        result = self.simulate_get('/results/')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json['results']['TEST']['jenkinsfile-test']), 3)

    def test_results_for_project_that_exists(self):
        result = self.simulate_get('/results/TEST')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json['results']['TEST']['jenkinsfile-test']), 3)

    def test_results_for_project_that_does_not_exist(self):
        result = self.simulate_get('/results/FAKENEWS')
        self.assertEqual(result.status_code, 404)

    def test_results_for_project_and_repo_that_exist(self):
        result = self.simulate_get('/results/TEST/jenkinsfile-test')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json['results']['TEST']['jenkinsfile-test']), 3)

    def test_results_for_repo_with_nonexistent_project(self):
        result = self.simulate_get('/results/FAKENEWS/jenkinsfile-test')
        self.assertEqual(result.status_code, 404)

    def test_results_cors_header(self):
        result = self.simulate_get('/results/')
        self.assertEqual(result.headers['Access-Control-Allow-Origin'], '*')

    def test_heatmap_cors_header(self):
        result = self.simulate_get('/heatmap/')
        self.assertEqual(result.headers['Access-Control-Allow-Origin'], '*')
