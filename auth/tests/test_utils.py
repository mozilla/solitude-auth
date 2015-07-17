import json

from django.conf import settings
from django.test import RequestFactory, TestCase

import requests
from nose.tools import eq_, ok_, raises

from auth import utils
from auth.exceptions import MissingDestination
from auth.tests.base import BaseTestCase


class TestPrepare(TestCase):

    def setUp(self):
        self.req = RequestFactory().get('/')
        self.req.META[settings.HEADER_DESTINATION] = '/some/url/'

    @raises(MissingDestination)
    def test_no_header(self):
        utils.prepare(RequestFactory().get('/'))

    def test_body(self):
        data = json.dumps({'key': 'value'})
        post = RequestFactory().post('/', data,
                                     content_type='application/json')
        post.META[settings.HEADER_DESTINATION] = '/some/url/'
        eq_(utils.prepare(post)['data'], data)

    def test_url_ok(self):
        res = utils.prepare(self.req)
        eq_(res['url'], '/some/url/')

    def test_header_added(self):
        self.req.META['HTTP_X_SOLITUDE_SOAPACTION'] = 'something'
        res = utils.prepare(self.req)
        eq_(res['headers']['SOAPAction'], 'something')

    def test_header_ignored(self):
        assert 'Foo' not in settings.HEADERS_ALLOWED
        self.req.META['HTTP_FOO'] = 'bar'
        res = utils.prepare(self.req)
        ok_('Foo' not in res['headers'])


class TestSend(BaseTestCase):

    def send(self, **kwargs):
        kw = {
            'body': '', 'headers': {}, 'method': 'get', 'timeout': 60,
            'url': 'http://f.c', 'verify': True
        }
        kw.update(kwargs)
        return utils.send(kw)

    def test_ok(self):
        self.send()
        self.req.get.assert_called_with(
            'http://f.c', verify=True, body='', timeout=60, headers={})

    @raises(ValueError)
    def test_verify_sanity(self):
        self.send(verify=False)

    def test_patch(self):
        self.send(method='patch')
        assert self.req.patch.assert_called

    def test_network_error(self):
        self.req.get.side_effect = requests.exceptions.RequestException
        res = self.send()
        eq_(res.status_code, 502)

    def test_2xx(self):
        response = self.get_response('foo', 201, {'Content-Type': 'app/xml'})
        self.req.get.return_value = response
        res = self.send()
        eq_(res.status_code, 201)
        eq_(res.content, 'foo')
        eq_(res['Content-Type'], 'app/xml')


def test_url():
    req = RequestFactory().get(
        '/v1/reference/reference/bar?q=1',
        **{settings.HEADER_DESTINATION: 'http://foo.com'})
    eq_(utils.reference_url(req, utils.prepare(req), 'reference'),
        'http://foo.com/bar?q=1')
