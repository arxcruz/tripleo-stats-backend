from __future__ import absolute_import
from celery import Celery


app = Celery(include=['framework.tasks.tasks'])
app.config_from_object('framework.celeryconfig')


if __name__ == '__main__':
    app.start()
