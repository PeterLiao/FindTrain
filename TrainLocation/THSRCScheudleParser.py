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
import copy
from TrainLocation.weather import *

debug = False


class THSRCHTMLParser(HTMLParser):
    schedule_item = {"train_number": "", "train_station": "", "arrive_time": ""}
    schedule_list = []
    applicable_list = []
    in_table = False
    in_tr = False
    in_td = False
    in_train_number = False
    in_train_station = False
    in_applicable_train = False
    first_applicable_matched_count = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        if tag == "tr":
            self.in_tr = True
        if tag == "td":
            self.in_td = True
            for key, value in attrs:
                if key == 'title' and self.in_train_number:
                    if value != "":
                        self.in_train_station = True
                        self.schedule_item["train_station"] = value
                        if debug:
                            print "train_station:", value
                    else:
                        self.in_train_station = False
                        self.in_applicable_train = True
                        self.first_applicable_matched_count += 1
                    break

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
        if tag == "tr":
            self.in_tr = False
            self.in_train_number = False
            self.in_train_station = False
            self.in_applicable_train = False
            self.first_applicable_matched_count = 0
        if tag == "td":
            self.in_td = False
            self.in_train_station = False
            self.in_applicable_train = False

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
            elif self.in_applicable_train and self.first_applicable_matched_count == 1:
                if debug:
                    print "This train not running today"
                self.applicable_list.append(self.schedule_item["train_number"])

    def get_schedule_list(self):
        return list(self.schedule_list)

    def get_applicable_list(self):
        return list(self.applicable_list)

    def clean_schedule_list(self):
        del self.schedule_list[:]
        del self.applicable_list[:]


def get_schedule_list(direction):
    url = 'http://www.thsrc.com.tw/tw/TimeTable/WeeklyTimeTable/1'
    if direction == Direction.NORTH:
        url = 'http://www.thsrc.com.tw/tw/TimeTable/WeeklyTimeTable/0'
    print url
    src = urllib2.urlopen(url).read()
    parser = THSRCHTMLParser()
    parser.feed(src)
    schedule_list = parser.get_schedule_list()
    applicable_list = parser.get_applicable_list()
    #show_schedule_list(schedule_list)
    parser.clean_schedule_list()
    return [schedule_list, applicable_list]


def update_location_info_to_station():
    TrainStation.objects.filter(name=u"台北站").update(latitude=25.047924, longitude=121.517081)
    TrainStation.objects.filter(name=u"板橋站").update(latitude=25.014051, longitude=121.463815)
    TrainStation.objects.filter(name=u"桃園站").update(latitude=25.013093, longitude=121.215217)
    TrainStation.objects.filter(name=u"新竹站").update(latitude=24.808060, longitude=121.040415)
    TrainStation.objects.filter(name=u"台中站").update(latitude=24.112143, longitude=120.616152)
    TrainStation.objects.filter(name=u"嘉義站").update(latitude=23.459565, longitude=120.323320)
    TrainStation.objects.filter(name=u"台南站").update(latitude=22.924928, longitude=120.285720)
    TrainStation.objects.filter(name=u"左營站").update(latitude=22.686927, longitude=120.307827)


def add_train_if_not_exist(train_number, direction):
        train_list = Train.objects.filter(train_number=train_number)
        if train_list.count() == 0:
            train = Train(train_number=train_number, direction=direction, pub_date=get_utc_now(), departure_time=get_utc_now(), arrive_time=get_utc_now(), average_speed_in_minute=0.0)
            train.save()
            if debug:
                print 'create new train:', train.train_number


def add_train_station_if_not_exist(name):
        train_station_list = TrainStation.objects.filter(name=name)
        if train_station_list.count() == 0:
            weather = get_weather(name)
            train_station = TrainStation(name=name, pub_date=get_utc_now(), latitude=0.0, longitude=0.0, weather=weather)
            train_station.save()
            if debug:
                print 'create new station:', train_station.name


