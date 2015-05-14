from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url('^v1/bango$', 'auth.views.bango', name='bango'),
    url('^v1/braintree$', 'auth.views.braintree', name='braintree'),
    url('^v1/reference$', 'auth.views.reference', name='reference')
)
