from django.conf import settings
from django.core.urlresolvers import reverse

from auth.tests.base import Proxy


class TestBraintree(Proxy):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.url = reverse('braintree')

    def test_ok(self):
        self.req.get.return_value = self.get_response('foo', 200)
        assert self.get(self.url).status_code, 200
        self.req.get.assert_called_with(
            'https://b.c/some/url/',
            verify='https://b.c' + settings.BRAINTREE_CRT,
            data='', timeout=30, headers={'Authorization': 'Basic Og=='})
