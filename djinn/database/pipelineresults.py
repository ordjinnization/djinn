from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from .entity import PipelineRun


class PipelineResults(object):
    def __init__(self, connection_url, echo=False):
        """
        Initialize the database if required, and create a sessionmaker bound to our conn URL.
        :param connection_url: connection url for target database
        :param echo: echo all commands to logs
        """
        if not connection_url:
            raise ValueError('No database connection URL provided.')
        engine = create_engine(connection_url, echo=echo)
        PipelineRun.metadata.create_all(engine)
        self.session_factory = sessionmaker(bind=engine)

    def _check_row_exists(self, pk):
        """
        Check if the row is already in the database using the primary key
        :param pk: primary key to search
        :return: status as boolean
        """
        session = self.session_factory()
        exists = session.query(PipelineRun).filter_by(id=pk).first()
        session.close()
        if exists:
            return True
        return False

    def check_project_exists(self, project):
        """
        Check if a given project has results in our database.
        :param project: project key as string
        :return: status as boolean
        """
        session = self.session_factory()
        exists = session.query(PipelineRun).filter_by(project=project).first()
        session.close()
        if exists:
            return True
        return False

    def _get_filtered_results(self, **kwargs):
        """
        Filter results search by keyword arguments
        :param kwargs: key and value to filter by, e.g. _get_filtered_results(id=1, success=True)
        :return: list of results
        """
        session = self.session_factory()
        results = list(session.query(PipelineRun).filter_by(**kwargs).all())
        session.close()
        return results

    def insert_single_result(self, result):
        """
        Add new unique result to database
        :param result: result from djinn.djenkins.DJenkins as dict
        """
        session = self.session_factory()
        if not self._check_row_exists(pk=result.get('id')):
            session.add(PipelineRun(**result))
        if self._get_filtered_results(id=result.get('id'), status='IN_PROGRESS'):
            session.query(PipelineRun).filter_by(id=result.get('id')).update(result)
        session.commit()
        session.close()

    def insert_result_batch(self, results):
        """
        Add a list of results to database
        :param results: list of results from djinn.djenkins.DJenkins
        """
        session = self.session_factory()
        for result in results:
            if not self._check_row_exists(pk=result.get('id')):
                session.add(PipelineRun(**result))
            if self._get_filtered_results(id=result.get('id'), status='IN_PROGRESS'):
                session.query(PipelineRun).filter_by(id=result.get('id')).update(result)
        session.commit()
        session.close()

    def get_result_by_primary_key(self, pk):
        """
        Retrieve a single result using the primary key(repository name + run id)
        :param pk: primary key to retrieve
        :return: PipelineRun or None
        """
        session = self.session_factory()
        result = session.query(PipelineRun).filter_by(id=pk).first()
        session.close()
        return result

    def get_all_results(self):
        """
        Get all results.
        :return: list of PipelineRun rows
        """
        session = self.session_factory()
        results = list(session.query(PipelineRun).all())
        session.close()
        return results

    def get_all_failures(self):
        """
        Get all failed pipeline runs.
        :return: list of PipelineRun rows.
        """
        return self._get_filtered_results(success=False)

    def get_results_for_project(self, project):
        """
        Get all results for a given project.
        :param project: project name as string
        :return: list of PipelineRun rows
        """
        return self._get_filtered_results(project=project)

    def get_results_for_repo(self, reponame):
        """
        Get all results for a given repository.
        :param reponame: repository as string
        :return: list of PipelineRun rows
        """
        return self._get_filtered_results(repository=reponame)

    def get_failed_results_for_project(self, projectname):
        """
        Get all failed results for a given project.
        :param projectname: project as string
        :return: list of PipelineRun rows
        """
        return self._get_filtered_results(project=projectname, success=False)

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

    def get_failed_results_by_error_type(self, error):
        """
        Get all results for pipelines that failed with a given error.
        :param error: Jenkins error type as string
        :return: list of PipelineRun rows
        """
        return self._get_filtered_results(error_type=error)

    def get_projects(self):
        """
        Return list of project names available.
        :return: List of strings
        """
        session = self.session_factory()
        results = [row.project for row in session.query(PipelineRun.project.distinct().label('project')).all()]
        session.commit()
        session.close()
        return results

    def get_repos_for_project(self, project):
        """
        Return list of repositories in a given project
        :param project: project name as string
        :return: list of strings
        """
        session = self.session_factory()
        results = [row.repo for row in
                   session.query(PipelineRun.repository.distinct().label('repo')).filter_by(project=project).all()]
        session.commit()
        session.close()
        return results

    def get_latest_results(self):
        """
        Return results highest run ID for each repository
        :return: list of PipelineRun rows
        """
        session = self.session_factory()
        results = session.query(PipelineRun).group_by(PipelineRun.repository).all()
        session.close()
        return results

    def get_latest_results_for_project(self, project):
        """
        Check we can retrieve the highest run ID for each repository in a given project.
        :param project: project name as string
        :return: list of PipelineRun rows
        """
        session = self.session_factory()
        results = session.query(PipelineRun).group_by(PipelineRun.repository).filter_by(project=project).all()
        session.close()
        return results
