from base64 import encodestring as encodebytes
from urlparse import urlparse

from django.conf import settings

from utils import prepare, send


def bango(request):
    raise NotImplementedError


def braintree(request):
    """
    Pass the request through to Braintree. There are two jobs to do:
    1) Add in the Braintree auth into the HTTP headers
    2) Ensure that requests will check the correct Braintree crt.
    """
    new_request = prepare(request)

    # Add in the correct Braintree Authorization.
    new_request['headers']['Authorization'] = b"Basic " + encodebytes(
        settings.BRAINTREE_PUBLIC_KEY.encode('ascii') + b":" +
        settings.BRAINTREE_PRIVATE_KEY.encode('ascii')).strip()
    # Taken from http://bit.ly/1cBESdC and ensures that the
    # crt is passed through to the requests verify parameter.
    new_request['verify'] = (
        '{url.scheme}://{url.netloc}{crt}'.
        format(url=urlparse(new_request['url']),
               crt=settings.BRAINTREE_CRT))

    return send(new_request)


def reference(request):
    raise NotImplementedError
