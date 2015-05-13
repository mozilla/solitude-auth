from StringIO import StringIO

from django.conf import settings
from django.test import RequestFactory, TestCase

from nose.tools import eq_, ok_, raises
from mock import Mock, patch
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

    def send(self, **kwargs):
        kw = {
            'body': '', 'headers': {}, 'method': 'get', 'timeout': 60,
            'url': 'http://f.c',
        }
        kw.update(kwargs)
        return utils.send(kw)

    def body(self, data):
        raw = StringIO()
        raw.write(data)
        raw.seek(0)
        return raw

    def test_ok(self):
        self.send()
        self.req.get.assert_called_with(
            'http://f.c',
            verify=True,
            data='',
            timeout=60,
            headers={}
        )

    def test_patch(self):
        self.send(method='patch')
        assert self.req.patch.assert_called

    def test_network_error(self):
        self.req.get.side_effect = requests.exceptions.RequestException
        res = self.send()
        eq_(res.status_code, 502)

    def test_2xx(self):
        res = requests.Response()
        res.status_code = 101
        res.raw = self.body('foo')
        res.headers['Content-Type'] = 'app/xml'
        self.req.get.return_value = res

        res = self.send()
        eq_(res.status_code, 101)
        eq_(res.content, 'foo')
        eq_(res['Content-Type'], 'app/xml')
