import time
from unittest import TestCase

from djinn import PipelineResults


def generate_mock_result(project='TEST', repository=None, status='SUCCESS', success=True, run_id=1,
                         timestamp=None):
    """
    Create a dict matching the format used for writing to the database.
    :param project: project name as string
    :param repository: repository. If None, {project}-repo will be used.
    :param status: status as string
    :param success: boolean
    :param run_id: integer
    :param timestamp: timestamp in milliseconds since epoch as string. If None, now will be used.
    :return: result dictionary
    """
    if not timestamp:  # If no time provided, use right now.
        timestamp = str(int(time.time() * 1000))
    if not repository:
        repository = '{}-repo'.format(project.lower())
    result = dict(project=project, repository=repository, status=status, success=success, run_id=run_id,
                  timestamp=timestamp, id='{}{}'.format(repository, run_id))
    return result


class TestPipelineResults(TestCase):
    successfulresult = {'status': u'SUCCESS', 'success': True, 'repository': 'jenkinsfile-test', 'run_id': u'7',
                        'timestamp': '1491143071036', 'project': 'TEST', 'id': 'jenkinsfile-test7'}
    failedresult = {'status': u'FAILED', 'error_type': u'hudson.AbortException', 'success': False,
                    'repository': 'jenkinsfile-test', 'run_id': u'6', 'timestamp': '1491143013685',
                    'error_message': u'Oops.', 'stage_failed': u'Setup', 'project': 'TEST', 'id': 'jenkinsfile-test6'}

    def setUp(self):
        self.db = PipelineResults('sqlite://')  # Use in-memory database for testing

    def test_insert_successful_result_and_retrieve(self):
        """
        Check we can insert and read back successful results.
        """
        self.db.insert_single_result(self.successfulresult)
        result = self.db.get_result_by_primary_key(pk=self.successfulresult.get('id'))
        self.assertDictContainsSubset(self.successfulresult, result.__dict__)

    def test_insert_failed_result_and_retrieve(self):
        """
        Check we can insert and read back failed results.
        """
        self.db.insert_single_result(self.failedresult)
        result = self.db.get_result_by_primary_key(pk=self.failedresult.get('id'))
        self.assertDictContainsSubset(self.failedresult, result.__dict__)

    def test_insert_batch_result_and_retrieve(self):
        """
        Check we can insert batches of results.
        """
        batch = [self.successfulresult, self.failedresult]
        self.db.insert_result_batch(results=batch)
        successentry = self.db.get_result_by_primary_key(pk=self.successfulresult.get('id'))
        self.assertDictContainsSubset(self.successfulresult, successentry.__dict__)
        failureentry = self.db.get_result_by_primary_key(pk=self.failedresult.get('id'))
        self.assertDictContainsSubset(self.failedresult, failureentry.__dict__)

    def test_update_single_row_if_status_is_in_progress(self):
        """
        Check that a row previously saved as IN_PROGRESS is updated with the latest result.
        """
        first = generate_mock_result(status='IN_PROGRESS', success=False)
        self.db.insert_single_result(first)
        current = self.db.get_result_by_primary_key(first.get('id'))
        self.assertEqual(current.status, 'IN_PROGRESS')
        second = generate_mock_result(status='SUCCESS', success=True)
        self.db.insert_single_result(second)
        current = self.db.get_result_by_primary_key(first.get('id'))
        self.assertEqual(current.status, 'SUCCESS')

    def test_insert_batch_result_with_a_single_update(self):
        """
        Check that a row previously saved as IN_PROGRESS is updated with the latest result
        as part of a batch insert.
        """
        incomplete = generate_mock_result(status='IN_PROGRESS', success=False, run_id=1)
        self.db.insert_result_batch(results=[incomplete, generate_mock_result(run_id=2)])
        self.assertEqual(2, len(self.db.get_results_for_project('TEST')))
        self.assertEqual(1, len(self.db.get_failed_results_for_project('TEST')))
        incomplete.update({'status': 'SUCCESS', 'success': True})
        self.db.insert_result_batch(results=[incomplete, generate_mock_result(run_id=3)])
        self.assertEqual(3, len(self.db.get_results_for_project('TEST')))
        self.assertEqual(0, len(self.db.get_failed_results_for_project('TEST')))

    def test_get_all_failures(self):
        """
        Check that only failed results are returned.
        """
        batch = [self.successfulresult, self.failedresult]
        self.db.insert_result_batch(results=batch)
        results = self.db.get_all_failures()
        self.assertTrue(len(results) == 1, msg="Retrieved more than a single failure unexpectedly.")
        self.assertDictContainsSubset(self.failedresult, results[0].__dict__)

    def test_get_results_for_repo(self):
        """
        Check filtering for results by repository name.
        """
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

    def test_get_projects(self):
        """
        Check we can retrieve a unique list of projects
        """
        for project in ['TEST', 'NEWTEST', 'MYPROJECT']:
            self.db.insert_single_result(generate_mock_result(project=project))
        projects = self.db.get_projects()
        self.assertItemsEqual(['MYPROJECT', 'NEWTEST', 'TEST'], projects)

    def test_get_repos_for_project(self):
        """
        Check we can retrieve all repositories for a given project.
        """
        batch = list()
        for project in ['TEST', 'NEWTEST']:
            for i in xrange(5):
                batch.append(generate_mock_result(project=project, run_id=i))
        self.db.insert_result_batch(results=batch)
        testrepos = self.db.get_repos_for_project(project='TEST')
        self.assertListEqual(['test-repo'], testrepos)
        newtestrepos = self.db.get_repos_for_project(project='NEWTEST')
        self.assertListEqual(['newtest-repo'], newtestrepos)
        norepos = self.db.get_repos_for_project(project='FAKE_NEWS')
        self.assertListEqual([], norepos)

    def test_get_latest_results(self):
        """
        Check we can retrieve the highest run ID for all repositories.
        Use a range that includes 99, 100 to verify we're not getting the max string value('99' > '100')
        """
        for x in xrange(98, 103):
            self.db.insert_single_result(generate_mock_result(repository='test-repo', run_id=x))
            self.db.insert_single_result(generate_mock_result(repository='newtest-repo', run_id=x + 1))
        results = self.db.get_all_results()
        self.assertEqual(len(results), 10)
        latest = self.db.get_latest_results()
        self.assertEqual(len(latest), 2)
        for result in latest:
            if result.repository == 'test-repo':
                self.assertEqual(result.run_id, '102')
            elif result.repository == 'newtest-repo':
                self.assertEqual(result.run_id, '103')

    def test_get_latest_results_for_repo(self):
        """
        Check we can retrieve the highest run ID for each repository in a project.
        Use a range that includes 99, 100 to verify we're not getting the max string value('99' > '100')
        """
        for x in xrange(98, 103):
            self.db.insert_single_result(generate_mock_result(project='TEST', repository='test-repo', run_id=x))
            self.db.insert_single_result(generate_mock_result(project='NEWTEST', repository='newtest-repo', run_id=x))
        testlatest = self.db.get_latest_results_for_project('TEST')
        self.assertEqual(len(testlatest), 1)
        self.assertEqual(testlatest[0].repository, 'test-repo')
        self.assertEqual(testlatest[0].run_id, '102')
