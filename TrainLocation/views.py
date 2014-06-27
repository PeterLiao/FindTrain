# -*- coding: utf-8 -*-
from django.shortcuts import render
import json
from datetime import date, timedelta
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from THSRCScheudleParser import *
from TrainLocation.forms import *
from django.contrib.auth import authenticate, login


@csrf_exempt
def show_running_train(request):
    schedule_list = get_running_train_schedule()
    return render_to_response("running.html", {"schedule_list": schedule_list})


@csrf_exempt
def show_trains_schedule(request, direction_id):
    direction = int(direction_id)
    schedule_list = TrainSchedule.objects.filter(direction=direction)
    station_list = TrainStation.objects.all()
    if direction == Direction.SOUTH:
        station_list = station_list.order_by("-latitude")
    return render_to_response("schedule.html", {"schedule_list": schedule_list,
                                                "station_list": station_list,
                                                "direction_id": direction})

@csrf_exempt
def show_train_schedule(request, train_id):
    train_number = train_id
    train = Train.objects.filter(train_number=train_number)[0]
    schedule_list = TrainSchedule.objects.filter(train=train)
    station_list = TrainStation.objects.all()
    if train.direction == Direction.SOUTH:
        station_list = station_list.order_by("-latitude")
    return render_to_response("schedule.html", {"schedule_list": schedule_list,
                                                "station_list": station_list,
                                                "direction_id": train.direction})

@csrf_exempt
def show_distance_between_station(request):
    station_list = TrainStation.objects.all().order_by("-latitude")
    for x in range(len(station_list)-1):
        print get_dist(station_list[x].latitude, station_list[x].longitude, station_list[x+1].latitude, station_list[x+1].longitude)
        print get_direction(station_list[x].latitude, station_list[x].longitude, station_list[x+1].latitude, station_list[x+1].longitude)
    return HttpResponse('OK')


@csrf_exempt
def show_your_train(request):
    train_form = TrainForm()
    train_schedule = TrainSchedule()
    err_code = 0
    if request.method == 'POST':
        train_form = TrainForm(request.POST)
        if train_form.is_valid():
            lat = float(train_form.cleaned_data['lat'])
            long = float(train_form.cleaned_data['long'])
            heading = float(train_form.cleaned_data['heading'])
            train_schedule = get_your_train(lat, long, heading)
            if train_schedule == None:
                err_code = -1
                train_schedule = TrainSchedule()
    return render_to_response("where_is_my_train.html",
                              {"train_form": train_form,
                               "train_schedule": train_schedule,
                               "err_code": err_code},
                               context_instance = RequestContext(request))
