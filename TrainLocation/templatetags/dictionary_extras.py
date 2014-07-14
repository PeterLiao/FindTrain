__author__ = 'peter_c_liao'
from django import template
register = template.Library()

@register.filter(name='get_user')
def get_user(value, arg):
    return value[int(arg)]['user']


@register.filter(name='get_count')
def get_count(value, arg):
    return value[int(arg)]['checkin_count']


@register.filter(name='get_list_count_by_index')
def get_list_count_by_index(value, arg):
    checkins =  value[int(arg)]
    return checkins.count()

