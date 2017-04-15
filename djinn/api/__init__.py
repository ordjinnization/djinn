import falcon

from .resources import HeatmapResource, ResultsResource


class DJinnAPI(falcon.API):
    """
    REST API for retrieving pipeline data
    """

    def __init__(self, djenkins, pipeline_results, analysis_service):
        """
        Initialize the API with instantiated DJenkins, PipelineResults and AnalysisService objects
        :param djenkins: DJenkins instance
        :param pipeline_results: PipelineResults instance
        :param analysis_service: AnalysisService instance
        """
        super(self.__class__, self).__init__()
        self.djenkins = djenkins
        self.db = pipeline_results
        self.analysis = analysis_service
        heatmap = HeatmapResource(analysis_service=analysis_service)
        self.add_route('/heatmap/', heatmap)
        self.add_route('/heatmap/{project}', heatmap)
        results = ResultsResource(database=self.db)
        self.add_route('/results/', results)
        self.add_route('/results/{project}', results)
        self.add_route('/results/{project}/{repo}', results)
