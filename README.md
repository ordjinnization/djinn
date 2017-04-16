# Djinn: fetching and persisting Jenkins' pipeline information

## Summary

If you're using Jenkins Pipelines, you might already be familiar with the 
[Pipeline Stage View Plugin](https://github.com/jenkinsci/pipeline-stage-view-plugin),
which provides a lovely graph of the last 11 pipeline runs and the results of each stage.

This is great for day to day usage, but this data gathered over the course of hundreds of 
runs across all your projects could be useful for determining flakiness in your common 
build/test configurations. Djinn is meant to serve as a single source of pipeline data,
preserving historical data beyond that offered by the Stage View Plugin.

How you manage and access this data is up to you - while the whole project is meant to 
live as a REST API somewhere that periodically polls Jenkins and writes the data out to 
a SQL database, it should be pretty trivial to import the particular bits you want
and do whatever. 

## Setup

For running locally, edit `local.py` and replace the JENKINS_URL, DB_URL and 
PIPELINE_BRANCH variables appropriately. This will use SQLite as a local database, which is 
_not_ thread-safe, so no attempt has been made to schedule data refreshes. After initial
population is complete, the API should be available on http://localhost:8000 .

For CloudFoundry deployments, everything you need is set in `manifest.yml`. A MySQL service
should be created before attempting to push. Your environment may differ, but assuming 
a service `p-mysql` with a plan `500mb-dev` is available, you can create this using the
CloudFoundry CLI client like so:  
`cf create-service p-mysql 500mb-dev djinn-mysql`

Once your manifest is set, deployment is a simple `cf push djinn`.

## API usage

The raw data retrieved from Jenkins can be retrieved using the `/results/` path. For
more granularity, you can add a project key and a further repository name to only
fetch that subset, e.g.:  
```bash
# Fetch only the top level folder TEST
curl https://djinnurl/results/TEST
# Fetch only the example-repo from the TEST folder
curl https://djinnurl/results/TEST/example-repo
```

Heatmap data can be retrieved from the `/heatmap/` path. This endpoint is designed to be 
used with wayofthepie's [djinn-ui](https://github.com/wayofthepie/djinn-ui) project.