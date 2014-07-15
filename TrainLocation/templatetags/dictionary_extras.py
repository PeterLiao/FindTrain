__author__ = 'peter_c_liao'
from django import template
register = template.Library()

@register.filter(name='get_user')
def get_user(value, arg):
    return value[int(arg)]['user']


@register.filter(name='get_count')
def get_count(value, arg):
    return value[int(arg)]['checkin_count']


@register.filter(name='get_checked')
def get_checked(value, arg):
    checked = False
    for item in value:
        if item['train_number'] == arg:
            checked = item['checked']
            break
    return checked

