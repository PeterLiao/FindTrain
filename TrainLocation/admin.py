from django.contrib import admin
from TrainLocation.models import *
from THSRCScheudleParser import *

admin.site.register(Train)
admin.site.register(TrainStation)
admin.site.register(TrainSchedule)