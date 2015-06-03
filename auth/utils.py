from logging import getLogger

from django.conf import settings
from django.http import HttpResponse

import requests
from django_statsd.clients import statsd

from auth.exceptions import MissingDestination

log = getLogger(__name__)


def prepare(request):
    """
    Takes in the incoming request object and does the work
    to figure out what the next request in the chain should be.
    """
    try:
        url = request.META[settings.HEADER_DESTINATION]
    except KeyError:
        log.warning('Client did not specify the provider URL in the headers.')
        raise MissingDestination()

    log.info('Processing request for: {}'.format(url))
    new = {
        'url': url,
        'data': request.body,
        'method': request.method.lower(),
        'headers': {},
        'timeout': settings.DEFAULT_TIMEOUT,
        # Argument passed to requests, see: http://bit.ly/1A4orBB
        'verify': True
    }

    # Add in any headers we need to pass through,
    for incoming, outgoing in settings.HEADERS_ALLOWED.items():
        # Transform the key from the settings into the appropriate
        # format from Django request.
        meta = incoming.upper().replace('-', '_')
        if meta in request.META:
            new['headers'][outgoing] = request.META[meta]
            log.info('Adding header: {}, {} from {}'
                     .format(outgoing, request.META[meta], incoming))

    return new


def send(requested):
    """
    Given data from request, call the actual provider server.

    If a provider generates a 500 it is returned as a 502 and does not raise
    an error locally.

    All other responses are returned to the calling application.
    """
    response = HttpResponse()
    method = getattr(requests, requested.pop('method'))

    if not requested['verify']:
        raise ValueError('verify must be a path to a .crt or True')

    try:
        with statsd.timer('solitude-auth.send'):
            log.info('Calling: {0}'.format(requested['url']))
            result = method(requested.pop('url'), **requested)
    except requests.exceptions.RequestException as err:
        log.exception('%s: %s' % (err.__class__.__name__, err))
        # Return exceptions from the provider as a 502, leaving
        # 500 for payments-server-auth errors.
        response.status_code = 502
        return response

    if result.status_code < 200 or result.status_code > 299:
        log.error('Warning response status: {0}'.format(result.status_code))

    response.status_code = result.status_code
    response.content = result.text
    response['Content-Type'] = result.headers['Content-Type']
    return response


class BraintreeConfig(object):
    """
    Rather than trying to recreate the entire Environment, which needs
    information we don't have, just create an object which contains
    the parts we need to parse webhooks, namely the public and private keys.
    """
    def __init__(self):
        self.public_key = settings.BRAINTREE_PUBLIC_KEY
        self.private_key = settings.BRAINTREE_PRIVATE_KEY


class BraintreeGateway(object):
    """
    Provide access to our simplified BraintreeConfig.
    """
    def __init__(self):
        self.config = BraintreeConfig()
