import json

import falcon


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


class HeatmapResource(object):
    def __init__(self, analysis_service):
        self.service = analysis_service

    def on_get(self, req, resp, project=None):
        if project is None:
            resp.body = json.dumps(self.service.get_failures_heatmap_data())
            resp.status = falcon.HTTP_200
        else:
            resp.body = json.dumps({'Error': 'Not implemented yet.'})
            resp.status = falcon.HTTP_501


class ResultsResource(object):
    def __init__(self, database):
        self.db = database

    def on_get(self, req, resp, project=None):
        if project is None:
            results = self.db.get_all_results()
            output = format_results(results)
            resp.body = json.dumps({'results': output})
            resp.status = falcon.HTTP_200
        else:
            results = self.db.get_results_for_project(project=project)
            output = format_results(results)
            resp.body = json.dumps({'results': output})
            resp.status = falcon.HTTP_200
