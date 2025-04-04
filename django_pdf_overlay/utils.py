import datetime
import importlib
import math


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])


def import_attribute(path):
    assert isinstance(path, str)
    pkg, attr = path.rsplit('.', 1)
    return getattr(importlib.import_module(pkg), attr)


def get_field_data(attribute_name, default=None, **kwargs):

    object_name = None
    if '.' in attribute_name:
        object_name, attribute_name = attribute_name.split('.', 1)

    def get_val(obj, attr):
        value = None

        if hasattr(obj, attr):
            value = getattr(obj, attr, default)
        elif isinstance(obj, dict) and attr in obj:
            value = obj[attr]

        if callable(value):
            return value()
        return value

    # kwargs is required as well if we're given an object name, ensure the
    # object name wanted was in fact given as a parameter
    if not kwargs or (object_name and object_name not in kwargs):
        return default

    if object_name:
        tmp = kwargs[object_name]

        val = get_val(tmp, attribute_name)
        if val is not None:
            return val
        return default

    for tmp in kwargs.values():
        val = get_val(tmp, attribute_name)

        if val is not None:
            return val

    return default


def convert_datetime_objects(obj):
    now = datetime.datetime.now()

    d = obj.lower()
    if d.startswith(('dt:', 'datetime:', 'date:')):
        t, f = obj.split(':', 1)
        return now.strftime(f)

    # Backwards compatibility reasons
    if obj == 'month_long':
        return now.strftime("%B")
    if obj == 'year_short':
        return str(now.year)[2:]
    if obj == 'day':
        return ordinal(now.day)

    return obj
