# -*- coding: utf-8 -*-
__author__ = 'peter_c_liao'
from datetime import timedelta
from django.utils.timezone import utc
import datetime
import math


class GeoDirection:
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7


class Direction:
    NORTH = 0
    SOUTH = 1
    OTHERS = 2

def get_utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=utc)


def get_local_now():
    return get_utc_now() + timedelta(hours=8)


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


def get_train_direction(geo__direction):
    train_direction = Direction.OTHERS
    if geo__direction in [GeoDirection.N, GeoDirection.NE, GeoDirection.NW, GeoDirection.E]:
        train_direction = Direction.NORTH
    elif geo__direction in [GeoDirection.S, GeoDirection.SE, GeoDirection.SW, GeoDirection.W]:
        train_direction = Direction.SOUTH
    print 'train direction:', train_direction
    return train_direction


def get_train_direction_for_taoyuan_above(geo__direction):
    train_direction = Direction.OTHERS
    if geo__direction in [GeoDirection.N, GeoDirection.NE, GeoDirection.E, GeoDirection.SE]:
        train_direction = Direction.NORTH
    elif geo__direction in [GeoDirection.S, GeoDirection.SW, GeoDirection.W, GeoDirection.NW]:
        train_direction = Direction.SOUTH
    print '[taoyuan above] train direction:', train_direction
    return train_direction


def get_geo_direction_by_moving(lat1, long1, lat2, long2):
    radians = math.atan2((long2 - long1), (lat2 - lat1))
    compassReading = radians * (180 / math.pi);

    coordNames = [GeoDirection.N, GeoDirection.NE, GeoDirection.E, GeoDirection.SE, GeoDirection.S, GeoDirection.SW, GeoDirection.W, GeoDirection.NW, GeoDirection.N]
    coordIndex = int(round(compassReading / 45))
    if coordIndex < 0:
        coordIndex = coordIndex + 8
    print 'geo direction by moving:', coordNames[coordIndex]
    return coordNames[coordIndex]


def get_geo_direction(heading):
    print 'heading:', heading
    geo_direction = GeoDirection.N
    if 0 <= heading <= 22.5 or (360-22.5) < heading <= 360:
        geo_direction = GeoDirection.N
    elif 22.5 < heading <= (45+22.5):
        geo_direction = GeoDirection.NE
    elif (45+22.5) < heading <= (90+22.5):
        geo_direction = GeoDirection.E
    elif (90+22.5) < heading <= (180-22.5):
        geo_direction = GeoDirection.SE
    elif (180-22.5) < heading <= (180+22.5):
        geo_direction = GeoDirection.S
    elif (180+22.5) < heading <= (270-22.5):
        geo_direction = GeoDirection.SW
    elif (270-22.5) < heading <= (270+22.5):
        geo_direction = GeoDirection.W
    elif (270+22.5) < heading <= (360-22.5):
        geo_direction = GeoDirection.NW
    print 'geo direction:', geo_direction
    return geo_direction


def get_train_direction_by_moving(lat1, long1, lat2, long2):
    geo_direction = get_geo_direction_by_moving(lat1, long1, lat2, long2)
    return get_train_direction(geo_direction)


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
    if tdelta.days < 1 and tdelta.seconds < 60:
        return strfdelta(tdelta, "{seconds} 秒")
    elif tdelta.days < 1 and tdelta.seconds < 60*60:
        return strfdelta(tdelta, "{minutes} 分鐘")
    elif tdelta.days < 1:
        return strfdelta(tdelta, "{hours} 小時 {minutes} 分")
    return strfdelta(tdelta, "{days} 天")


def parse_datetime(datetime_str):
    time_list = datetime_str.split(":")
    if len(time_list) < 2:
        return datetime.datetime(1982, 5, 31, 0, 0, tzinfo=utc)
    d = timedelta(hours=int(time_list[0]), minutes = int(time_list[1]))
    d2 = timedelta(hours=get_local_now().hour, minutes=get_local_now().minute)
    today = get_local_now() - d2 + d
    return today
