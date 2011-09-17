from django.conf.urls.defaults import *
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       (r'^admin/', include(admin.site.urls)),
                       (r'^journeys/(?P<journey_id>\d+)/$', 'journey.views.journey_detail'),
                       (r'/journeys/(?P<journey_id>\d+)/edit$', 'journey.views.journey_form'),
                       (r'^journeys/json/(?P<journey_id>\d+)/$', 'journey.views.journey_json'),
                       (r'/journeys/$', 'journey.views.index'),
                       (r'/journeys/new$', 'journey.views.journey_new'),
                       (r'/journeys/new/(?P<journey_id>\d+)/$', 'journey.views.journey_view'),
                       (r'^j/(?P<journey_url>\.+)/$', 'journey.views.journey_detail_from_url'),
                       (r'^peoples/new$', 'journey.views.people_new'),
                       (r'^peoples/json/(?P<people_id>\d+)/$', 'journey.views.people_json'),
                       (r'^vehicles/json/(?P<vehicle_id>\d+)/$', 'journey.views.vehicle_json'),
                       (r'^test$', 'journey.views.ootest'),
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve')
)
