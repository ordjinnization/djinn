from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PipelineRun(Base):
    __tablename__ = 'pipeline_runs'
    id = Column(String(length=255), primary_key=True)
    run_id = Column(String(length=255))
    project = Column(String(length=255))
    repository = Column(String(length=255))
    status = Column(String(length=255))
    timestamp = Column(String(length=255))
    success = Column(Boolean)
    stage_failed = Column(String(length=255))
    error_type = Column(String(length=255))
    error_message = Column(String(length=4096))

    def __repr__(self):
        reprstr = ("<PipelineRun(id={id}, run_id={run_id}, project={project}, repository={repository}, "
                   "status={status}, timestamp={timestamp}, success={success}, stage_failed={stage_failed}, "
                   "error_type={error_type})>")
        return reprstr.format(id=self.id, run_id=self.run_id, project=self.project, repository=self.repository,
                              status=self.status, timestamp=self.timestamp, success=self.success,
                              stage_failed=self.stage_failed, error_type=self.error_type)
