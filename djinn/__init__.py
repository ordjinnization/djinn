from database import PipelineResults
from jenkins import DJenkins


class Djinn(object):
    def __init__(self, jenkinsurl=None, dburl=None):
        self.dj = DJenkins(baseurl=jenkinsurl)
        self.db = PipelineResults(connection_url=dburl, echo=False)

    def get_all_pipeline_results_and_save_to_db(self, pipelinebranch):
        pipelines = self.dj.get_pipeline_history_for_all_repos(pipelinebranch=pipelinebranch)
        self.db.insert_result_batch(pipelines)
