from djinn import Djinn

JENKINS_URL = 'https://replace:me@jenkinsurl'
DB_URL = 'sqlite:///jenkins.db'
PIPELINE_BRANCH = 'develop'

djinn = Djinn(jenkinsurl=JENKINS_URL, dburl=DB_URL)
djinn.get_all_pipeline_results_and_save_to_db(pipelinebranch=PIPELINE_BRANCH)
app = djinn.create_api()

if __name__ == '__main__':
    from wsgiref import simple_server

    httpd = simple_server.make_server('0.0.0.0', 8000, app)
    httpd.serve_forever()
