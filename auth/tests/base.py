from StringIO import StringIO

from django.conf import settings
from django.test import TestCase

import requests
from mock import patch


class BaseTestCase(TestCase):

    def setUp(self):
        request = patch('auth.utils.requests', name='test.BaseTestCase')
        self.req = request.start()
        self.req.exceptions = requests.exceptions
        self.req.patcher = request
        self.addCleanup(request.stop)

    def get_response(self, data, status_code, headers=None):
        headers = headers or {}
        raw = StringIO()
        raw.write(data)
        raw.seek(0)

        res = requests.Response()
        res.status_code = status_code
        res.raw = raw
        res.headers.update(headers)
        return res

    def get(self, url):
        return self.client.get(
            url, **{settings.HEADER_DESTINATION: 'https://b.c/some/url/'})

    def post(self, url, data, content_type='text/xml'):
        return self.client.post(
            url, data, content_type=content_type,
            **{settings.HEADER_DESTINATION: 'https://b.c/some/url/'}
        )
