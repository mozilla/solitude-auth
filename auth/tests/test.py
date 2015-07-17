from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

import mock
from nose.tools import eq_

from braintree.environment import Environment
from braintree.webhook_notification_gateway import WebhookNotificationGateway

from auth.tests.base import BaseTestCase
from auth.utils import BraintreeGateway


@override_settings(BRAINTREE_PUBLIC_KEY='',
                   BRAINTREE_PRIVATE_KEY='')
class TestBraintree(BaseTestCase):

    def setUp(self):
        super(TestBraintree, self).setUp()
        # This is the verify string at test creation which we'll store so tests
        # can manipulate the inputs.
        self.verify_string = (
            WebhookNotificationGateway(BraintreeGateway()).verify(''))

    def test_ok(self):
        self.req.get.return_value = self.get_response('foo', 200)
        assert self.get(reverse('braintree:auth')).status_code, 200
        self.req.get.assert_called_with(
            'https://b.c/some/url/',
            verify=(Environment.braintree_root() +
                    '/ssl/api_braintreegateway_com.ca.crt'),
            data='', timeout=settings.DEFAULT_TIMEOUT, headers={
                'Authorization': 'Basic Og==',
                'Content-Type': 'application/xml; charset=utf-8'
            })

    def test_verify_ok(self):
        res = self.client.get(reverse('braintree:verify'))
        eq_(res.status_code, 200)
        eq_(res.content, self.verify_string)

    def test_verify_changes(self):
        res = self.client.get(reverse('braintree:verify') + '?bt_challenge=f')
        assert res.content != self.verify_string

    def test_verify_changes_with_keys(self):
        with self.settings(BRAINTREE_PUBLIC_KEY='foo'):
            res = self.client.get(reverse('braintree:verify'))
            assert res.content != self.verify_string

    def test_parse_payload(self):
        with mock.patch('braintree.webhook_notification_gateway.'
                        'WebhookNotificationGateway.parse') as parse:
            parse.return_value = {}
            res = self.client.post(
                reverse('braintree:parse'),
                {'bt_signature': 'sig', 'bt_payload': 'payload'}
            )
            parse.assert_called_with('sig', 'payload')
        eq_(res.status_code, 204)

    def test_parse_payload_not_ok(self):
        res = self.client.post(
            reverse('braintree:parse'),
            {'bt_signature': self.verify_string, 'bt_payload': 'b'}
        )
        eq_(res.status_code, 403)

    def test_parse_totally_not_ok(self):
        res = self.client.post(reverse('braintree:parse'))
        eq_(res.status_code, 403)


# The SOAP-ENV is all on the same line so that the new lines equals the output
# from etree.
example = """<SOAP-ENV:Envelope xmlns:ns0="com.bango.webservices.mozillaexporter" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
    <SOAP-ENV:Header/>
    <ns1:Body>
        <ns0:CreatePackage>
            <ns0:request>
                <ns0:username>weee!</ns0:username>
                <ns0:password>wooo!</ns0:password>
            </ns0:request>
        </ns0:CreatePackage>
    </ns1:Body>
</SOAP-ENV:Envelope>"""  # noqa


@override_settings(BANGO_AUTH={'USER': 'bango', 'PASSWORD': 'bob'})
class TestBango(BaseTestCase):

    def setUp(self):
        super(TestBango, self).setUp()
        self.url = reverse('bango')

    def test_ok(self):
        self.req.post.return_value = self.get_response('foo', 200)
        assert self.post(self.url, example).status_code, 200
        data = example.replace('weee!', 'bango').replace('wooo!', 'bob')
        self.req.post.assert_called_with(
            'https://b.c/some/url/', verify=True,
            data=data, timeout=30, headers={'Content-Type': 'text/xml'}
        )


class TestZippy(BaseTestCase):

    def setUp(self):
        super(TestZippy, self).setUp()
        self.url = reverse('reference', kwargs={'reference_name': 'reference'})

    def test_not_registered(self):
        with self.assertRaises(ValueError):
            url = reverse('reference', kwargs={'reference_name': 'foo'})
            self.get(url).status_code

    def test_ok(self):
        assert self.get(self.url + '/something?else=1').status_code, 200
        self.req.get.assert_called_with(
            'https://b.c/something?else=1', verify=True,
            data='', timeout=30,
            headers={'Authorization': mock.ANY}
        )
        auth = self.req.get.call_args[1]['headers']['Authorization']
        # A quick smoke test that signing happened and it smells like OAuth.
        assert auth.startswith('OAuth realm="zippy:2605", oauth_nonce')
