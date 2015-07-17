from logging import getLogger
from base64 import encodestring as encodebytes

from curling.lib import sign_request
from lxml import etree

from django.conf import settings

from django.http import HttpResponse

from utils import BraintreeGateway, prepare, reference_url, send

from braintree.environment import Environment
from braintree.webhook_notification_gateway import WebhookNotificationGateway

log = getLogger(__name__)


def bango(request):
    """
    Pass the request through to Bango. There's one job:
    1) Parse the XML and insert the correct user and password
    """
    namespaces = [
        'com.bango.webservices.billingconfiguration',
        'com.bango.webservices.directbilling',
        'com.bango.webservices.mozillaexporter'
    ]

    new_request = prepare(request)
    # Alter the XML to include the username and password from the config.
    root = etree.fromstring(new_request['data'])

    tags = lambda name: ['{%s}%s' % (n, name) for n in namespaces]
    username, password = tags('username'), tags('password')
    changed_username, changed_password = False, False

    for element in root.iter():
        if element.tag in username:
            element.text = settings.BANGO_AUTH.get('USER', '')
            changed_username = True
        elif element.tag in password:
            element.text = settings.BANGO_AUTH.get('PASSWORD', '')
            changed_password = True
        # No point in process the rest of the body if both have
        # been changed.
        if changed_username and changed_password:
            break

    new_request['data'] = etree.tostring(root)
    return send(new_request)


def braintree(request):
    """
    Pass the request through to Braintree. There are two jobs to do:
    1) Add in the Braintree auth into the HTTP headers
    2) Ensure that requests will check the correct Braintree crt.
    """
    new_request = prepare(request)
    # Until https://github.com/mozilla/solitude-auth/pull/3 is merged.
    new_request['headers']['Content-Type'] = 'application/xml; charset=utf-8'
    # Add in the correct Braintree Authorization.
    new_request['headers']['Authorization'] = b"Basic " + encodebytes(
        settings.BRAINTREE_PUBLIC_KEY.encode('ascii') + b":" +
        settings.BRAINTREE_PRIVATE_KEY.encode('ascii')).strip()
    # Taken from http://bit.ly/1cBESdC and ensures that the
    # crt is passed through to the requests verify parameter.
    new_request['verify'] = (
        Environment.braintree_root() + '/ssl/api_braintreegateway_com.ca.crt')

    return send(new_request)


def braintree_verify(request):
    """
    Process Braintree webhooks. This is a pretty simple endpoint that
    assumes the data has already been sanitised and cleaned by the solitude
    server.

    :bt_challenge string: the bt_challenge param sent by Braintree.

    :status 200: contains the string to pass back.

    Any other status is a failure to verify.
    """
    data = request.GET.get('bt_challenge')
    res = WebhookNotificationGateway(BraintreeGateway()).verify(data)
    return HttpResponse(res)


def braintree_parse(request):
    """
    Validate Braintree webhook data. This assumes that solitude has cleaned
    the data. It doesn't actually return any data

    :bt_payload string: the payload from braintree.
    :bt_signature string: the signature that needs to be verified.

    :status 204: the data is to be trusted. Contains no content.

    Any other status is a failure to verify and should not be trusted.
    """
    data = (
        request.POST.get('bt_signature', ''),
        request.POST.get('bt_payload', '')
    )
    try:
        WebhookNotificationGateway(BraintreeGateway()).parse(*data)
    except:
        log.exception('Parse webhook failed')
        return HttpResponse(status=403)

    return HttpResponse(status=204)


def reference(request, reference_name):
    """
    Pass through the request to the reference implementation.
    We have to:
    * get the provider from the URL
    * sign the request with OAuth
    """
    if reference_name not in settings.ZIPPY_CONFIGURATION:
        raise ValueError('Unknown provider: {}'.format(reference_name))

    new_request = prepare(request)
    new_request['url'] = reference_url(request, new_request, reference_name)

    sign_request(
        None,
        settings.ZIPPY_CONFIGURATION[reference_name]['auth'],
        headers=new_request['headers'],
        method=new_request['method'].upper(),
        params={'oauth_token': 'not-implemented'},
        url=new_request['url'])
    return send(new_request)
