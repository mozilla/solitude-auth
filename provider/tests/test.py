from django.core.urlresolvers import reverse
from django.test import TestCase


class TestBango(TestCase):

    def setUp(self):
        self.url = reverse('provider:bango')

    def test(self):
        self.client.get(self.url)


class TestBraintree(TestCase):

    def setUp(self):
        self.url = reverse('provider:braintree')

    def test(self):
        self.client.get(self.url)


class TestReference(TestCase):

    def setUp(self):
        self.url = reverse('provider:reference')

    def test(self):
        self.client.get(self.url)
