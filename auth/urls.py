from django.conf.urls import include, patterns, url

urlpatterns = patterns(
    '',
    url('^v1/provider/', include('provider.urls', namespace='provider'))
)
