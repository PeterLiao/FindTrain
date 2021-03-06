#!/usr/bin/env python2.7
__author__ = 'peter_c_liao'

from TrainLocation.THSRCScheudleParser import *
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Fetch today train schedule information from official web site'

    def handle(self, *args, **options):
        print 'download_schedule_and_save..'
        download_schedule_and_save()
        print 'update_location_info_to_station...'
        update_location_info_to_station()
        print 'calculate_train_info...'
        calculate_train_info()
        print 'calculate_train_speed_base_on_each_station...'
        calculate_train_speed_base_on_each_station()
        print 'update_station_weather...'
        update_station_weather()
        print 'update train info finished'