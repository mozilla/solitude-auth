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
            data='', timeout=30, headers={
                'Authorization': 'Basic Og==',
                'Content-Type': 'application/xml; charset=utf-8'
            })
