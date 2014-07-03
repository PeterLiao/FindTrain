# -*- coding: utf-8 -*-
from django.db import models
from utils import *


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


    departure_time_str = property(get_departure_str)
    arrive_time_str = property(get_arrive_str)
    arrive_timedelta_str = property(get_arrive_timedelta_str)


class TrainStation(models.Model):
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
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

    arrive_time_str = property(get_arrive_str)
    arrive_timedelta_str = property(get_arrive_timedelta_str)