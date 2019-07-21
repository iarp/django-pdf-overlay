import datetime
import math


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])


def get_field_data(attribute_name, object_name=None, default=None, **kwargs):

    if object_name:
        if object_name in kwargs:
            tmp = kwargs[object_name]
            if hasattr(tmp, attribute_name):
                return getattr(tmp, attribute_name, default)
            elif isinstance(tmp, dict):
                return tmp[attribute_name]
            return tmp
        return default

    if not kwargs:
        return default

    for tmp in kwargs.values():
        if hasattr(tmp, attribute_name):
            return getattr(tmp, attribute_name, default)
        elif isinstance(tmp, dict) and attribute_name in tmp:
            return tmp[attribute_name]

    return default


def startswith_many(string, items):
    for item in items:
        if string.startswith(item):
            return True


def convert_datetime_objects(obj):
    now = datetime.datetime.now()

    d = obj.lower()
    if startswith_many(d, ['dt:', 'datetime:', 'date:']):
        t, f = obj.split(':', 1)
        return now.strftime(f)

    if obj == 'month_long':
        return now.strftime("%B")
    if obj == 'year_short':
        return str(now.year)[2:]
    if obj == 'day':
        return ordinal(now.day)

    return obj
