"""
Django settings for auth project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import logging
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'please change this'
DEBUG = True

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []


LOGGING = {
    'version': 1,
    'filters': {},
    'formatters': {},
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'console': {
            '()': logging.StreamHandler,
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
LOGGING_CONFIG = 'django.utils.log.dictConfig'

# Application definition

INSTALLED_APPS = (
    'django_nose',
    'django_statsd',
)

MIDDLEWARE_CLASSES = (
    'auth.exceptions.ExceptionMiddleware',
)

ROOT_URLCONF = 'auth.urls'

WSGI_APPLICATION = 'auth.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

################################################################
# Project specific settings.

DEFAULT_TIMEOUT = 30

# HTTP Headers that we will pass through, if provided by the client.
HEADERS_ALLOWED = {
    'Accept': 'Accept',
    'Content-Type': 'Content-Type',
    'HTTP-X-ApiVersion': 'X-ApiVersion',  # Braintree
    'HTTP-X-Solitude-SOAPAction': 'SOAPAction'  # Bango
}

# Where there the actual destination will be stored in the incoming request.
HEADER_DESTINATION = 'HTTP_X_SOLITUDE_SERVICE'

################################################################
# Payment provider settings.

BANGO_AUTH = {
    'USER': os.environ.get('BANGO_AUTH_USER'),
    'PASSWORD': os.environ.get('BANGO_AUTH_PASSWORD')
}

BRAINTREE_PUBLIC_KEY = os.environ.get('BRAINTREE_PUBLIC_KEY')
BRAINTREE_PRIVATE_KEY = os.environ.get('BRAINTREE_PRIVATE_KEY')
