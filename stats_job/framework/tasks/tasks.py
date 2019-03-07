import json
import logging
import os
import re
import requests
import sys

from datetime import datetime
from sqlalchemy.orm import sessionmaker
from ..celery import app
from database import model

from patterns import Pattern

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

PATTERN_FILE = os.path.join(os.path.dirname(__file__), 'patterns.yml')

TRIPLEOCI = {
    'console': 'job-output.txt.gz',
    "postci": 'logs/undercloud/var/log/extra/logstash.txt.gz',
    'ironic-conductor': ('logs/undercloud/var/log/ironic/ironic-conductor.'
                         'txt.gz'),
    'syslog': 'logs/undercloud/var/log/journal.txt.gz',
    'logstash': 'logs/undercloud/var/log/extra/logstash.txt.gz',
    #  'errors': 'logs/undercloud/var/log/extra/errors.txt.gz'
}


@app.task
def process_results(data):
    for job in data:
        if job['job_status'] == 'SUCCESS':
            reason = {'tag': 'Passed', 'reason': 'SUCCESS'}
        else:
            reason = check_reason(job)

        job['failure_type'] = reason['tag']
        job['reason'] = reason['reason']
        if not insert_job(job):
            LOG.debug('Failed to insert job on database')


def insert_job(job):
    LOG.debug('Inserting job {}'.format(job['job_name']))

    Session = sessionmaker(bind=model.engine)
    session = Session()

    _job = session.query(model.Job).filter(
            model.Job.name == job['job_name']).first()
    if not _job:
        LOG.debug('Job {} not found'.format(job['job_name']))
        return False

    job_run = model.JobRun()
    job_run.status = job['job_status']
    job_run.log_url = job['log_url']
    job_run.reason = job['reason']
    job_run.date = datetime.fromtimestamp(job['date'])
    job_run.job_id = _job.job_id
    job_run.failure_type = job['failure_type']
    job_run.review = job['review']

    session.add(job_run)
    session.commit()

    LOG.debug('Job {} inserted on database'.format(job_run))
    return True


def check_reason(job):
    pattern = Pattern(PATTERN_FILE)
    patterns = pattern.patterns

    msg = {'tag': 'infra', 'reason': 'Reason was not found'}

    for job_key, job_file in TRIPLEOCI.iteritems():
        LOG.debug('Checking {} - {}'.format(job_key, job_file))
        #  try:
        full_log = job['log_url'] + job_file
        LOG.debug('Downloading {}'.format(full_log))
        r = requests.get(full_log)
        if r.status_code == 200:
            found = False
            for line in r.iter_lines():
                for p in patterns.get(job_key, {}):
                    line_matched = (line_match(
                        p["pattern"], line, exclude=p.get("exclude")
                    ))
                    if line_matched:
                        LOG.debug('Line matched! - {}'.format(p['pattern']))
                        msg['tag'] = p['tag']
                        msg['reason'] = p['msg'].format(
                            line_match(p["pattern"], line))
                        found = True
                        break
                if found:
                    return msg
        else:
            LOG.debug('Could not download {}'.format(full_log))
            msg['tag'] = 'infra'
            msg['reason'] = 'Could not download log'
        #  except Exception:
            #  LOG.debug('Could not download {}'.format(full_log))
            #  msg['tag'] = 'infra'
            #  msg['reason'] = 'Failed to fetch logs'

    return msg


def line_match(pat, line, exclude=None):
    exclude = exclude or []
    if any([i in line for i in exclude]):
        return False
    if isinstance(pat, re._pattern_type):
        if not pat.search(line):
            return False
        elif pat.search(line).groups():
            return pat.search(line).group(1)
        else:
            return True
    if isinstance(pat, str):
        return pat in line
