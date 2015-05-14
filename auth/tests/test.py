from django.core.urlresolvers import reverse
from django.test import TestCase


class TestBraintree(TestCase):

    def setUp(self):
        self.url = reverse('braintree')

    def test(self):
        self.client.get(self.url)
