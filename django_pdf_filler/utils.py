import os
import datetime
import math

from django.conf import settings


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
