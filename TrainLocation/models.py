# -*- coding: utf-8 -*-
from django.db import models
from utils import *

class Weather(models.Model):
    name = models.CharField(max_length=10)
    day_wx = models.CharField(max_length=30)
    night_wx = models.CharField(max_length=30)
    day_maxt = models.IntegerField()
    night_maxt = models.IntegerField()
    day_mint = models.IntegerField()
    night_mint = models.IntegerField()
    day_ci = models.CharField(max_length=30)
    night_ci = models.CharField(max_length=30)
    day_pop = models.IntegerField()
    night_pop = models.IntegerField()
    pub_date = models.DateTimeField('date published')


class Train(models.Model):
    train_number = models.CharField(max_length=4)
    departure_time = models.DateTimeField()
    arrive_time = models.DateTimeField()
    pub_date = models.DateTimeField('date published')
    average_speed_in_minute = models.FloatField()
    direction = models.IntegerField()

    def get_departure_str(self):
        if self.departure_time == datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc):
            return " - "
        else:
            return self.departure_time.strftime("%H:%M")

    def get_arrive_str(self):
        if self.arrive_time == datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc):
            return " - "
        else:
            return self.arrive_time.strftime("%H:%M")

    def get_arrive_timedelta_str(self):
        if self.arrive_time == datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc):
            return " - "
        else:
            return get_formatted_timedelta_by_now(self.arrive_time)

    def is_stopped(self):
        if self.arrive_time >= get_local_now():
            return False
        else:
            return True

    def is_started(self):
        if self.departure_time <= get_local_now():
            return True
        else:
            return False

    def curr_checkins(self):
        return TrainCheckIn.objects.filter(train=self, pub_date__lte=self.arrive_time, pub_date__gte=self.departure_time)

    departure_time_str = property(get_departure_str)
    arrive_time_str = property(get_arrive_str)
    arrive_timedelta_str = property(get_arrive_timedelta_str)
    is_stopped = property(is_stopped)
    is_started = property(is_started)
    curr_checkins = property(curr_checkins)


class TrainStation(models.Model):
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    weather = models.ForeignKey(Weather)
    pub_date = models.DateTimeField('date published')


class TrainSchedule(models.Model):
    train = models.ForeignKey(Train)
    train_station = models.ForeignKey(TrainStation)
    arrive_time = models.DateTimeField()
    pub_date = models.DateTimeField('date published')
    direction = models.IntegerField()
    average_speed_in_minute = models.FloatField()

    def get_arrive_str(self):
        if self.arrive_time == datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc):
            return " - "
        else:
            return self.arrive_time.strftime("%H:%M")

    def get_arrive_timedelta_str(self):
        if self.arrive_time == datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc):
            return " - "
        else:
            return get_formatted_timedelta_by_now(self.arrive_time)

    def is_passed(self):
        if self.arrive_time == datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc):
            return True
        elif self.arrive_time > get_local_now():
            return False
        else:
            return True

    def is_day(self):
        if self.arrive_time.hour in range(6, 18):
            return True
        else:
            return False

    def is_first_station(self):
        invalid_datetime = datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc)
        schedule_list = TrainSchedule.objects.filter(train=self.train).exclude(arrive_time=invalid_datetime).order_by("arrive_time")
        if schedule_list.count() > 0 and schedule_list[0] == self:
            return True
        else:
            return False

    def is_last_station(self):
        invalid_datetime = datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc)
        schedule_list = TrainSchedule.objects.filter(train=self.train).exclude(arrive_time=invalid_datetime).order_by("arrive_time")
        if schedule_list.count() > 0 and schedule_list.last() == self:
            return True
        else:
            return False

    arrive_time_str = property(get_arrive_str)
    arrive_timedelta_str = property(get_arrive_timedelta_str)
    is_day = property(is_day)
    is_passed = property(is_passed)
    is_first_station = property(is_first_station)
    is_last_station = property(is_last_station)


class User(models.Model):
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    email = models.EmailField()
    fb_id = models.IntegerField(primary_key=True)
    pub_date = models.DateTimeField('date published')


class TrainCheckIn(models.Model):
    user = models.ForeignKey(User)
    train = models.ForeignKey(Train)
    pub_date = models.DateTimeField('date published')