import datetime
import os
from PyPDF2 import PdfFileReader

from django.test import TestCase
from django.conf import settings


from django_pdf_filler.models import Document, Page, Field
from django_pdf_filler.signals import post_save, create_page_images_new_pdf


def setup_test_document_no_signal():
    post_save.disconnect(create_page_images_new_pdf, sender=Document)
    document = Document.objects.create(name='Tests Document')
    post_save.connect(create_page_images_new_pdf, sender=Document)
    Page.objects.create(document=document, number=0)
    Page.objects.create(document=document, number=1)
    return document


class ModelTests(TestCase):

    def setUp(self) -> None:
        self.created_documents = []
        super().setUp()

    def tearDown(self) -> None:
        for doc in self.created_documents:
            doc.delete()
        super().tearDown()

    def setup_test_document(self):
        path_to_file = os.path.join(settings.BASE_DIR, 'django_pdf_filler', 'tests', 'fixtures',
                                    'OHFRowansLawAcknowledgementForm.pdf')
        document = Document(name='Tests Document')
        document.file.save('OHFRowansLawAcknowledgementForm.pdf', open(path_to_file, 'rb'))
        self.created_documents.append(document)
        return document

    def test_real_document(self):
        doc = self.setup_test_document()
        self.assertEqual(2, doc.pages.count())
        self.assertEqual(0, doc.total_fields_counter)
        self.assertEqual([], doc._rendered_pages)
        doc.render_pages()
        self.assertEqual(2, len(doc._rendered_pages))
        self.assertEqual(0, doc.times_used)

        file = doc.render_as_document()
        self.assertEqual(1, doc.times_used)
        template_pdf = PdfFileReader(file)
        self.assertEqual(2, template_pdf.getNumPages())

        file = doc.render_as_document(pages=[0])
        self.assertEqual(2, doc.times_used)
        template_pdf = PdfFileReader(file)
        self.assertEqual(1, template_pdf.getNumPages())

        file = doc.render_as_document(pages=[0, 1])
        self.assertEqual(3, doc.times_used)
        template_pdf = PdfFileReader(file)
        self.assertEqual(2, template_pdf.getNumPages())

        file = doc.render_as_document(pages=[])
        self.assertEqual(4, doc.times_used)
        template_pdf = PdfFileReader(file)
        self.assertEqual(0, template_pdf.getNumPages())

    def test_field_default_as_datetime(self):
        f = Field(default='dt:%Y-%m-%d')
        today = datetime.datetime.now()
        self.assertEqual(today.strftime('%Y-%m-%d'), f.get_default())

    def test_field_default_blank(self):
        self.assertEquals('', Field().get_default())

    def test_field_counter(self):
        doc = setup_test_document_no_signal()
        self.assertEqual(0, doc.total_fields_counter)

        p1 = doc.pages.first()
        p2 = doc.pages.last()

        p1.fields.create(name='p1t1')
        p1.fields.create(name='p1t2')
        self.assertEqual(2, doc.total_fields_counter)

        p2.fields.create(name='p2t1')
        p2.fields.create(name='p2t2')
        self.assertEqual(4, doc.total_fields_counter)
