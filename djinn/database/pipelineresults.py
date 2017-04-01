from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from entity import PipelineRun


class PipelineResults(object):
    def __init__(self, connection_url, echo=False):
        """
        Initialize the database if required, and create a session.
        :param connection_url: connection url for target database
        :param echo: echo all commands to logs
        """
        engine = create_engine(connection_url, echo=echo)
        PipelineRun.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()
        self.pipelinequery = self.session.query(PipelineRun)

    def _check_row_exists(self, pk):
        """
        Check if the row is already in the database using the primary key
        :param pk: primary key to search
        :return: status as boolean
        """
        exists = self.pipelinequery.filter_by(id=pk).all()
        if exists:
            return True
        return False

    def _get_filtered_results(self, **kwargs):
        """
        Filter results search by keyword arguments
        :param kwargs: key and value to filter by, e.g. _get_filtered_results(id=1, success=True)
        :return: list of results
        """
        return self.pipelinequery.filter_by(**kwargs).all()

    def insert_single_result(self, result):
        """
        Add new unique result to database
        :param result: result from djinn.jenkins.DJenkins as dict
        """
        if not self._check_row_exists(pk=result.get('id')):
            self.session.add(PipelineRun(**result))
        self.session.commit()

    def insert_result_batch(self, results):
        """
        Add a list of results to database
        :param results: list of results from djinn.jenkins.DJenkins
        """
        for result in results:
            if not self._check_row_exists(pk=result.get('id')):
                self.session.add(PipelineRun(**result))
        self.session.commit()

    def get_all_results(self):
        """
        Get all results.
        :return: list of PipelineRun rows
        """
        return self.pipelinequery.all()

    def get_all_failures(self):
        """
        Get all failed pipeline runs.
        :return: list of PipelineRun rows.
        """
        return self._get_filtered_results(success=False)

    def get_results_for_repo(self, reponame):
        """
        Get all results for a given repository.
        :param reponame: repository as string
        :return: list of PipelineRun rows
        """
        return self._get_filtered_results(repository=reponame)

    def get_failed_results_for_repo(self, reponame):
        """
        Get all failed pipeline runs for a given repository.
        :param reponame: repository as string
        :return: list of PipelineRun rows
        """
        return self._get_filtered_results(repository=reponame, success=False)

    def get_failed_results_for_stage(self, stage):
        """
        Get all results for pipelines that failed at a given stage.
        :param stage: stage name as string
        :return: list of PipelineRun rows
        """
        return self._get_filtered_results(stage_failed=stage)
