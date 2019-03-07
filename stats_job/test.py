from datetime import datetime
from framework.tasks import tasks
from database import model

if __name__ == '__main__':
    jobs = [{
        "job_status": "FAILURE",
        "date": 1540469833,
        "job_name": "legacy-tripleo-ci-centos-7-scenario001-multinode-oooq",
        "log_url": "http://logs.rdoproject.org/openstack-periodic/git.openstack.org/openstack-infra/tripleo-ci/master/periodic-tripleo-ci-centos-7-ovb-1ctlr_1comp-featureset020-rocky/770ccab/"
    }]

    tasks.process_results.apply_async(args=[jobs])
