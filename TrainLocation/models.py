from django.db import models
from utils import *


class Train(models.Model):
    train_number = models.CharField(max_length=4)
    departure_time = models.DateTimeField()
    arrive_time = models.DateTimeField()
    pub_date = models.DateTimeField('date published')
    average_speed_in_minute = models.FloatField()

    def get_departure_str(self):
        return self.departure_time.strftime("%H:%M")

    def get_arrive_str(self):
        return self.arrive_time.strftime("%H:%M")

    departure_time_str = property(get_departure_str)
    arrive_time_str = property(get_arrive_str)


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

    def get_arrive_str(self):
        return self.arrive_time.strftime("%H:%M")

    arrive_time_str = property(get_arrive_str)