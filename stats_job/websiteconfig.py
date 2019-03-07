import os

_basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = ('sqlite:///%s' %
                           os.path.join('/home/arxcruz/', 'dashboard.db'))

SQLALCHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY = 'herpaderp'

SOURCE_ROOT = '%s' % os.path.join(_basedir, 'local')

del os
