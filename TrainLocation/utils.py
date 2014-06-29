# -*- coding: utf-8 -*-
__author__ = 'peter_c_liao'
from datetime import timedelta
from django.utils.timezone import utc
import datetime
import math


def get_utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=utc)


def utc_to_local(t):
    utc_offset = datetime.datetime.utcnow() - datetime.datetime.now()
    return t - utc_offset


def get_dist(lat1, long1, lat2, long2):

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc * 6373.0


def get_direction(lat1, long1, lat2, long2):
    radians = math.atan2((long2 - long1), (lat2 - lat1))
    compassReading = radians * (180 / math.pi);

    coordNames = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    coordIndex = int(round(compassReading / 45))
    if coordIndex < 0:
        coordIndex = coordIndex + 8
    return coordNames[coordIndex]


def show_schedule_list(schedule_list):
    for item in schedule_list:
        print item["train_number"], ',', item["train_station"], ',', item["arrive_time"]



def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


def get_formatted_timedelta_by_now(date):
    tdelta = date - get_utc_now() - timedelta(hours=8)
    print 'timedelta.days:', tdelta.days , 'timedelta.seconds:', tdelta.seconds
    if tdelta.days < 1 and tdelta.seconds < 60:
        return strfdelta(tdelta, "還有 {seconds} 秒")
    elif tdelta.days < 1 and tdelta.seconds < 60*60:
        return strfdelta(tdelta, "還有 {minutes} 分鐘")
    elif tdelta.days < 1:
        return strfdelta(tdelta, "還有 {hours} 小時 {minutes} 分")
    return strfdelta(tdelta, "還有 {days} 天")