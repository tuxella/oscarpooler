from django.conf.urls.defaults import *
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       (r'^admin/', include(admin.site.urls)),
                       (r'^journeys/(?P<journey_url>[0-9a-fA-F]+)$', 'journey.views.journey_form'),
                       (r'^journeys/$', 'journey.views.index'),
                       (r'^journeys/new$', 'journey.views.journey_new'),
                       (r'^journeys/new/(?P<journey_url>[0-9a-fA-F]+)/$', 'journey.views.journey_view'),
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve'),
                       (r'', 'journey.views.index')
)
