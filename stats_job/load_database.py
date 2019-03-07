from sqlalchemy.orm import sessionmaker
from database import model


COLUMNED_TRACKED_JOBS = {
    'Containers': [
        'tripleo-ci-centos-7-containers-multinode',
        'tripleo-ci-centos-7-scenario001-multinode-oooq-container',
        'tripleo-ci-centos-7-scenario002-multinode-oooq-container',
        'tripleo-ci-centos-7-scenario003-multinode-oooq-container',
        'tripleo-ci-centos-7-scenario004-multinode-oooq-container',
        'tripleo-ci-centos-7-scenario007-multinode-oooq-container',
        'tripleo-ci-centos-7-scenario008-multinode-oooq-container',
        'tripleo-ci-centos-7-scenario010-multinode-oooq-container',
        'tripleo-ci-centos-7-standalone'
    ],
    'OVB': [
        'tripleo-ci-centos-7-ovb-1ctlr_1comp-featureset022',
        'tripleo-ci-centos-7-ovb-1ctlr_1comp_1ceph-featureset024',
        'tripleo-ci-centos-7-ovb-3ctlr_1comp-featureset001',
        'tripleo-ci-centos-7-ovb-3ctlr_1comp-featureset001-pike-branch',
        'tripleo-ci-centos-7-ovb-3ctlr_1comp-featureset001-queens-branch',
        'tripleo-ci-centos-7-ovb-3ctlr_1comp-featureset001-rocky-branch',
        'tripleo-ci-centos-7-ovb-3ctlr_1comp-featureset035',
        'tripleo-ci-centos-7-ovb-3ctlr_1comp-featureset053'
    ],

    'Scenarios': [
        'tripleo-ci-centos-7-scenario001-multinode-oooq',
        'tripleo-ci-centos-7-scenario002-multinode-oooq',
        'tripleo-ci-centos-7-scenario003-multinode-oooq',
        'tripleo-ci-centos-7-scenario004-multinode-oooq',
        'tripleo-ci-centos-7-scenario006-multinode-oooq',
        'tripleo-ci-centos-7-scenario009-multinode-oooq'
    ],

    'Update/Upgrades': [
        'tripleo-ci-centos-7-containerized-undercloud-upgrades',
        'tripleo-ci-centos-7-scenario000-multinode-oooq-container-updates',
        'tripleo-ci-centos-7-scenario000-multinode-oooq-container-upgrades',
        'tripleo-ci-centos-7-undercloud-upgrades'
    ],

    'Branches': [
        'tripleo-ci-centos-7-containers-multinode-pike',
        'tripleo-ci-centos-7-containers-multinode-queens',
        'tripleo-ci-centos-7-containers-multinode-rocky'
    ],

    'Multinode': [
        'tripleo-ci-centos-7-nonha-multinode-oooq'
    ]
}


def load_jobs_in_database():
    Session = sessionmaker(bind=model.engine)
    session = Session()

    category = model.Category()
    category.description = 'Tripleo CI gate jobs'
    session.add(category)
    session.commit()

    for key in COLUMNED_TRACKED_JOBS:
        job_type = model.JobType()
        job_type.description = key
        session.add(job_type)
        session.commit()
        for job in COLUMNED_TRACKED_JOBS[key]:
            job = model.Job(name=job)
            job.job_type = job_type
            category.jobs.append(job)
            session.add(job)
        session.commit()


if __name__ == '__main__':
    load_jobs_in_database()
