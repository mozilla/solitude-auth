"""
Django settings for auth project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'please change this'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []


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
HEADERS_ALLOWED = [
    'Accept',
    'Content-type',
    'X-ApiVersion',  # Braintree
    'SOAPAction'  # Bango
]

# Where there the actual destination will be stored in the incoming request.
HEADER_DESTINATION = 'HTTP_X_SOLITUDE_URL'

################################################################
# Payment provider settings.

BANGO_USERNAME = ''
BANGO_PASSWORD = ''

BRAINTREE_PUBLIC_KEY = ''
BRAINTREE_PRIVATE_KEY = ''
