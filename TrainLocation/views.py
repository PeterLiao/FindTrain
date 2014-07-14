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


class HTTP_STATUS:
    ERROR_SUCCESS = 0
    ERROR_INVALID_DATA = 1
    ERROR_CHECKED_ALREADY = 2
    ERROR_TRAIN_STOPPED = 3
    ERROR_NOT_LOGIN = 4
    ERROR_FIND_NO_TRAIN = 5
    ERROR_UNCHECKED_ALREADY = 6


@csrf_exempt
def show_running_train(request):
    user_id = 0
    if 'user_id' in request.COOKIES:
        user_id = request.COOKIES.get('user_id')
    user = None
    if user_id != 0:
        users = User.objects.filter(fb_id=user_id)
        if users.count() > 0:
            user = users[0]

    direction = Direction.NORTH
    direction_str = request.GET.get('direction')
    if direction_str:
        direction = int(direction_str)
    schedule_list = get_running_train_schedule_by_direction(direction)
    station_list = TrainStation.objects.all().order_by("-latitude")
    schedule_list_ex = []
    for schedule in schedule_list:
        checkins = TrainCheckIn.objects.filter(train=schedule.train)
        checked = False
        if user:
            your_checkins = TrainCheckIn.objects.filter(user=user, train=schedule.train, pub_date__lte=schedule.train.arrive_time, pub_date__gte=schedule.train.departure_time)
            if your_checkins.count() > 0:
                checked = True
        schedule_list_ex.append({"schedule": schedule, "checkins": checkins, "checked": checked})

    return render_to_response("running.html", {"schedule_list": schedule_list,
                                               "direction": direction,
                                               "schedule_list_ex": schedule_list_ex,
                                               "user": user,
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
    user_id = 0
    if 'user_id' in request.COOKIES:
        user_id = request.COOKIES.get('user_id')
    train_number = train_id
    train = Train.objects.filter(train_number=train_number)[0]
    schedule_list = TrainSchedule.objects.filter(train=train)
    station_list = TrainStation.objects.all()
    d = datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc)
    running_schedule_list = TrainSchedule.objects.filter(train=train, arrive_time__gte=get_local_now()).exclude(arrive_time=d).order_by("arrive_time")
    running_schedule = None
    if len(running_schedule_list) > 0:
        running_schedule = running_schedule_list[0]
    if train.direction == Direction.SOUTH:
        station_list = station_list.order_by("-latitude")
    end_station = station_list[len(station_list)-1]
    checkins = TrainCheckIn.objects.filter(train=train)
    checked = False
    user = None
    curr_checkins = TrainCheckIn.objects.filter(train=train, pub_date__lte=train.arrive_time, pub_date__gte=train.departure_time)
    if user_id != 0:
        users = User.objects.filter(fb_id=user_id)
        if users.count() > 0:
            user = users[0]
            your_checkins = TrainCheckIn.objects.filter(user=user, train=train, pub_date__lte=train.arrive_time, pub_date__gte=train.departure_time)
            if your_checkins.count() > 0:
                checked = True

    top_checkins = TrainCheckIn.objects.values('user').annotate(
        checkin_count=models.Count("user")
    ).filter(train=train).order_by("-checkin_count")[:3]

    return render_to_response("train.html", {"schedule_list": schedule_list,
                                             "station_list": station_list,
                                             "train": train,
                                             "end_station": end_station,
                                             "running_schedule": running_schedule,
                                             "user_form": UserForm(),
                                             "checkins": checkins,
                                             "checked": checked,
                                             "top_checkins": top_checkins,
                                             "user": user,
                                             "curr_checkins": curr_checkins,
                                             'top_checkins_range': range(top_checkins.count()),
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

    if err_code != STATUS.ERROR_SUCCESS:
        return render_to_response("where_is_my_train.html",
                                  {"train_form": train_form,
                                   "train_schedule": train_schedule,
                                   "station_list": station_list,
                                   "nearby_station": nearby_station,
                                   "direction": direction,
                                   "err_code": err_code},
                                   context_instance = RequestContext(request))
    else:
        url = '/train/%s/' % train_schedule.train.train_number
        return HttpResponseRedirect(url)


@csrf_exempt
def show_station(request, station_id):
    user_id = 0
    if 'user_id' in request.COOKIES:
        user_id = request.COOKIES.get('user_id')
    user = None
    if user_id != 0:
        users = User.objects.filter(fb_id=user_id)
        if users.count() > 0:
            user = users[0]

    station_id_int = int(station_id)
    station = TrainStation.objects.filter(id=station_id_int)
    direction = Direction.NORTH
    direction_str = request.GET.get('direction')
    if direction_str:
        direction = int(direction_str)
    now = get_utc_now()+timedelta(hours=8)
    schedule_list = TrainSchedule.objects.filter(train_station=station, arrive_time__gte=now, direction=direction)
    station_list = TrainStation.objects.all().order_by("-latitude")

    schedule_list_ex = []
    for schedule in schedule_list:
        checkins = TrainCheckIn.objects.filter(train=schedule.train)
        checked = False
        if user:
            your_checkins = TrainCheckIn.objects.filter(user=user, train=schedule.train, pub_date__lte=schedule.train.arrive_time, pub_date__gte=schedule.train.departure_time)
            if your_checkins.count() > 0:
                checked = True
        schedule_list_ex.append({"schedule": schedule, "checkins": checkins, "checked": checked})

    return render_to_response("station.html", {"schedule_list": schedule_list,
                                               "direction": direction,
                                               "schedule_list_ex": schedule_list_ex,
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


@csrf_exempt
def add_user(request):
    result = HTTP_STATUS.ERROR_INVALID_DATA
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = User(name=form.cleaned_data['name'],
                        fb_id=form.cleaned_data['user_id'],
                        email=form.cleaned_data['email'],
                        pub_date=get_utc_now())
            user.save()
            result = HTTP_STATUS.ERROR_SUCCESS

    response_data = {"result": result}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def add_checkin(request, train_id):
    result = HTTP_STATUS.ERROR_INVALID_DATA
    user_id = 0
    if 'user_id' in request.COOKIES:
        user_id = request.COOKIES.get('user_id')
    if user_id != 0:
        train_list = Train.objects.filter(train_number=train_id)
        if train_list.count() > 0:
            train = train_list[0]
            if not train.is_stopped:
                user_list = User.objects.filter(fb_id=user_id)
                if user_list.count() > 0:
                    user = user_list[0]
                    today_checkin_list = TrainCheckIn.objects.filter(user=user, train=train, pub_date__lte=train.arrive_time, pub_date__gte=train.departure_time)
                    if today_checkin_list.count() == 0:
                        train_checkin = TrainCheckIn(user=user, train=train, pub_date=get_local_now())
                        train_checkin.save()
                        result = HTTP_STATUS.ERROR_SUCCESS
                    else:
                        result = HTTP_STATUS.ERROR_CHECKED_ALREADY
            else:
                result = HTTP_STATUS.ERROR_TRAIN_STOPPED
        else:
            result = HTTP_STATUS.ERROR_FIND_NO_TRAIN
    else:
        result = HTTP_STATUS.ERROR_NOT_LOGIN

    response_data = {"result": result}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def delete_checkin(request, train_id):
    result = HTTP_STATUS.ERROR_INVALID_DATA
    user_id = 0
    if 'user_id' in request.COOKIES:
        user_id = request.COOKIES.get('user_id')
    if user_id != 0:
        train_list = Train.objects.filter(train_number=train_id)
        if train_list.count() > 0:
            train = train_list[0]
            user_list = User.objects.filter(fb_id=user_id)
            if user_list.count() > 0:
                user = user_list[0]
                today_checkin_list = TrainCheckIn.objects.filter(user=user, train=train, pub_date__lte=train.arrive_time, pub_date__gte=train.departure_time)
                if today_checkin_list.count() != 0:
                    train_checkin = today_checkin_list[0]
                    train_checkin.delete()
                    result = HTTP_STATUS.ERROR_SUCCESS
                else:
                    result = HTTP_STATUS.ERROR_UNCHECKED_ALREADY
        else:
            result = HTTP_STATUS.ERROR_FIND_NO_TRAIN
    else:
        result = HTTP_STATUS.ERROR_NOT_LOGIN

    response_data = {"result": result}
    return HttpResponse(json.dumps(response_data), content_type="application/json")