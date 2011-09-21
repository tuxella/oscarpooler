from django.conf.urls.defaults import *
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       (r'^admin/', include(admin.site.urls)),
                       (r'^j/$', 'journey.views.index'),
                       (r'^j/new/(?P<journey_url>.+)$', 'journey.views.journey_view'),
                       (r'^j/new$', 'journey.views.journey_new'),
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve'),
                       (r'^j/(?P<journey_url>.+)$', 'journey.views.journey_form'),
                       (r'', 'journey.views.index'))
