from django.conf.urls import patterns, include, url
from TrainLocation.views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^running/', show_running_train),
    url(r'^schedule/', show_train_schedule),
    url(r'^dist/', show_distance_between_station),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^train/', show_your_train),
)
