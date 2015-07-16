import logging

import private_base as private

from solitude.settings import base
from django_sha2 import get_password_hashers

ALLOWED_HOSTS = ['payments-proxy-dev.allizom.org']

DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = False

HMAC_KEYS = private.HMAC_KEYS

PASSWORD_HASHERS = get_password_hashers(base.BASE_PASSWORD_HASHERS, HMAC_KEYS)

LOG_LEVEL = logging.DEBUG

SECRET_KEY = private.SECRET_KEY

SENTRY_DSN = private.SENTRY_DSN

STATSD_HOST = private.STATSD_HOST
STATSD_PORT = private.STATSD_PORT
STATSD_PREFIX = private.STATSD_PREFIX

SYSLOG_TAG = 'http_app_payments_dev'

NEWRELIC_INI = '/etc/newrelic.d/payments-proxy-dev.allizom.org.ini'

ZIPPY_CONFIGURATION = {
    'reference': {
        'url': 'https://zippy-dev.allizom.org',
        'auth': {'key': private.ZIPPY_PAAS_KEY,
                 'secret': private.ZIPPY_PAAS_SECRET,
                 'realm': 'zippy-dev.allizom.org'}
    },
}
