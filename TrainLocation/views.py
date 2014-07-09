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
from django.shortcuts import redirect

class STATUS:
    ERROR_SUCCESS = 0
    ERROR_FIND_NO_TRAIN = -1
    ERROR_OTHERS = -2


@csrf_exempt
def show_running_train(request):
    direction = Direction.NORTH
    direction_str = request.GET.get('direction')
    if direction_str:
        direction = int(direction_str)
    schedule_list = get_running_train_schedule_by_direction(direction)
    station_list = TrainStation.objects.all().order_by("-latitude")
    return render_to_response("running.html", {"schedule_list": schedule_list,
                                               "direction": direction,
                                               "station_list": station_list})


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
    end_station = station_list[len(station_list)-1]
    return render_to_response("train.html", {"schedule_list": schedule_list,
                                                "station_list": station_list,
                                                "train": train,
                                                "end_station": end_station,
                                                "direction_id": train.direction})

@csrf_exempt
def show_distance_between_station(request):
    station_list = TrainStation.objects.all().order_by("-latitude")
    for x in range(len(station_list)-1):
        print get_dist(station_list[x].latitude, station_list[x].longitude, station_list[x+1].latitude, station_list[x+1].longitude)
        print get_geo_direction_by_moving(station_list[x].latitude, station_list[x].longitude, station_list[x+1].latitude, station_list[x+1].longitude)
    return HttpResponse('OK')


@csrf_exempt
def show_your_train(request):
    train_form = TrainForm()
    train_schedule = TrainSchedule()
    nearby_station = TrainStation()
    err_code = STATUS.ERROR_OTHERS
    direction = Direction.OTHERS

    if request.method == 'POST':
        train_form = TrainForm(request.POST)
        if train_form.is_valid():
            lat = float(train_form.cleaned_data['lat'])
            long = float(train_form.cleaned_data['long'])
            heading = float(train_form.cleaned_data['heading'])
            direction = get_train_direction(get_geo_direction(heading))
            train_schedule = get_your_train(lat, long, heading)
            nearby_station = get_nearby_station(lat, long)
            if train_schedule == None:
                err_code = STATUS.ERROR_FIND_NO_TRAIN
                train_schedule = TrainSchedule()
            else:
                err_code = STATUS.ERROR_SUCCESS

    station_list = TrainStation.objects.all().order_by("-latitude")

    if not STATUS.ERROR_SUCCESS:
        return render_to_response("where_is_my_train.html",
                                  {"train_form": train_form,
                                   "train_schedule": train_schedule,
                                   "station_list": station_list,
                                   "nearby_station": nearby_station,
                                   "direction": direction,
                                   "err_code": err_code},
                                   context_instance = RequestContext(request))
    else:
        url = '/train/%d/' % train_schedule.train.train_number
        return HttpResponseRedirect(url)


@csrf_exempt
def show_station(request, station_id):
    station_id_int = int(station_id)
    station = TrainStation.objects.filter(id=station_id_int)
    direction = Direction.NORTH
    direction_str = request.GET.get('direction')
    if direction_str:
        direction = int(direction_str)
    now = get_utc_now()+timedelta(hours=8)
    schedule_list = TrainSchedule.objects.filter(train_station=station, arrive_time__gte=now, direction=direction)
    station_list = TrainStation.objects.all().order_by("-latitude")
    return render_to_response("station.html", {"schedule_list": schedule_list,
                                               "direction": direction,
                                               "station_list": station_list})


@csrf_exempt
def show_nearby_station(request):
    train_form = TrainForm()
    if request.method == 'POST':
        train_form = TrainForm(request.POST)
        if train_form.is_valid():
            lat = float(train_form.cleaned_data['lat'])
            long = float(train_form.cleaned_data['long'])
            nearby_station = get_nearby_station(lat, long)
            print 'nearby_station:', nearby_station.name.encode('utf-8')
            url = '/station/%d/' % nearby_station.id
            return HttpResponseRedirect(url)
    return render_to_response("nearby.html", {"train_form": train_form}, context_instance = RequestContext(request))


@csrf_exempt
def show_weather(request):
    weather_list = Weather.objects.all()
    return HttpResponse(weather_list)