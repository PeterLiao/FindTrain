# -*- coding: utf-8 -*-
from django.shortcuts import render
import json
from datetime import date, timedelta
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from THSRCScheudleParser import *
from TrainLocation.forms import *


def show_running_train(request):
    schedule_list = get_running_train_schedule()
    return render_to_response("running.html", {"schedule_list": schedule_list})


def show_train_schedule(request, direction_id):
    print direction_id
    schedule_list = TrainSchedule.objects.filter(direction=direction_id)
    for item in schedule_list:
        print item.train.train_number
    station_list = TrainStation.objects.all()
    if direction_id == 1:
        station_list = station_list.order_by("-latitude")
    return render_to_response("schedule.html", {"schedule_list": schedule_list,
                                                "station_list": station_list,
                                                "direction_id": int(direction_id)})


def show_distance_between_station(request):
    station_list = TrainStation.objects.all().order_by("-latitude")
    for x in range(len(station_list)-1):
        print get_dist(station_list[x].latitude, station_list[x].longitude, station_list[x+1].latitude, station_list[x+1].longitude)
        print get_direction(station_list[x].latitude, station_list[x].longitude, station_list[x+1].latitude, station_list[x+1].longitude)
    return HttpResponse('OK')


def show_your_train(request):
    train_form = TrainForm()
    train_schedule = TrainSchedule()
    if request.method == 'POST':
        train_form = TrainForm(request.POST)
        if train_form.is_valid():
            lat1 = train_form.cleaned_data['lat1']
            long1 = train_form.cleaned_data['long1']
            lat2 = train_form.cleaned_data['lat2']
            long2 = train_form.cleaned_data['long2']
            train_schedule = get_your_train(lat1, long1, lat2, long2)
    return render_to_response("where_is_my_train.html",
                              {"train_form": train_form,
                               "train_schedule": train_schedule},
                               context_instance = RequestContext(request))
