from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PipelineRun(Base):
    __tablename__ = 'pipeline_runs'
    id = Column(String, primary_key=True)
    run_id = Column(String)
    project = Column(String)
    repository = Column(String)
    status = Column(String)
    timestamp = Column(Integer)
    success = Column(Boolean)
    stage_failed = Column(String)
    error_type = Column(String)
    error_message = Column(String)

    def __repr__(self):
        reprstr = ("<PipelineRun(id={id}, run_id={run_id}, project={project}, repository={repository}, "
                   "status={status}, timestamp={timestamp}, success={success}, stage_failed={stage_failed}, "
                   "error_type={error_type})>")
        return reprstr.format(id=self.id, run_id=self.run_id, project=self.project, repository=self.repository,
                              status=self.status, timestamp=self.timestamp, success=self.success,
                              stage_failed=self.stage_failed, error_type=self.error_type)
