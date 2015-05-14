from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from auth.tests.base import BaseTestCase

from braintree.environment import Environment


@override_settings(BRAINTREE_PUBLIC_KEY='',
                   BRAINTREE_PRIVATE_KEY='')
class TestBraintree(BaseTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.url = reverse('braintree')

    def test_ok(self):
        self.req.get.return_value = self.get_response('foo', 200)
        assert self.get(self.url).status_code, 200
        self.req.get.assert_called_with(
            'https://b.c/some/url/',
            verify=(Environment.braintree_root() +
                    '/ssl/api_braintreegateway_com.ca.crt'),
            data='', timeout=settings.DEFAULT_TIMEOUT, headers={
                'Authorization': 'Basic Og==',
                'Content-Type': 'application/xml; charset=utf-8'
            })


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
        super(self.__class__, self).setUp()
        self.url = reverse('bango')

    def test_ok(self):
        self.req.post.return_value = self.get_response('foo', 200)
        assert self.post(self.url, example).status_code, 200
        data = example.replace('weee!', 'bango').replace('wooo!', 'bob')
        self.req.post.assert_called_with(
            'https://b.c/some/url/', verify=True,
            data=data, timeout=30, headers={'Content-Type': 'text/xml'}
        )
