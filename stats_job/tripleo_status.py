import json
import logging
import re

from gerrit import Gerrit
from openstack_mqtt import OpenstackMqtt

from framework.tasks import tasks

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class TripleoStatus(object):
    def __init__(self):
        self.start()

    def start(self):
        self.gerrit = Gerrit(['zuul'])
        self.omqtt = OpenstackMqtt()
        self.omqtt.on_connect = self.on_connect
        self.omqtt.on_message = self.on_message
        self.omqtt.connect()
        self.omqtt.client.loop_forever()

    def subscribe(self):
        self.omqtt.add_subscribe('openstack/tripleo-quickstart')
        self.omqtt.add_subscribe('openstack/tripleo-quickstart-extras')
        self.omqtt.add_subscribe('openstack-infra/tripleo-ci')

    def on_connect(self, data):
        self.subscribe()

    def on_message(self, data):
        #  change = self.gerrit.get_data_from_gerrit(data['change_id'])
        #  LOG.debug('Change: {}'.format(json.dumps(change, indent=2)))
        if data['author'] == 'zuul':
            jobs = self.get_job_and_logs_from_data(data)
            LOG.debug('List of jobs found: {}'.format(
                      json.dumps(jobs, indent=4)))
            LOG.debug('Adding job to database')
            tasks.process_results.apply_async(args=[jobs])
            LOG.debug('Job added to database')
        else:
            LOG.debug('We found a comment on {}, but it is not from zuul. '
                      'Discarding'.format(data['change_id']))

    def get_job_and_logs_from_data(self, data):
        pattern = (r'^- (?P<job_name>.*).(?P<log_url>https?:.*).:.'
                   '(?P<job_status>(SUCCESS|FAILURE))')
        comment = data['comment']
        LOG.debug('Gathering information from comment: {}'.format(comment))
        sequence = re.compile(pattern, re.MULTILINE)
        job_and_logs = []
        for match in sequence.finditer(comment):
            #  LOG.debug('Group job_name: {}'.format(match.group('job_name')))
            #  LOG.debug('Group log_url: {}'.format(match.group('log_url')))
            job_and_logs.append({'job_name': match.group('job_name'),
                                 'log_url': match.group('log_url'),
                                 'job_status': match.group('job_status'),
                                 'date': data['date'],
                                 'review': data['change']['url']})

        return job_and_logs


def main():
    TripleoStatus()


if __name__ == '__main__':
    main()
