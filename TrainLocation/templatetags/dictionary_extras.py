__author__ = 'peter_c_liao'
from django import template
register = template.Library()

@register.filter(name='get_user')
def get_user(value, arg):
    return value[int(arg)]['user']


@register.filter(name='get_count')
def get_count(value, arg):
    return value[int(arg)]['checkin_count']