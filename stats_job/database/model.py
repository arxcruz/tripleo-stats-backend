import datetime
import os

from sqlalchemy import create_engine, Column, DateTime, Integer, Sequence
from sqlalchemy import String, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class JobRun(Base):
    __tablename__ = 'job_run'

    job_run_id = Column('job_run_id', Integer, primary_key=True)
    job_id = Column('job_id', String, ForeignKey('job.job_id'))
    status = Column('status', String)
    log_url = Column('log_url', String)
    reason = Column('reason', String)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    failure_type = Column('failure_type', String)
    review = Column('review', String)

    def __repr__(self):
        return '{} - {} - {}'.format(self.job_id, self.status, self.log_url)


class JobType(Base):
    __tablename__ = 'job_type'

    job_type_id = Column('job_type_id', Integer, primary_key=True)
    description = Column('description', String)


category_job = Table('category_job', Base.metadata,
                     Column('job_id', Integer, ForeignKey('job.job_id')),
                     Column('category_id', Integer,
                            ForeignKey('category.category_id')))


class Category(Base):
    __tablename__ = 'category'

    category_id = Column('category_id', Integer, primary_key=True)
    description = Column('description', String)
    jobs = relationship('Job', secondary=category_job, backref='parents')


class Job(Base):
    __tablename__ = 'job'
    job_id = Column('job_id', Integer, Sequence('job_id_seq'),
                    primary_key=True)
    name = Column('name', String)
    job_type_id = Column('job_type_id', String,
                         ForeignKey('job_type.job_type_id'))
    job_type = relationship('JobType')


engine = create_engine('sqlite:///%s' % os.path.join(
    '/home/arxcruz/', 'dashboard.db'), echo=True)

Base.metadata.create_all(engine)
