import datetime

from django.test import TestCase


from forms.models import Document, Page, Field
from forms.signals import post_save, create_page_images_new_pdf


class ModelTests(TestCase):

    def setup_test_document(self):
        post_save.disconnect(create_page_images_new_pdf, sender=Document)
        document = Document.objects.create(name='Tests Document')
        post_save.connect(create_page_images_new_pdf, sender=Document)
        Page.objects.create(document=document, number=0)
        Page.objects.create(document=document, number=1)
        return document

    def test_field_default_as_datetime(self):
        f = Field(default='dt:%Y-%m-%d')
        today = datetime.datetime.now()
        self.assertEqual(today.strftime('%Y-%m-%d'), f.get_default())

    def test_field_default_blank(self):
        self.assertEquals('', Field().get_default())

    def test_field_counter(self):
        doc = self.setup_test_document()
        self.assertEqual(0, doc.total_fields_counter)
        del doc.total_fields_counter

        p1 = doc.pages.first()
        p2 = doc.pages.last()

        p1.fields.create(name='p1t1')
        p1.fields.create(name='p1t2')

        self.assertEqual(2, doc.total_fields_counter)
        del doc.total_fields_counter

        p2.fields.create(name='p2t1')
        p2.fields.create(name='p2t2')

        self.assertEqual(4, doc.total_fields_counter)
        del doc.total_fields_counter
