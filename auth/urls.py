from django.conf.urls import include, patterns, url

braintree = patterns(
    'auth.views',
    url('^$', 'braintree', name='auth'),
    url('^/verify$', 'braintree_verify', name='verify'),
    url('^/parse$', 'braintree_parse', name='parse'),
)

urlpatterns = patterns(
    'auth.views',
    url('^v1/bango$', 'bango', name='bango'),
    url('^v1/braintree', include(braintree, namespace='braintree')),
    url('^v1/reference/(?P<reference_name>\w+)/', 'reference',
        name='reference'),
)
