from django.conf.urls import patterns, url

from provider import views

urlpatterns = patterns(
    '',
    url('^bango', views.bango, name='bango'),
    url('^braintree', views.braintree, name='braintree'),
    url('^reference', views.reference, name='reference')
)
