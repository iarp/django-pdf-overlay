import datetime
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
import os
import math
import tempfile
import subprocess
import copy
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.auth.models import User

from . import validators

ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])

BASE_PDF_LOCAL_STORAGE_LOCATION = os.path.join(settings.BASE_DIR, 'forms', 'pdf-base')
fs = FileSystemStorage(location=BASE_PDF_LOCAL_STORAGE_LOCATION)


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


class PDF(models.Model):

    class Meta:
        verbose_name = 'PDF'
        verbose_name_plural = 'PDFs'

    name = models.CharField(max_length=255, unique=True)
    file = models.FileField(storage=fs, validators=[validators.validate_pdf])

    inserted = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
                data = field.get_default()

                if field.obj_name:
                    composed_data = []
                    for possible_field in field.obj_name.split(','):
                        if '.' in possible_field:
                            obj, attr_name = possible_field.split('.', 1)
                            data = get_field_data(object_name=obj, attribute_name=attr_name, default=data, **kwargs)
                            if data:
                                composed_data.append(data)
                        else:
                            data = get_field_data(attribute_name=possible_field, default=data, **kwargs)
                            if data:
                                composed_data.append(data)

                    data = ' '.join(composed_data)

                else:

                    try:
                        obj, attr_name = field.name.split('.', 1)
                        data = get_field_data(object_name=obj, attribute_name=attr_name, default=data, **kwargs)
                    except ValueError:
                        data = get_field_data(attribute_name=field.name, default=data, **kwargs)

                fields[field] = data

            self._rendered_pages.append({
                'template_page_number': page.number,
                'page': self._render_page(fields)
            })

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

    def render_as_response(self, filename, pages=None):
        file = self.render_as_document(pages=pages)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(file.read())
        return response

    def generate_page_layout_images(self):
        template_pdf = PdfFileReader(self.file.file)

        for x in range(template_pdf.getNumPages()):
            page, _ = self.pages.get_or_create(number=x)
            page.convert_to_image(force=True)


class PDFPage(models.Model):

    class Meta:
        unique_together = ('pdf', 'number')
        ordering = ['number']

    pdf = models.ForeignKey(PDF, on_delete=models.CASCADE, related_name='pages')
    number = models.PositiveIntegerField(default=0)
    image = models.FileField(upload_to='forms/layouts/', blank=True, null=True)

    def get_layout_image(self):
        try:
            return self.image.url
        except:
            if self.convert_to_image():
                return self.image.url

    def convert_to_image(self, force=False):
        filepath_raw, ext = self.pdf.file.path.rsplit('.', 1)

        if not force and self.image:
            return True

        image_file = f'{filepath_raw}_{self.number}.jpg'

        cmd_path = ['/usr/bin/convert']
        if os.name == 'nt':
            cmd_path = ['magick.exe', 'convert']

        commands = cmd_path + ['-density', '300', '-flatten', f'{self.pdf.file.path}[{self.number}]', image_file]

        process = subprocess.Popen(commands, stdout=subprocess.PIPE)
        process.wait()

        tmp_image_name = self.pdf.file.name.rsplit('.', 1)
        image_filename = f'{tmp_image_name[0]}_{self.number}.jpg'

        if os.path.isfile(image_file):
            with open(image_file, 'rb') as fo:
                self.image.save(image_filename, fo)

            os.remove(image_file)
            return True

        return False


class PDFField(models.Model):

    class Meta:
        unique_together = ('page', 'name')

    page = models.ForeignKey(PDFPage, on_delete=models.CASCADE, related_name='fields')

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

    # The user can change the x and y all they want, but if something goes wrong
    # and they want to restore to defaults, need to store those somewhere...
    system_default_x = models.IntegerField(default=10)
    system_default_y = models.IntegerField(default=10)

    def get_default(self):
        if not self.default:
            return ''

        now = datetime.datetime.now()

        if self.default == 'month_long':
            return now.strftime("%B")
        if self.default == 'year_short':
            return str(now.year)[2:]
        if self.default == 'day':
            return ordinal(now.day)

        return self.default

