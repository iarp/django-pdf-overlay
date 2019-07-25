import datetime
import os
from PyPDF2 import PdfFileReader

from django.test import TestCase
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from django_pdf_filler.models import Document, Page, Field


class ModelTests(TestCase):

    def setUp(self):
        self.created_documents = []
        super(ModelTests, self).setUp()

    def tearDown(self):
        for doc in self.created_documents:
            doc.delete()
        super(ModelTests, self).tearDown()

    def setup_test_document(self):
        path_to_file = os.path.join(settings.BASE_DIR, 'django_pdf_filler', 'tests', 'fixtures',
                                    'OHFRowansLawAcknowledgementForm.pdf')
        document = Document(name='Tests Document')
        with open(path_to_file, 'rb') as fo:
            document.file.save('OHFRowansLawAcknowledgementForm.pdf', fo)
        document.generate_page_layout_images(create_layout_images=False)
        self.created_documents.append(document)

        self.assertEqual(2, document.pages.count())
        self.assertEqual(0, document.total_fields_counter)
        self.assertEqual([], document._rendered_pages)

        return document

    def test_document_single_render_limited_to_certain_pages(self):
        doc = self.setup_test_document()
        doc.render_pages()
        self.assertEqual(2, len(doc._rendered_pages))

        file = doc.render_as_document()
        template_pdf = PdfFileReader(file)
        self.assertEqual(2, template_pdf.getNumPages())

        file = doc.render_as_document(pages=[0])
        template_pdf = PdfFileReader(file)
        self.assertEqual(1, template_pdf.getNumPages())

        file = doc.render_as_document(pages=[0, 1])
        template_pdf = PdfFileReader(file)
        self.assertEqual(2, template_pdf.getNumPages())

        file = doc.render_as_document(pages=[])
        template_pdf = PdfFileReader(file)
        self.assertEqual(0, template_pdf.getNumPages())

    def test_document_multi_render_limited_to_certain_pages(self):
        doc = self.setup_test_document()

        doc.render_pages()
        self.assertEqual(2, len(doc._rendered_pages))
        doc.render_pages()
        self.assertEqual(4, len(doc._rendered_pages))

        file = doc.render_as_document()
        template_pdf = PdfFileReader(file)
        self.assertEqual(4, template_pdf.getNumPages())

        file = doc.render_as_document(pages=[0])
        template_pdf = PdfFileReader(file)
        self.assertEqual(2, template_pdf.getNumPages())

        file = doc.render_as_document(pages=[0, 1])
        template_pdf = PdfFileReader(file)
        self.assertEqual(4, template_pdf.getNumPages())

        file = doc.render_as_document(pages=[])
        template_pdf = PdfFileReader(file)
        self.assertEqual(0, template_pdf.getNumPages())

    def test_document_used_counter(self):
        doc = self.setup_test_document()
        self.assertEqual(0, doc.times_used)

        doc.render_pages()
        self.assertEqual(1, doc.times_used)

        doc.render_as_document().close()
        self.assertEqual(1, doc.times_used)

        doc.render_as_response()
        self.assertEqual(1, doc.times_used)

        doc.render_pages()
        self.assertEqual(2, doc.times_used)

    def test_document_render_multipage(self):
        doc = self.setup_test_document()

        doc.render_pages()
        self.assertEqual(2, len(doc._rendered_pages))

        doc.render_as_document().close()
        self.assertEqual(2, len(doc._rendered_pages))

        doc.render_as_response()
        self.assertEqual(2, len(doc._rendered_pages))

        doc.render_pages()
        self.assertEqual(4, len(doc._rendered_pages))

    def test_document_render_as_response_is_valid(self):
        doc = self.setup_test_document()

        response = doc.render_as_response(filename='tests.pdf')

        self.assertIs(type(response), HttpResponse)
        self.assertEqual('attachment; filename="tests.pdf"', response['Content-Disposition'])
        self.assertEqual('application/pdf', response['Content-Type'])

    def test_field_default_as_datetime(self):
        f = Field(default='dt:%Y-%m-%d')
        today = datetime.datetime.now()
        self.assertEqual(today.strftime('%Y-%m-%d'), f.get_default())

    def test_field_default_blank(self):
        self.assertEqual('', Field().get_default())

    def test_field_counter(self):
        doc = self.setup_test_document()

        p1 = doc.pages.first()
        p2 = doc.pages.last()

        p1.fields.create(name='p1t1')
        p1.fields.create(name='p1t2')
        self.assertEqual(2, doc.total_fields_counter)

        p2.fields.create(name='p2t1')
        p2.fields.create(name='p2t2')
        self.assertEqual(4, doc.total_fields_counter)

    def test_field_process(self):
        user = get_user_model().objects.create_user(
            username='test',
            password='12345',
            first_name='John',
            last_name='Doe',
            email='test@example.com'
        )
        field = Field(
            name='FullName',
            obj_name='user.first_name|user.last_name'
        )
        self.assertEqual('John Doe', field.process(user=user))

        field.obj_name = 'user.first_name|user.last_name|,'
        self.assertEqual('John,Doe', field.process(user=user))

        field.obj_name = 'user.first_name|user.last_name|b'
        self.assertEqual('John Doe', field.process(user=user))

        field.obj_name = 'user.date_joined:%Y-%m-%d'
        self.assertEqual(user.date_joined.strftime('%Y-%m-%d'), field.process(user=user))

        field.obj_name = 'user.date_joined:%Y-%m-%d|user.first_name|user.last_name'
        self.assertEqual('{} John Doe'.format(user.date_joined.strftime('%Y-%m-%d')), field.process(user=user))
