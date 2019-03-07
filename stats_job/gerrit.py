import json
import logging
import re
import requests


LOG = logging.getLogger(__name__)
REVIEW = 'https://review.openstack.org'


class Gerrit(object):
    def __init__(self, users):
        self._users = users
        self._review_url = 'https://review.openstack.org'

    @property
    def users(self):
        return self._users

    @users.setter
    def users(self, value):
        self._users = value

    @property
    def review(self):
        return self._review_url

    @review.setter
    def review(self, value):
        self._review_url = value

    def get_job_and_logs_from_comment(self, comment, date=None):
        pattern = (r'^- (?P<job_name>.*).(?P<log_url>https?:.*).:.'
                   '(?P<job_status>(SUCCESS|FAILURE))')
        LOG.debug('Comment: {}'.format(comment))
        sequence = re.compile(pattern, re.MULTILINE)
        job_and_logs = []
        for match in sequence.finditer(comment):
#              LOG.debug('Group job_name: {}'.format(match.group('job_name')))
#              LOG.debug('Group log_url: {}'.format(match.group('log_url')))
            job_and_logs.append({'job_name': match.group('job_name'),
                                 'log_url': match.group('log_url'),
                                 'job_status': match.group('job_status'),
                                 'date': date})
        return job_and_logs

    def _get_request_content(self, change_id):
        r = requests.get('{}/changes/{}/detail'.format(self.review, change_id))
        if r.status_code == 200:
            return json.loads(r.content[4:-1])
        return None

    def get_data_from_gerrit(self, change_id):
        content = self._get_request_content(change_id)
        if content:
            verified = -1
            jobs = []
            messages = content.get('messages')
            for message in messages:
                if message['author'].get('username') == 'zuul':
                    comment = message['message']
                    jobs = self.get_job_and_logs_from_comment(comment,
                                                              message['date'])

            users = content.get('labels').get('Verified').get('all', [])
            for user in users:
                if user.get('username') == 'zuul':
                    verified = user.get('value', -1)
                    break
            return {'change_id': change_id,
                    'jobs': jobs,
                    'verified': verified}

    def get_job_and_logs_from_gerrit(self, change_id):
        content = self._get_request_content(change_id)
        if content:
            LOG.debug('Gerrit verify: {}'.format(json.dumps(content,
                                                            indent=4,
                                                            sort_keys=True)))
        #  users = content.get('labels', {}).get('Verified', {}).get('all', [])
            messages = content.get('messages')
            for message in messages:
                if message['author'].get('username') == 'zuul':
                    LOG.debug('Zuul message found')
                    content = message['message']
                    LOG.debug('Message: {}'.format(content))
                    return self.get_job_and_logs_from_comment(content)

    def get_verified_from_gerrit(self, change_id):
        content = self._get_request_content(change_id)
        if content:
            users = content.get(
                'labels', {}).get('Verified', {}).get('all', [])
            verified = -1
            for user in users:
                if user.get('username') == 'zuul':
                    LOG.debug('User zuul found')
                    verified = user.get('value', -1)
                    LOG.debug('Verified value: {}'.format(verified))
                    break
            if verified == 1:
                return True
            return False
        else:
            return False
