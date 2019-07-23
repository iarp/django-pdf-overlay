import datetime
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
import os
import tempfile
import subprocess
import copy
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.functional import cached_property

from . import validators, utils


class OverwriteFileSystemStore(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        path = os.path.join(self.location, name)
        if os.path.isfile(path):
            os.remove(path)
        return name


BASE_PDF_LOCAL_STORAGE_LOCATION = getattr(
    settings, 'DJANGO_PDF_FILLER_LOCAL_DOCUMENT_STORAGE',
    os.path.join(settings.BASE_DIR, 'media', 'django_pdf_filler', 'documents')
)
local_document_storage = OverwriteFileSystemStore(location=BASE_PDF_LOCAL_STORAGE_LOCATION)


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

            if field.font_color:
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
                data = None

                if field.obj_name:
                    composed_data = []
                    for possible_field in field.obj_name.split(','):
                        if '.' in possible_field:
                            obj, attr_name = possible_field.split('.', 1)
                            data = utils.get_field_data(object_name=obj, attribute_name=attr_name, **kwargs)
                            if data:
                                composed_data.append(data)
                        else:
                            data = utils.get_field_data(attribute_name=possible_field, **kwargs)
                            if data:
                                composed_data.append(data)

                    if composed_data:
                        data = ' '.join(composed_data)

                else:

                    try:
                        obj, attr_name = field.name.split('.', 1)
                        data = utils.get_field_data(object_name=obj, attribute_name=attr_name, **kwargs)
                    except ValueError:
                        data = utils.get_field_data(attribute_name=field.name, **kwargs)

                if data is None:
                    data = field.get_default()

                fields[field] = data

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
        else:
            return temp_file

    def render_as_response(self, filename=None, pages=None):
        file = self.render_as_document(pages=pages)

        if not filename:
            filename = self.file.name

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        response.write(file.read())
        return response

    def generate_page_layout_images(self, create_layout_images=True):
        template_pdf = PdfFileReader(self.file.file)

        existing_pages = set()

        for x in range(template_pdf.getNumPages()):
            _, _, width, height = template_pdf.getPage(x).mediaBox
            page, _ = self.pages.update_or_create(number=x, defaults={
                'width': width,
                'height': height,
            })

            if create_layout_images:
                page.convert_to_image()

            existing_pages.add(page.pk)

        self.pages.all().exclude(pk__in=existing_pages).delete()

    def get_absolute_url(self):
        return reverse('django-pdf-filler:document-details', args=[self.pk])

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
    image = models.FileField(upload_to='django_pdf_filler/layouts/', blank=True, null=True)

    width = models.PositiveIntegerField(default=612)
    height = models.PositiveIntegerField(default=792)

    def __str__(self):
        return '{} Page #{}'.format(self.document, self.number)

    def get_absolute_url(self):
        return reverse('django-pdf-filler:page-layout', args=[self.pk])

    def get_fields_editor_url(self):
        return reverse('django-pdf-filler:page-fields', args=[self.pk])

    def get_fields_layout_url(self):
        return self.get_absolute_url()

    def get_image_regen_url(self):
        return reverse('django-pdf-filler:page-regen-image', args=[self.pk])

    def get_layout_image_url(self):
        try:
            return self.image.url
        except:
            if self.convert_to_image():
                return self.image.url

    def convert_to_image(self):
        filepath_raw, ext = self.document.file.path.rsplit('.', 1)

        if self.image:
            self.image.delete(save=False)

        image_file = '{}_{}.jpg'.format(filepath_raw, self.number)

        commands = utils.get_pdf_to_image_command(
            path=self.document.file.path,
            page_number=self.number,
            image_location=image_file,
        )

        process = subprocess.Popen(commands, stdout=subprocess.PIPE)
        process.wait()

        tmp_image_name, _ = self.document.file.name.rsplit('.', 1)
        image_filename = '{}_{}.jpg'.format(tmp_image_name, self.number)

        if os.path.isfile(image_file):
            with open(image_file, 'rb') as fo:
                self.image.save(image_filename, fo)

            os.remove(image_file)
            return True

        return False


class Field(models.Model):

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='fields')

    name = models.CharField(max_length=255)
    x = models.IntegerField(default=10)
    y = models.IntegerField(default=10)
    default = models.CharField(max_length=255, blank=True)
    system_info = models.CharField(max_length=255, blank=True)

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
