from base64 import encodestring as encodebytes

from django.conf import settings

from utils import prepare, send


def bango(request):
    raise NotImplementedError


def braintree(request):
    new_request = prepare(request)
    new_request['headers']['Authorization'] = b"Basic " + encodebytes(
        settings.BRAINTREE_PUBLIC_KEY.encode('ascii') + b":" +
        settings.BRAINTREE_PRIVATE_KEY.encode('ascii')).strip()
    return send('braintree', new_request)


def reference(request):
    raise NotImplementedError
