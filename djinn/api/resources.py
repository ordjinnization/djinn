import json

import falcon

from ..analysis import gen_heatmap_with_strategy, projects_stage_inner_groupby, repos_stage_inner_groupby


def format_results(resultlist):
    """
    Take a list of SQLAlchemy DB objects and arrange them into a dict of {project: {repository: [stages] } }
    :param resultlist: list of stage results
    :return: formatted dict of results
    """
    output = dict()
    for item in resultlist:
        item = item.__dict__
        item.pop('_sa_instance_state')
        output.setdefault(item.get('project'), {}).setdefault(item.get('repository'), []).append(item)
    return output


def set_cors_header(req, resp, resource):
    """
    CORS function to be used with Falcon.after decorators. Args are provided by Falcon calls.
    """
    resp.set_header(name='Access-Control-Allow-Origin', value='*')


@falcon.after(set_cors_header)
class HeatmapResource(object):
    """
    REST resource for heatmap data
    """

    def __init__(self, database):
        self.db = database

    def on_get(self, req, resp, project=None):
        if project is None:
            failures = self.db.get_all_failures()
            resp.body = json.dumps(
                    gen_heatmap_with_strategy(projects_stage_inner_groupby, failures))
            resp.status = falcon.HTTP_200
        else:
            failures = self.db.get_failed_results_for_project(project)
            resp.body = json.dumps(
                    gen_heatmap_with_strategy(repos_stage_inner_groupby, failures))
            resp.status = falcon.HTTP_200


@falcon.after(set_cors_header)
class ResultsResource(object):
    """
    REST resource for raw results
    """

    def __init__(self, database):
        self.db = database

    def on_get(self, req, resp, project=None, repo=None):
        if project:
            if not self.db.check_project_exists(project):
                resp.body = json.dumps({'Error': 'Project key {} not found!'.format(project)})
                resp.status = falcon.HTTP_404
                return

        if project and repo:
            results = self.db.get_results_for_repo(reponame=repo)
        elif project:
            results = self.db.get_results_for_project(project=project)
        else:
            results = self.db.get_all_results()
        resp.body = json.dumps({'results': format_results(results)})
        resp.status = falcon.HTTP_200


@falcon.after(set_cors_header)
class ProjectResource(object):
    """
    REST resource for available projects, or a list of repositories for a given project
    """

    def __init__(self, database):
        self.db = database

    def on_get(self, req, resp, project=None):
        if project:
            if not self.db.check_project_exists(project):
                resp.body = json.dumps({'Error': 'Project key {} not found!'.format(project)})
                resp.status = falcon.HTTP_404
                return

        if project:
            repos = self.db.get_repos_for_project(project)
            body = {'repositories': repos}
        else:
            projects = self.db.get_projects()
            body = {'projects': projects}
        resp.body = json.dumps(body)
        resp.status = falcon.HTTP_200
