from datetime import datetime

from django import template

register = template.Library()


def date_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y, %H:%M:%S")


def verb(v):
    switcher = {"add": "Thêm", "edited": "Sửa", "remove": "Xóa", "hide": "Ẩn"}
    return switcher.get(v, "Unknown")


register.filter(date_time)
register.filter(verb)
