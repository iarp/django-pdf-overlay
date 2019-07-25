import os

from django.conf import settings


GENERATE_LAYOUT_IMAGE = getattr(settings, 'DJANGO_PDF_FILLER_GENERATE_LAYOUT_IMAGE', True)

LOCAL_DOCUMENT_STORAGE = getattr(
    settings, 'DJANGO_PDF_FILLER_LOCAL_DOCUMENT_STORAGE',
    os.path.join(settings.BASE_DIR, 'media', 'django_pdf_filler', 'documents')
)

MAGICK_DENSITY = str(getattr(settings, 'DJANGO_PDF_FILLER_MAGICK_DENSITY', 300))
MAGICK_FLATTEN = getattr(settings, 'DJANGO_PDF_FILLER_MAGICK_FLATTEN', True)
MAGICK_LOCATION = getattr(settings, 'DJANGO_PDF_FILLER_MAGICK_LOCATION', None)

if MAGICK_LOCATION:
    if isinstance(MAGICK_LOCATION, str):
        MAGICK_LOCATION = [MAGICK_LOCATION]
else:
    MAGICK_LOCATION = ['/usr/bin/convert']
    if os.name == 'nt':
        MAGICK_LOCATION = ['magick.exe', 'convert']

FIELD_VALUE_JOINS = getattr(settings, 'DJANGO_PDF_FILLER_FIELD_VALUE_JOINS', ', .|-_')
FIELD_CHAIN_SPLITTER = getattr(settings, 'DJANGO_PDF_FILLER_FIELD_CHAIN_SPLITTER', '|')
FIELD_DATETIME_SPLITTER = getattr(settings, 'DJANGO_PDF_FILLER_FIELD_DATETIME_SPLITTER', ':')

assert isinstance(FIELD_VALUE_JOINS, (str, list, set, tuple)), \
    "DJANGO_PDF_FILLER_FIELD_VALUE_JOINS must be of type list, set, tuple, or str"
assert FIELD_CHAIN_SPLITTER != FIELD_DATETIME_SPLITTER, \
    "DJANGO_PDF_FILLER_FIELD_CHAIN_SPLITTER and DJANGO_PDF_FILLER_FIELD_DATETIME_SPLITTER cannot be the same value."
assert isinstance(MAGICK_LOCATION, list), \
    "DJANGO_PDF_FILLER_MAGICK_LOCATION must be of type list or str"
