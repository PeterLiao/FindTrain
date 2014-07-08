#!/usr/bin/env python2.7
__author__ = 'peter_c_liao'

from TrainLocation.weather import *
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Fetch today weather information'

    def handle(self, *args, **options):
        import_weather_list()
        update_station_weather()
        print 'update weather finished'