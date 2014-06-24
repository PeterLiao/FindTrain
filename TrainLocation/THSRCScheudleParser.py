# -*- coding: utf-8 -*-
__author__ = 'peter_c_liao'
import urllib2
import re
import json
from HTMLParser import HTMLParser
from TrainLocation.models import *
from datetime import timedelta
from django.utils.timezone import utc
import datetime
from utils import *

debug = False

class THSRCHTMLParser(HTMLParser):
    schedule_item = {"train_number": "", "train_station": "", "arrive_time": ""}
    schedule_list = []
    in_table = False
    in_tr = False
    in_td = False
    in_train_number = False
    in_train_station = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        if tag == "tr":
            self.in_tr = True
        if tag == "td":
            self.in_td = True
            for key, value in attrs:
                if key == 'title' and self.in_train_number and value != '':
                    self.in_train_station = True
                    if debug:
                        print "train_station:", value
                    self.schedule_item["train_station"] = value
                    break

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
        if tag == "tr":
            self.in_tr = False
            self.in_train_number = False
            self.in_train_station = False
        if tag == "td":
            self.in_td = False

    def handle_data(self, data):
        if self.in_table and self.in_tr and self.in_td:
            if re.search("[0-9]{4}", data):
                self.in_train_number = True
                if debug:
                    print "train_number:", data
                self.schedule_item["train_number"] = data
            elif self.in_train_station:
                if debug:
                    print "arrive_time:", data
                self.schedule_item["arrive_time"] = data
                self.schedule_list.append(self.schedule_item.copy())

    def get_schedule_list(self):
        return self.schedule_list


def get_schedule_list(direction):
    url = 'http://www.thsrc.com.tw/tw/TimeTable/WeeklyTimeTable/1'
    if direction == 0:
        url = 'http://www.thsrc.com.tw/tw/TimeTable/WeeklyTimeTable/0'
    src = urllib2.urlopen(url).read()
    parser = THSRCHTMLParser()
    parser.feed(src)
    return parser.get_schedule_list()


def update_location_info_to_station():
    TrainStation.objects.filter(name=u"台北站").update(latitude=25.047924, longitude=121.517081)
    TrainStation.objects.filter(name=u"板橋站").update(latitude=25.014051, longitude=121.463815)
    TrainStation.objects.filter(name=u"桃園站").update(latitude=25.013093, longitude=121.215217)
    TrainStation.objects.filter(name=u"新竹站").update(latitude=24.808060, longitude=121.040415)
    TrainStation.objects.filter(name=u"台中站").update(latitude=24.112143, longitude=120.616152)
    TrainStation.objects.filter(name=u"嘉義站").update(latitude=23.459565, longitude=120.323320)
    TrainStation.objects.filter(name=u"台南站").update(latitude=22.924928, longitude=120.285720)
    TrainStation.objects.filter(name=u"左營站").update(latitude=22.686927, longitude=120.307827)


def parse_datetime(datetime_str):
    time_list = datetime_str.split(":")
    if len(time_list) < 2:
        return datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc)
    d = timedelta(hours=int(time_list[0]), minutes = int(time_list[1]))
    d2 = timedelta(hours=get_utc_now().hour, minutes=get_utc_now().minute, seconds=get_utc_now().second, microseconds=get_utc_now().microsecond)
    today = datetime.datetime.utcnow().replace(tzinfo=utc) - d2
    return today + d


def add_train_if_not_exist(train_number, direction):
        train_list = Train.objects.filter(train_number=train_number)
        if train_list.count() == 0:
            train = Train(train_number=train_number, direction=direction, pub_date=get_utc_now(), departure_time=get_utc_now(), arrive_time=get_utc_now(), average_speed_in_minute=0.0)
            train.save()
            print 'create new train:', train.train_number


def add_train_station_if_not_exist(name):
        train_station_list = TrainStation.objects.filter(name=name)
        if train_station_list.count() == 0:
            train_station = TrainStation(name=name, pub_date=get_utc_now(), latitude=0.0, longitude=0.0)
            train_station.save()
            print 'create new station:', train_station.name


def get_schedule_list_and_save(direction):
    train_schedule_list = []
    schedule_list = get_schedule_list(direction)
    for item in schedule_list:

        add_train_if_not_exist(item["train_number"], direction)
        train = Train.objects.filter(train_number=item["train_number"])[0]

        add_train_station_if_not_exist(item["train_station"])
        train_station = TrainStation.objects.filter(name=item["train_station"])[0]

        arrive_time = parse_datetime(item["arrive_time"])

        train_schedule_list.append(TrainSchedule(train=train, train_station=train_station, direction=direction, arrive_time=arrive_time,pub_date=get_utc_now()))
        print 'create new schedule:', train.train_number, ',', train_station.name.encode('utf-8'), ',', arrive_time

    TrainSchedule.objects.bulk_create(train_schedule_list)


def download_schedule_and_save():
    TrainSchedule.objects.all().delete()
    get_schedule_list_and_save(0) #北上列車
    get_schedule_list_and_save(1) #南下列車


def calculate_train_info():
    train_list = Train.objects.all()
    for train in train_list:
        d = datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc)
        train_schedule_list = TrainSchedule.objects.filter(train=train).exclude(arrive_time=d).order_by('arrive_time')
        departure_time = train_schedule_list[0].arrive_time
        arrive_time = train_schedule_list[train_schedule_list.count()-1].arrive_time
        dist = get_dist(train_schedule_list[0].train_station.latitude,
                        train_schedule_list[0].train_station.longitude,
                        train_schedule_list[len(train_schedule_list)-1].train_station.latitude,
                        train_schedule_list[len(train_schedule_list)-1].train_station.longitude)
        print 'dist:', dist
        running_time = arrive_time - departure_time
        speed = dist/(running_time.seconds/60.0)
        Train.objects.filter(train_number=train.train_number).update(departure_time=departure_time, arrive_time=arrive_time, average_speed_in_minute=speed)
        print 'update train:', train.train_number, ' departure_time: ', departure_time, ' arrive_time:', arrive_time, ' total_time:', running_time, ' speed:', speed


