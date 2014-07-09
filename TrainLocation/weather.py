# -*- coding: utf-8 -*-
__author__ = 'peter_c_liao'

from xml.dom import minidom
import urllib2
from TrainLocation.models import *

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def import_weather_list():
    Weather.objects.all().delete()
    weather_list = []
    src = urllib2.urlopen('http://opendata.cwb.gov.tw/opendata/MFC/F-C0032-001.xml').read()
    xml_doc = minidom.parseString(src)
    item_list = xml_doc.getElementsByTagName('location')
    for item in item_list:
        new_weather = Weather()
        name = getText(item.getElementsByTagName("name")[0].childNodes)
        new_weather.name = name
        new_weather.pub_date = get_utc_now()
        weathers = item.getElementsByTagName("weather-elements")[0].childNodes
        for weather in weathers:
            #今日天氣
            if weather.nodeName == 'Wx':
                #白天氣候
                day_wx = getText(weather.childNodes[1].childNodes[1].childNodes)
                #夜晚氣候
                night_wx = getText(weather.childNodes[3].childNodes[1].childNodes)
                new_weather.day_wx = day_wx
                new_weather.night_wx = night_wx
            if weather.nodeName == 'MaxT':
                #白天高溫
                day_maxt = getText(weather.childNodes[1].childNodes[1].childNodes)
                #夜晚高溫
                night_maxt = getText(weather.childNodes[3].childNodes[1].childNodes)
                new_weather.day_maxt = int(day_maxt)
                new_weather.night_maxt = int(night_maxt)
            if weather.nodeName == 'MinT':
                #白天低溫
                day_mint = getText(weather.childNodes[1].childNodes[1].childNodes)
                #夜晚低溫
                night_mint = getText(weather.childNodes[3].childNodes[1].childNodes)
                new_weather.day_mint = int(day_mint)
                new_weather.night_mint = int(night_mint)
            if weather.nodeName == 'CI':
                #白天舒適度
                day_ci = getText(weather.childNodes[1].childNodes[1].childNodes)
                #夜晚舒適度
                night_ci = getText(weather.childNodes[3].childNodes[1].childNodes)
                new_weather.day_ci = day_ci
                new_weather.night_ci = night_ci

        weather_list.append(new_weather)
    Weather.objects.bulk_create(weather_list)


def get_weather(station_name):
    weather = Weather()
    station_list = TrainStation.objects.all()
    if station_name == "台北站":
        weather = Weather.objects.filter(name=u"臺北市")[0]
    elif station_name == "板橋站":
        weather = Weather.objects.filter(name=u"新北市")[0]
    elif station_name == "桃園站":
        weather = Weather.objects.filter(name=u"桃園縣")[0]
    elif station_name == "新竹站":
        weather = Weather.objects.filter(name=u"新竹市")[0]
    elif station_name == "台中站":
        weather = Weather.objects.filter(name=u"臺中市")[0]
    elif station_name == "嘉義站":
        weather = Weather.objects.filter(name=u"嘉義市")[0]
    elif station_name == "台南站":
        weather = Weather.objects.filter(name=u"臺南市")[0]
    elif station_name == "左營站":
        weather = Weather.objects.filter(name=u"高雄市")[0]
    return weather

def update_station_weather():
    station_list = TrainStation.objects.all()
    for station in station_list:
        if station.name == u"台北站":
            weather = Weather.objects.filter(name=u"臺北市")[0]
            TrainStation.objects.filter(name=u"台北站").update(weather=weather)
        elif station.name == u"板橋站":
            weather = Weather.objects.filter(name=u"新北市")[0]
            TrainStation.objects.filter(name=u"板橋站").update(weather=weather)
        elif station.name == u"桃園站":
            weather = Weather.objects.filter(name=u"桃園縣")[0]
            TrainStation.objects.filter(name=u"桃園站").update(weather=weather)
        elif station.name == u"新竹站":
            weather = Weather.objects.filter(name=u"新竹市")[0]
            TrainStation.objects.filter(name=u"新竹站").update(weather=weather)
        elif station.name == u"台中站":
            weather = Weather.objects.filter(name=u"臺中市")[0]
            TrainStation.objects.filter(name=u"台中站").update(weather=weather)
        elif station.name == u"嘉義站":
            weather = Weather.objects.filter(name=u"嘉義市")[0]
            TrainStation.objects.filter(name=u"嘉義站").update(weather=weather)
        elif station.name == u"台南站":
            weather = Weather.objects.filter(name=u"臺南市")[0]
            TrainStation.objects.filter(name=u"台南站").update(weather=weather)
        elif station.name == u"左營站":
            weather = Weather.objects.filter(name=u"高雄市")[0]
            TrainStation.objects.filter(name=u"左營站").update(weather=weather)

