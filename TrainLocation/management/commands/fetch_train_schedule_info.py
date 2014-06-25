#!/usr/bin/env python2.7
__author__ = 'peter_c_liao'

from TrainLocation.THSRCScheudleParser import *
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Fetch today train schedule information from official web site'

    def handle(self, *args, **options):
        download_schedule_and_save()
        update_location_info_to_station()
        calculate_train_info()