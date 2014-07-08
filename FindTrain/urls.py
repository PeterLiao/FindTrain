from django.conf.urls import patterns, include, url
from TrainLocation.views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^running/', show_running_train),
    url(r'^schedule/(?P<direction_id>[0-9]+)/$', show_trains_schedule),
    url(r'^dist/', show_distance_between_station),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', show_your_train),
    url(r'^train/(?P<train_id>[0-9]+)/$', show_train_schedule),
    url(r'^station/(?P<station_id>[0-9]+)/$', show_station),
    url(r'^nearby/', show_nearby_station),
    url(r'^weather/', show_weather),
)
