import os

from django.test import TestCase
from django.conf import settings

from django_pdf_overlay.models import Document


class BaseTestClassMethods(TestCase):

    def setUp(self):
        self.created_documents = []
        super(BaseTestClassMethods, self).setUp()

    def tearDown(self):
        for doc in self.created_documents:
            doc.delete()
        super(BaseTestClassMethods, self).tearDown()

    def setup_test_document(self):
        path_to_file = os.path.join(settings.BASE_DIR, 'django_pdf_overlay', 'tests', 'fixtures',
                                    'OHFRowansLawAcknowledgementForm.pdf')
        document = Document(name='Tests Document')
        with open(path_to_file, 'rb') as fo:
            document.file.save('OHFRowansLawAcknowledgementForm.pdf', fo)
        document.setup_document(create_layout_images=False)
        self.created_documents.append(document)

        self.assertEqual(2, document.pages.count())
        self.assertEqual(0, document.total_fields_counter)
        self.assertEqual([], document._rendered_pages)

        return document
