import copy
import datetime
import io
import os
import tempfile
import warnings

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.http import HttpResponse
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_str
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas

from . import app_settings, utils, validators
from .commands import get_commands


@deconstructible
class OverwriteFileSystemStore(FileSystemStorage):

    def __init__(self, *args, **kwargs):
        kwargs['location'] = app_settings.LOCAL_DOCUMENT_STORAGE
        super(OverwriteFileSystemStore, self).__init__(*args, **kwargs)

    def get_available_name(self, name, max_length=None):
        path = os.path.join(self.location, name)
        if os.path.isfile(path):
            os.remove(path)
        return name


local_document_storage = OverwriteFileSystemStore()


class Document(models.Model):

    name = models.CharField(max_length=255, unique=True)
    file = models.FileField(storage=local_document_storage, validators=[validators.validate_pdf])

    times_used = models.PositiveIntegerField(default=0)

    inserted = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self._rendered_pages = []

    @staticmethod
    def _render_page(fields):

        packet = io.BytesIO()

        can = canvas.Canvas(packet, pagesize=(612, 792), bottomup=False)

        for field, data in fields.items():

            if field.font_size:
                can.setFont(field.font, field.font_size)
            else:
                can.setFont(field.font, 12)

            if ',' in field.font_color:
                r, g, b = field.font_color.replace(' ', '').split(',', 2)
                can.setFillColorRGB(r, g, b)
            elif field.font_color:
                can.setFillColor(field.font_color)
            else:
                can.setFillColorRGB(0, 0, 0)

            if isinstance(data, datetime.date):
                data = data.strftime('%Y-%m-%d')

            if data is not None:
                can.drawString(field.x, field.y, text=data)

        can.save()

        packet.seek(0)
        return PdfFileReader(packet)

    def render_pages(self, **kwargs):

        for page in self.pages.all():

            fields = {}
            for field in page.fields.all():
                fields[field] = field.process(**kwargs)

            self._rendered_pages.append({
                'template_page_number': page.number,
                'page': self._render_page(fields)
            })

        Document.objects.filter(pk=self.pk).update(times_used=models.F('times_used')+1)
        self.times_used += 1

    def render_as_document(self, filename=None, pages=None):

        output = PdfFileWriter()

        template_pdf = PdfFileReader(self.file.file)

        for page in self._rendered_pages:

            if isinstance(pages, (set, list)) and page['template_page_number'] not in pages:
                continue

            template_page = copy.copy(template_pdf.getPage(page['template_page_number']))
            try:
                template_page.mergePage(page['page'].getPage(0))
            except IndexError:
                pass
            output.addPage(template_page)

        temp_file = tempfile.TemporaryFile()
        output.write(temp_file)
        temp_file.seek(0)

        if filename:
            with open(filename, 'wb') as fw:
                fw.write(temp_file.read())
            temp_file.close()
        else:
            return temp_file

    def render_as_response(self, filename=None, pages=None):
        file = self.render_as_document(pages=pages)

        if not filename:
            filename = self.file.name

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        response.write(file.read())
        file.close()
        return response

    def setup_document(self, create_layout_images=True):
        template_pdf = PdfFileReader(self.file.file)

        existing_pages = set()

        for x in range(template_pdf.getNumPages()):
            _, _, width, height = template_pdf.getPage(x).mediaBox
            page, _ = self.pages.update_or_create(number=x, defaults={
                'width': width,
                'height': height,
            })

            if create_layout_images and app_settings.GENERATE_LAYOUT_IMAGE:
                page.convert_to_image()

            existing_pages.add(page.pk)

        self.pages.all().exclude(pk__in=existing_pages).delete()

    def get_absolute_url(self):
        return reverse('django-pdf-overlay:document-details', args=[self.pk])

    @property
    def total_fields_counter(self):
        c = 0
        for p in self.pages.all():
            c += p.fields.count()
        return c


class Page(models.Model):

    class Meta:
        unique_together = ('document', 'number')
        ordering = ['number']

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='pages')
    number = models.PositiveIntegerField(default=0)
    image = models.FileField(upload_to='django_pdf_overlay/layouts/', blank=True, null=True)

    width = models.PositiveIntegerField(default=612)
    height = models.PositiveIntegerField(default=792)

    inserted = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} Page #{}'.format(self.document, self.number)

    def get_absolute_url(self):
        return reverse('django-pdf-overlay:page-layout', args=[self.pk])

    def get_edit_url(self):
        return reverse('django-pdf-overlay:page-edit', args=[self.pk])

    def get_fields_editor_url(self):
        return reverse('django-pdf-overlay:page-fields', args=[self.pk])

    def get_fields_layout_url(self):
        return self.get_absolute_url()

    def get_image_regen_url(self):
        return reverse('django-pdf-overlay:page-regen-image', args=[self.pk])

    def convert_to_image(self):
        return get_commands().convert_to_image(
            document=self.document,
            page=self
        )


class Field(models.Model):

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='fields')

    name = models.CharField(max_length=255)
    x = models.IntegerField(default=10)
    y = models.IntegerField(default=10)
    default = models.CharField(max_length=255, blank=True)

    obj_name = models.CharField(max_length=255, blank=True)

    font_size = models.IntegerField(default=12)
    font_color = models.CharField(max_length=50, default='black')
    font = models.CharField(max_length=50, default='Helvetica')

    inserted = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}.{}'.format(self.page, self.name)

    def get_default(self, default=''):

        if not self.default:
            return default

        return utils.convert_datetime_objects(self.default)

    def process(self, **kwargs):
        data = None

        # Keep for backwards compatibility
        val = self.obj_name or self.name

        # Due to chaining fields, we need somewhere to store
        # all the values for joining later.
        composed_data = []

        wanted_objects = val.split(app_settings.FIELD_CHAIN_SPLITTER)

        # The last object in the split list may be a join value,
        # check it against what is allowed
        joiner = ' '
        if len(wanted_objects) > 1:
            possible_joiner = wanted_objects[-1]
            if possible_joiner in app_settings.FIELD_VALUE_JOINS:
                wanted_objects = wanted_objects[:-1]
                joiner = possible_joiner

        # Fields can be chained by commas
        for possible_field in wanted_objects:

            try:
                possible_field, dt_format = possible_field.split(app_settings.FIELD_DATETIME_SPLITTER)
            except ValueError:
                dt_format = None

            data = utils.get_field_data(possible_field, **kwargs)

            if isinstance(data, (datetime.datetime, datetime.date, datetime.time)):
                if dt_format:
                    data = data.strftime(dt_format)
                else:
                    data = data.isoformat()
            elif dt_format:
                # If we were supplied with a datetime format but the data is NOT a datetime object, flag a warning.
                msg = 'Field "{}" with obj name "{}" was supplied with a datetime ' \
                      'format of "{}" but type {} was found instead.'
                warnings.warn(msg.format(self.name, possible_field, dt_format, type(data).__name__), SyntaxWarning)

            # We only care for data that exists, do not join on blanks
            if data:
                composed_data.append(force_str(data))

        if composed_data:
            data = joiner.join(composed_data)

        if data is None:
            data = self.get_default()

        return data
