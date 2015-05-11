from logging import getLogger

from django.conf import settings
from django.http import HttpResponse
from django_statsd.clients import statsd

import requests

from auth.exceptions import MissingDestination

log = getLogger(__name__)


def prepare(request):
    try:
        url = request.META[settings.HEADER_DESTINATION]
    except KeyError:
        log.warning('Client did not specify the provider URL in the headers.')
        raise MissingDestination()

    new = {
        'url': url,
        'body': '',
        'method': request.method,
        'headers': {},
        'timeout': settings.DEFAULT_TIMEOUT
    }

    # Add in any headers we need to pass through,
    for k in settings.HEADERS_ALLOWED:
        # Transform the key from the settings into the appropriate
        # format from Django request.
        meta = 'HTTP_' + k.upper().replace('-', '_')
        if meta in request.META:
            new['headers'][k] = request.META[meta]
            log.info('Adding header: {0}, {1}'.format(k, request.META[meta]))

    return new


def send(requested):
    response = HttpResponse()
    print requests
    method = getattr(requests, requested['method'])

    try:
        with statsd.timer('payments-server-auth.send'):
            log.info('Calling: {0}'.format(requested['url']))
            result = method(
                requested['url'],
                data=requested['body'],
                headers=requested['headers'],
                timeout=requested['timeout'],
                verify=True
            )
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
