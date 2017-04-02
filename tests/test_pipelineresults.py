from unittest import TestCase

from djinn import PipelineResults


class TestPipelineResults(TestCase):
    successfulresult = {'status': u'SUCCESS', 'success': True, 'repository': 'jenkinsfile-test', 'run_id': u'7',
                        'timestamp': 1491143071036L, 'project': 'TEST', 'id': 'jenkinsfile-test7'}
    failedresult = {'status': u'FAILED', 'error_type': u'hudson.AbortException', 'success': False,
                    'repository': 'jenkinsfile-test', 'run_id': u'6', 'timestamp': 1491143013685L,
                    'error_message': u'Oops.', 'stage_failed': u'Setup', 'project': 'TEST', 'id': 'jenkinsfile-test6'}

    def setUp(self):
        self.db = PipelineResults('sqlite://')  # Use in-memory database for testing

    def test_insert_successful_result_and_retrieve(self):
        self.db.insert_single_result(self.successfulresult)
        result = self.db.get_result_by_primary_key(pk=self.successfulresult.get('id'))
        self.assertDictContainsSubset(self.successfulresult, result.__dict__)

    def test_insert_failed_result_and_retrieve(self):
        self.db.insert_single_result(self.failedresult)
        result = self.db.get_result_by_primary_key(pk=self.failedresult.get('id'))
        self.assertDictContainsSubset(self.failedresult, result.__dict__)

    def test_insert_batch_result_and_retrieve(self):
        batch = [self.successfulresult, self.failedresult]
        self.db.insert_result_batch(results=batch)
        successentry = self.db.get_result_by_primary_key(pk=self.successfulresult.get('id'))
        self.assertDictContainsSubset(self.successfulresult, successentry.__dict__)
        failureentry = self.db.get_result_by_primary_key(pk=self.failedresult.get('id'))
        self.assertDictContainsSubset(self.failedresult, failureentry.__dict__)

    def test_get_all_failures(self):
        batch = [self.successfulresult, self.failedresult]
        self.db.insert_result_batch(results=batch)
        results = self.db.get_all_failures()
        self.assertTrue(len(results) == 1, msg="Retrieved more than a single failure unexpectedly.")
        self.assertDictContainsSubset(self.failedresult, results[0].__dict__)

    def test_get_results_for_repo(self):
        batch = [self.successfulresult, self.failedresult]
        self.db.insert_result_batch(results=batch)
        results = self.db.get_results_for_repo(reponame='jenkinsfile-test')
        for result in results:
            if result.id == self.successfulresult.get('id'):
                self.assertDictContainsSubset(self.successfulresult, result.__dict__)
            elif result.id == self.failedresult.get('id'):
                self.assertDictContainsSubset(self.failedresult, result.__dict__)
            else:
                self.fail('Unknown result from repository search: {}'.format(repr(results)))
