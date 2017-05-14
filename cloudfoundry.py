import os
from threading import Thread
from time import sleep

from djinn import Djinn


def get_pcf_mysql_connection_string():
    """
    Pivotal Cloud Foundry's connection string doesn't _quite_ work for us, need to change the
    dialect to mysqlclient and drop the reconnect arg.
    :return: formatted mysql database URL as string
    """
    dburl = os.environ.get('DATABASE_URL')
    if not dburl:
        raise EnvironmentError('No database URL found - have you bound a service to the app?')
    if dburl.startswith('mysql2'):
        dburl = dburl.replace('mysql2', 'mysql+mysqldb')
        dburl = dburl.replace('?reconnect=true', '')
    return dburl


def get_jenkins_url_from_env():
    """
    Retrieve Jenkins URL from environment settings set in manifest.
    :return: Jenkins URL as string.
    """
    return os.environ.get('JENKINS_URL')


def get_pipeline_data(frequency=3600):
    """
    Retrieve pipeline data from Jenkins and persist it.
    :param frequency: time in seconds to wait between fetches.
    """
    pipelinebranch = os.environ.get('DJINN_PIPELINE_BRANCH', 'develop')
    while True:
        djinn.get_all_pipeline_results_and_save_to_db(pipelinebranch=pipelinebranch)
        sleep(frequency)


djinn = Djinn(jenkinsurl=get_jenkins_url_from_env(), dburl=get_pcf_mysql_connection_string())
app = djinn.create_api()
fetch = Thread(target=get_pipeline_data)
fetch.setDaemon(True)
fetch.start()
