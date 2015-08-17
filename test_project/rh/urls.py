from django.conf.urls import patterns, url

urlpatterns = patterns('rh.views',
    url('^$', 'lista'),
    url(r'^(?P<funcionario_id>\w{0,50})$', 'individual'),
)
