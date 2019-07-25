import os

from django.conf import settings


GENERATE_LAYOUT_IMAGE = getattr(settings, 'DJANGO_PDF_FILLER_GENERATE_LAYOUT_IMAGE', True)

LOCAL_DOCUMENT_STORAGE = getattr(
    settings, 'DJANGO_PDF_FILLER_LOCAL_DOCUMENT_STORAGE',
    os.path.join(settings.BASE_DIR, 'media', 'django_pdf_filler', 'documents')
)

MAGICK_LOCATION = getattr(settings, 'DJANGO_PDF_FILLER_MAGICK_LOCATION', None)
if MAGICK_LOCATION:
    assert isinstance(MAGICK_LOCATION, list), "DJANGO_PDF_FILLER_MAGICK_LOCATION must be of type list"

MAGICK_DENSITY = str(getattr(settings, 'DJANGO_PDF_FILLER_MAGICK_DENSITY', 300))

FIELD_VALUE_JOINS = getattr(settings, 'DJANGO_PDF_FILLER_FIELD_VALUE_JOINS', ', .|-_')
assert isinstance(FIELD_VALUE_JOINS, (str, list, set, tuple)), "DJANGO_PDF_FILLER_FIELD_VALUE_JOINS must be of type list, set, tuple, or str"
