from django.conf import settings
from django.test import RequestFactory, TestCase

from nose.tools import eq_, ok_, raises
from mock import patch
from auth.exceptions import MissingDestination
from provider import utils

import requests

class TestPrepare(TestCase):

    def setUp(self):
        self.req = RequestFactory().get('/')
        self.req.META[settings.HEADER_DESTINATION] = '/some/url/'

    @raises(MissingDestination)
    def test_no_header(self):
        utils.prepare(RequestFactory().get('/'))

    def test_url_ok(self):
        res = utils.prepare(self.req)
        eq_(res['url'], '/some/url/')

    def test_header_added(self):
        self.req.META['HTTP_SOAPACTION'] = 'something'
        res = utils.prepare(self.req)
        eq_(res['headers']['SOAPAction'], 'something')

    def test_header_ignored(self):
        assert 'Foo' not in settings.HEADERS_ALLOWED
        self.req.META['HTTP_FOO'] = 'bar'
        res = utils.prepare(self.req)
        ok_('Foo' not in res['headers'])


class Proxy(TestCase):

    def setUp(self):
        request = patch('provider.utils.requests', name='test.proxy')
        self.req = request.start()
        self.req.exceptions = requests.exceptions
        self.req.patcher = request
        self.addCleanup(request.stop)


class TestSend(Proxy):

    def test_ok(self):
        res = utils.send({
            'body': '',
            'headers': {},
            'method': 'get',
            'timeout': 60,
            'url': 'http://f.c',
        })
        self.req.get.assert_called_with(
            'http://f.c',
            verify=True,
            data='',
            timeout=60,
            headers={}
        )
