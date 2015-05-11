from base64 import encodestring as encodebytes

from django.conf import settings

from utils import prepare, send


def bango(request):
    raise NotImplementedError


def braintree(request):
    new_request = prepare(request)
    new_request['headers']['Authorization'] = braintree_authorization()
    return send('braintree', new_request)


def braintree_authorization(self):
    return b"Basic " + encodebytes(
        settings.BRAINTREE_PUBLIC_KEY.encode('ascii') +
        b":" +
        settings.BRAINTREE_PRIVATE_KEY.encode('ascii')
    ).replace(b"\n", b"").strip()


def reference(request):
    raise NotImplementedError
