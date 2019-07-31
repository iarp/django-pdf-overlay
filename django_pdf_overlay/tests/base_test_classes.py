import os

from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model

from django_pdf_overlay.models import Document


class BaseTestClassMethods(TestCase):

    def setUp(self):
        self.created_documents = []
        self.user = self.setup_test_user()
        super(BaseTestClassMethods, self).setUp()

    def tearDown(self):
        for doc in self.created_documents:
            doc.delete()
        super(BaseTestClassMethods, self).tearDown()

    def setup_test_document(self):
        path_to_file = os.path.join(settings.BASE_DIR, 'django_pdf_overlay', 'tests',
                                    'fixtures', 'sample.pdf')
        document = Document(name='Tests Document')
        with open(path_to_file, 'rb') as fo:
            document.file.save('sample.pdf', fo)
        document.setup_document(create_layout_images=False)
        self.created_documents.append(document)

        self.assertEqual(2, document.pages.count())
        self.assertEqual(0, document.total_fields_counter)
        self.assertEqual([], document._rendered_pages)

        return document

    def setup_test_user(self, username='test', password='12345',
                        first_name='John', last_name='Doe',
                        email='john.doe@example.com'):
        return get_user_model().objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
