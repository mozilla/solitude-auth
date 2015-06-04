from base64 import encodestring as encodebytes

from django.conf import settings
from lxml import etree

from utils import prepare, send

from braintree.environment import Environment


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


def reference(request):
    raise NotImplementedError
