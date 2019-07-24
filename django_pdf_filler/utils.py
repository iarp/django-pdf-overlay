import os
import datetime
import math

from django.conf import settings


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])


def get_field_data(attribute_name, object_name=None, default=None, **kwargs):

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
        return tmp

    for tmp in kwargs.values():
        val = get_val(tmp, attribute_name)

        if val is not None:
            return val

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


def get_pdf_to_image_command(path, page_number, image_location):

    path_to_magick_convert = getattr(settings, 'DJANGO_PDF_FILLER_MAGICK_LOCATION', None)
    density = str(getattr(settings, 'DJANGO_PDF_FILLER_MAGICK_DENSITY', 300))

    if path_to_magick_convert:
        assert isinstance(path_to_magick_convert, list), "DJANGO_PDF_FILLER_MAGICK_LOCATION must be of type list"
        cmd_path = path_to_magick_convert
    else:
        cmd_path = ['/usr/bin/convert']
        if os.name == 'nt':
            cmd_path = ['magick.exe', 'convert']

    wanted_page = '{}[{}]'.format(path, page_number)
    commands = cmd_path + ['-density', density, '-flatten', wanted_page, image_location]

    return commands