def get_nearby_station(lat, long):
    nearby_station = TrainStation.objects.filter(name=u"台北站")[0]
    shortest_dist = get_dist(lat, long, nearby_station.latitude, nearby_station.longitude)
    station_list = TrainStation.objects.all()
    for station in station_list:
        dist = get_dist(lat, long, station.latitude, station.longitude)
        if dist < shortest_dist:
            nearby_station = station
            shortest_dist = dist
    return nearby_station


def get_nearby_station_by_specific_station(lat, long, station_list):
    nearby_station = station_list[0]
    shortest_dist = get_dist(lat, long, nearby_station.latitude, nearby_station.longitude)
    for station in station_list:
        dist = get_dist(lat, long, station.latitude, station.longitude)
        if dist < shortest_dist:
            nearby_station = station
            shortest_dist = dist
    return nearby_station


def get_nearby_station_by_direction(lat, long, station_list, direction):
    meet_direction_station_list = []
    nearby_station = station_list[0]
    for station in station_list:
        dir = get_direction_type(lat, long, station.latitude, station.longitude)
        if dir == direction:
            meet_direction_station_list.append(station)
    nearby_station = get_nearby_station_by_specific_station(lat, long, meet_direction_station_list)
    return nearby_station


def get_running_train_schedule():
    running_schedule_list = []
    now = get_utc_now()+timedelta(hours=8)
    print '+8 now is:', now
    train_list = Train.objects.filter(departure_time__lte=now, arrive_time__gte=now)
    for train in train_list:
        schedule_list = TrainSchedule.objects.filter(train=train, arrive_time__gte=now).order_by("arrive_time")
        schedule = schedule_list[0]
        running_schedule_list.append(schedule)
        print 'train:', train.train_number, ' is going to ', schedule.train_station.name.encode('utf-8')
    return running_schedule_list


def get_direction_type(lat1, long1, lat2, long2):
    direction = get_direction(lat1, long1, lat2, long2)
    if direction in ["SE", "S", "SW", "W"]:
        return 1
    else:
        return 0


def get_your_train(lat1, long1, lat2, long2):
    nearby_station = get_nearby_station(lat2, long2)
    nearby_station_direction_type = get_direction_type(get_direction(lat2, long2, nearby_station.latitude, nearby_station.longitude))
    train_direction_type = get_direction_type(lat1, long1, lat2, long2)
    if train_direction_type == 1 and nearby_station_direction_type == 1:
        print 'you are going to ', nearby_station.name
    elif train_direction_type == 1 and nearby_station_direction_type == 0:
        print 'you are leaving from ', nearby_station.name
    elif train_direction_type == 0 and nearby_station_direction_type == 1:
        print 'you are leaving from ', nearby_station.name
    elif train_direction_type == 0 and nearby_station_direction_type == 0:
        print 'you are going to ', nearby_station.name


def get_to_station(lat1, lat2, direction):
    schedule_list = get_running_train_schedule()
    station_list = []
    for schedule in schedule_list:
        station_list.append(schedule.train_station)


def get_station_list_from_schedule(schedule_list):
    station_list = []
    for schedule in schedule_list:
        station_list.append(schedule.train_station)
    return station_list


def get_train_list_from_schedule(schedule_list, station):
    train_list = []
    for schedule in schedule_list:
        if schedule.train_station == station:
            train_list.append(schedule.train)
    return train_list


def get_schedule_list_by_station(schedule_list, station):
    ret_list = []
    for schedule in schedule_list:
        if schedule.train_station == station:
            ret_list.append(schedule)
    return ret_list


def get_your_train(lat1, long1, lat2, long2):
    now = get_utc_now()+timedelta(hours=8)

    direction_type = get_direction_type(lat1, long1, lat2, long2)
    print 'you direction is:', direction_type
    if direction_type == "north":
        return TrainSchedule() # Not support north train so far

    schedule_list = get_running_train_schedule()
    station_list = get_station_list_from_schedule(schedule_list)

    nearby_station = get_nearby_station_by_direction(lat2, long2, station_list, direction_type)
    print 'nearby station is:', nearby_station.name.encode('utf-8')

    dist = get_dist(lat2, long2, nearby_station.latitude, nearby_station.longitude)
    print 'your train is still ', dist, ' away from ', nearby_station.name.encode('utf-8')

    train_list = get_train_list_from_schedule(schedule_list, nearby_station)
    schedule_list = get_schedule_list_by_station(schedule_list, nearby_station)

    you_schedule = schedule_list[0]
    dist_to_nearby_station = ((you_schedule.arrive_time - now).seconds/60) * you_schedule.train.average_speed_in_minute
    diff_between_yours_and_schedule = abs(dist - dist_to_nearby_station)

    for schedule in schedule_list:
        d = ((schedule.arrive_time - now).seconds/60) * schedule.train.average_speed_in_minute
        print 'By train:', schedule.train.train_number, ', to ', schedule.train_station.name.encode('utf-8'), ' it is still ', d, ' away'
        if abs(dist - d) < diff_between_yours_and_schedule:
            you_schedule = schedule
            diff_between_yours_and_schedule = abs(dist - d)

    print 'your train is:', you_schedule.train.train_number
    return you_schedule