def get_schedule_list_and_save(direction):
    train_schedule_list = []
    result = get_schedule_list(direction)
    schedule_list = result[0]
    applicable_list = result[1]
    for item in schedule_list:

        if item["train_number"] not in applicable_list:
            add_train_if_not_exist(item["train_number"], direction)
            train = Train.objects.filter(train_number=item["train_number"])[0]

            add_train_station_if_not_exist(item["train_station"])
            train_station = TrainStation.objects.filter(name=item["train_station"])[0]

            arrive_time = parse_datetime(item["arrive_time"])

            train_schedule_list.append(TrainSchedule(train=train, train_station=train_station, direction=direction, arrive_time=arrive_time,pub_date=get_utc_now(), average_speed_in_minute=0.0))
            if debug:
                print 'create new schedule:', train.train_number, ',', train_station.name.encode('utf-8'), ',', arrive_time

    TrainSchedule.objects.bulk_create(train_schedule_list)


def download_schedule_and_save():
    TrainSchedule.objects.all().delete()
    get_schedule_list_and_save(Direction.NORTH) #北上列車
    get_schedule_list_and_save(Direction.SOUTH) #南下列車


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


def get_nearby_station_by_specific_station_list(lat, long, station_list):

    nearby_station = station_list[0]
    shortest_dist = get_dist(lat, long, nearby_station.latitude, nearby_station.longitude)
    for station in station_list:
        dist = get_dist(lat, long, station.latitude, station.longitude)
        if dist < shortest_dist:
            nearby_station = station
            shortest_dist = dist
    return nearby_station


def get_running_train_schedule():
    running_schedule_list = []
    now = get_local_now()
    if debug:
        print 'now is:', now
    train_list = Train.objects.filter(departure_time__lte=now, arrive_time__gte=now)
    for train in train_list:
        schedule_list = TrainSchedule.objects.filter(train=train, arrive_time__gte=now).order_by("arrive_time")
        schedule = schedule_list[0]
        running_schedule_list.append(schedule)
        if debug:
            print 'train:', train.train_number, ' is going to ', schedule.train_station.name.encode('utf-8')
    return running_schedule_list



def get_running_train_schedule_by_direction(direction):
    running_schedule_list = []
    now = get_local_now()
    if debug:
        print 'now is:', now
    train_list = Train.objects.filter(departure_time__lte=now, arrive_time__gte=now, direction=direction)
    d = datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc)
    for train in train_list:
        schedule_list = TrainSchedule.objects.filter(train=train, arrive_time__gte=now).exclude(arrive_time=d).order_by("arrive_time")
        if schedule_list.count() > 0:
            schedule = schedule_list[0]
            running_schedule_list.append(schedule)
            if debug:
                print 'train:', train.train_number, ' is going to ', schedule.train_station.name.encode('utf-8')
    return running_schedule_list


def get_running_train_schedule_by_station(station_id):
    running_schedule_list = []
    now = get_local_now()
    if debug:
        print 'now is:', now
    train_list = Train.objects.filter(departure_time__lte=now, arrive_time__gte=now)
    for train in train_list:
        schedule_list = TrainSchedule.objects.filter(train=train, arrive_time__gte=now).order_by("arrive_time")
        schedule = schedule_list[0]
        station = TrainStation.objects.filter(id=station_id)[0]
        if schedule.train_station == station:
            running_schedule_list.append(schedule)
        if debug:
            print 'train:', train.train_number, ' is going to ', schedule.train_station.name.encode('utf-8')
    return running_schedule_list


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


