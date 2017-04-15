import re

import requests

from ..djinnutils.loggers import get_named_logger


class DJenkins(object):
    def __init__(self, url=None, logger=None):
        """
        Client for fetching workflow data from Jenkins' API, and the workflow-api.
        :param url: full URL to connect to Jenkins, including basic auth e.g. "http://admin:apitoken@localhost"
        """
        if not logger:
            logger = get_named_logger('DJenkins')
        self.logger = logger
        if url:
            self.check_for_valid_url(url)
            self.logger.info('URL check: appears to be valid.')
        else:
            self.logger.debug('DJenkins called without a URL!')
        self.jurl = url
        self.session = requests.Session()

    @staticmethod
    def check_for_valid_url(url):
        """
        Verify URL provided contains basic auth. Raises ValueError if regex doesn't match.
        :param url: Jenkins url containing protocol, auth and address, e.g. http://admin:apitoken@localhost
        :raises: ValueError
        :return: True on success
        """
        pattern = r'(https?://)\w.*:\w.*@\w+'
        if not re.match(pattern, url):
            msg = 'Provided URL does not appear to be correct: {}\n\t'.format(url)
            msg += 'Expected format: http(s)://username:password@url, e.g. http://admin:apitoken@localhost'
            raise ValueError(msg)
        return True

    def _get_json_response(self, url):
        """
        Retrieve JSON response from a given URL. Ignore 404 errors as the repo may not have any history, if
        the response returned something other than JSON(e.g. Jenkins 500 ISE error page) swallow it and move on.
        :param url: URL as string
        :return: response as dict
        """
        try:
            resp = self.session.get(url)
            if resp.status_code == 404:
                # Some repos don't have any history, ignore and move on with our lives.
                return dict()
            return resp.json()
        except ValueError as err:
            self.logger.exception('Error retrieving JSON from {}: {}'.format(url, repr(err)))

    @staticmethod
    def _parse_single_pipeline_result(project, repo, pipeline):
        """
        Parse a single pipeline run's data for relevant data, return as dict
        :param project: project name
        :param repo: repository name
        :param pipeline: dict containing pipeline data from the Jenkins WFAPI
        :return: dict of relevant information about this run
        """
        runid = pipeline.get('id')
        status = pipeline.get('status')
        start = pipeline.get('startTimeMillis')
        result = {'id': '{}{}'.format(repo, runid), 'timestamp': start, 'project': project, 'repository': repo,
                  'status': status, 'run_id': runid}
        if status == 'SUCCESS':
            result['success'] = True
        else:
            result['success'] = False
            for stage in pipeline.get('stages'):
                if stage.get('status') == 'FAILED':
                    result['stage_failed'] = stage.get('name')
                    result['error_message'] = stage.get('error').get('message')
                    result['error_type'] = stage.get('error').get('type')
        return result

    def get_organizational_folders(self):
        """
        Retrieve a list of folders linked to source control, defined by their _class attr
        :return: list of folder names as strings
        """
        results = list()
        apiurl = '{}/api/json'.format(self.jurl)
        folders = self._get_json_response(apiurl).get('jobs')
        if not folders:
            return folders
        for folder in folders:
            if folder.get('_class') == 'jenkins.branch.OrganizationFolder':
                results.append(folder.get('name'))
        return filter(None, results)

    def get_repos_in_folder(self, foldername):
        """
        Retrieve all repositories from a given folder
        :param foldername: string
        :return: list of valid repos as strings
        """
        self.logger.info('Retrieving repos in folder {}'.format(foldername))
        results = list()
        apiurl = '{}/job/{}/api/json'.format(self.jurl, foldername)
        jobs = self._get_json_response(apiurl).get('jobs')
        if not jobs:
            return results
        for job in jobs:
            results.append(job.get('name'))
        return filter(None, results)

    def get_pipeline_history_for_repo(self, projectname, reponame, pipelinebranch='develop'):
        """
        Retrieve results for pipeline runs for a given repo.
        :param projectname: Organizational folder containing the repo
        :param reponame: repository name
        :param pipelinebranch: branch to fetch history from.
        :return: list of dicts containing pipeline run information
        """
        self.logger.debug('Retrieving history for {}, branch {}'.format(reponame, pipelinebranch))
        results = list()
        apiurl = '{}/job/{}/job/{}/job/{}/wfapi/runs'.format(self.jurl, projectname, reponame, pipelinebranch)
        pipelines = self._get_json_response(apiurl)
        if not pipelines:
            return results
        for pipeline in pipelines:
            results.append(self._parse_single_pipeline_result(project=projectname, repo=reponame, pipeline=pipeline))
        return filter(None, results)

    def get_pipeline_history_for_all_repos(self, pipelinebranch='develop'):
        """
        Retrieve results for all pipelines found in this instance.
        :param pipelinebranch: branch to fetch history from.
        :return: list of dicts containing pipeline run information
        """
        results = list()
        folders = self.get_organizational_folders()
        for folder in folders:
            repos = self.get_repos_in_folder(foldername=folder)
            for repo in repos:
                results += self.get_pipeline_history_for_repo(projectname=folder, reponame=repo,
                                                              pipelinebranch=pipelinebranch)
        return results
