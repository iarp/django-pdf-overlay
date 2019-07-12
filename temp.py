import os
from PyPDF2 import PdfFileWriter, PdfFileReader

import django
import inspect

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_pdf.settings")

django.setup()

from forms.models import PDF

# PDF.objects.all().delete()

p = PDF.objects.first()  # type: PDF
template_pdf = PdfFileReader(p.file.file)
page = template_pdf.getPage(0)
print(page)
print(page.mediaBox)

# p.render_pages(something={'keyname': 'test'}, pdf=p)
# p.render_as_document('test.pdf')
# print(type(p.__class__.__name__), p.__class__.__name__)
# print(type(p).__name__, p.__class__.__name__)

# def get_field_data(attribute_name, object_name=None, default=None, **kwargs):
#
#     if object_name:
#         if object_name in kwargs:
#             tmp = kwargs[object_name]
#             if isinstance(tmp, type):
#                 return getattr(tmp, attribute_name, default)
#             elif isinstance(tmp, dict):
#                 return tmp[attribute_name]
#             return tmp
#         return default
#
#     if not kwargs:
#         return default
#
#     for tmp in kwargs.values():
#         if hasattr(tmp, attribute_name):
#             return getattr(tmp, attribute_name, default)
#         elif isinstance(tmp, dict) and attribute_name in tmp:
#             return tmp[attribute_name]
#
#     return default
#
# blahs = {
#     'test': 'here!',
#     'test1': 'blahs',
# }
#
# output = get_field_data(
#     attribute_name='test',
#     object_name='something',
#     something=blahs
# )
# print('output', output)
#
# output = get_field_data(
#     attribute_name='name',
#     something=blahs,
#     PDF=p
# )
# print('output', output)