def get_your_train(lat, long, heading):
    print '[start]'
    now = get_utc_now()+timedelta(hours=8)
    geo_direction = get_geo_direction(heading)
    taoyuan_station = TrainStation.objects.filter(name="桃園站")[0]
    geo_direction_between_you_and_station = get_geo_direction_by_moving(lat, long, taoyuan_station.latitude, taoyuan_station.longitude)
    train_direction = Direction.OTHERS
    if geo_direction_between_you_and_station in [GeoDirection.NW, GeoDirection.W, GeoDirection.SW]:
        train_direction = get_train_direction_for_taoyuan_above(geo_direction)
    else:
        train_direction = get_train_direction(geo_direction)
    schedule_list = get_running_train_schedule_by_direction(train_direction)

    ex_schedule_list = []
    for schedule in schedule_list:
        station = schedule.train_station
        station_direction = get_train_direction_by_moving(lat, long, station.latitude, station.longitude)
        if station_direction == train_direction:
            your_dist = get_dist(lat, long, station.latitude, station.longitude)
            time_diff = schedule.arrive_time - now - timedelta(minutes=2)
            if now > (schedule.arrive_time - timedelta(minutes=2)):
                time_diff = timedelta(minutes=1)
            train_dist = schedule.average_speed_in_minute * (time_diff.seconds/60.0)
            dist_diff = abs(your_dist - train_dist)
            print 'you are ', your_dist, ' away from ', station.name.encode('utf-8')
            #if dist_diff < 10.0:
            ex_schedule_list.append([schedule, dist_diff])
            print 'train [', schedule.train.train_number, '] is ', train_dist, ' away from ', station.name.encode('utf-8')
            #else:
            #    print '[> 10km] train [', schedule.train.train_number, '] is ', train_dist, ' away from ', station.name.encode('utf-8')


    if len(ex_schedule_list) == 0:
        print '[warning] no train schedule meet your position and direction'
        return None
    else:
        your_schedule = ex_schedule_list[0][0]
        min_dist_diff = ex_schedule_list[0][1]

        for ex_schedule in ex_schedule_list:
            if ex_schedule[1] < min_dist_diff:
                your_schedule = ex_schedule[0]
                min_dist_diff = ex_schedule[1]

    print '[success] your train is:[', your_schedule.train.train_number, ']'
    return your_schedule

def calculate_train_info():
    train_list = Train.objects.all()
    for train in train_list:
        d = datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc)
        train_schedule_list = TrainSchedule.objects.filter(train=train).exclude(arrive_time=d).order_by('arrive_time')
        if len(train_schedule_list) > 0:
            departure_time = train_schedule_list[0].arrive_time
            arrive_time = train_schedule_list[train_schedule_list.count()-1].arrive_time
            dist = get_dist(train_schedule_list[0].train_station.latitude,
                            train_schedule_list[0].train_station.longitude,
                            train_schedule_list[len(train_schedule_list)-1].train_station.latitude,
                            train_schedule_list[len(train_schedule_list)-1].train_station.longitude)
            if debug:
                print 'dist:', dist
            running_time = arrive_time - departure_time
            speed = dist/(running_time.seconds/60.0)
            Train.objects.filter(train_number=train.train_number).update(departure_time=departure_time, arrive_time=arrive_time, average_speed_in_minute=speed)
            if debug:
                print 'update train:', train.train_number, ' departure_time: ', departure_time, ' arrive_time:', arrive_time, ' total_time:', running_time, ' speed:', speed


def calculate_train_speed_base_on_each_station():
    train_list = Train.objects.all()
    for train in train_list:
        d = datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc)
        train_schedule_list = TrainSchedule.objects.filter(train=train).exclude(arrive_time=d).order_by('arrive_time')
        for i in range(1, len(train_schedule_list)):
            time_diff = train_schedule_list[i].arrive_time - train_schedule_list[i-1].arrive_time - timedelta(minutes=2)
            dist_diff = get_dist(train_schedule_list[i].train_station.latitude,
                                 train_schedule_list[i].train_station.longitude,
                                 train_schedule_list[i-1].train_station.latitude,
                                 train_schedule_list[i-1].train_station.longitude)
            speed = dist_diff/(time_diff.seconds/60.0)
            TrainSchedule.objects.filter(id=train_schedule_list[i].id).update(average_speed_in_minute = speed)
            if debug:
                print 'train:', train.train_number, ' speed is:', speed, ' between ', train_schedule_list[i].train_station.name.encode('utf-8'), ' and ', train_schedule_list[i-1].train_station.name.encode('utf-8')
