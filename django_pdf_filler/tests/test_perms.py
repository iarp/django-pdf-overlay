import os

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.conf import settings
from django.http.response import HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotAllowed
from django.template.response import TemplateResponse

from django_pdf_filler.models import Document


class TestViewPerms(TestCase):

    def setUp(self):
        self.created_documents = []

        self.user_username = 'testuser'
        self.user_password = '12345'
        self.user = get_user_model().objects.create_user(
            username=self.user_username,
            password=self.user_password,
            email='test@example.com'
        )

        self.staff_username = 'staffuser'
        self.staff_password = '54321'
        self.staff = get_user_model().objects.create_user(
            username=self.staff_username,
            password=self.staff_password,
            email='staff@example.com',
            is_staff=True,
        )

        for perm in Permission.objects.filter(content_type__app_label='django_pdf_filler'):
            self.staff.user_permissions.add(perm)

    def tearDown(self):
        for doc in self.created_documents:
            doc.delete()
        self.client.logout()
        super(TestViewPerms, self).tearDown()

    def login_user(self):
        self.client.login(username=self.user_username, password=self.user_password)

    def login_staff(self):
        self.client.login(username=self.staff_username, password=self.staff_password)

    def create_document(self):
        path_to_file = os.path.join(settings.BASE_DIR, 'django_pdf_filler', 'tests', 'fixtures',
                                    'OHFRowansLawAcknowledgementForm.pdf')
        document = Document(name='Tests Document')
        document.file.save('OHFRowansLawAcknowledgementForm.pdf', open(path_to_file, 'rb'))
        document.generate_page_layout_images(create_layout_images=False)
        self.created_documents.append(document)
        return document

    def get_test_url_patterns(self, document_pk=0, page_pk=0):
        return [
            reverse('django-pdf-filler:index'),
            reverse('django-pdf-filler:create'),
            reverse('django-pdf-filler:document-details', args=[document_pk]),
            reverse('django-pdf-filler:document-delete', args=[document_pk]),
            reverse('django-pdf-filler:document-edit', args=[document_pk]),
            reverse('django-pdf-filler:page-layout', args=[page_pk]),
            reverse('django-pdf-filler:page-fields', args=[page_pk]),
        ]

    def test_views_as_nobody(self):
        for url in self.get_test_url_patterns():
            response = self.client.get(url)
            self.assertIs(HttpResponseRedirect, type(response))

    def test_index_as_permission_denied_user(self):
        self.login_user()
        for url in self.get_test_url_patterns():
            response = self.client.get(url)
            self.assertIs(HttpResponseForbidden, type(response))

    def test_index_as_staff(self):
        self.login_staff()
        doc = self.create_document()
        page = doc.pages.first()

        for url in self.get_test_url_patterns(document_pk=doc.pk, page_pk=page.pk):
            response = self.client.get(url)
            self.assertIs(TemplateResponse, type(response))

        response = self.client.get(reverse('django-pdf-filler:page-fields-copy', args=[page.pk]))
        self.assertIs(HttpResponseNotAllowed, type(response))
