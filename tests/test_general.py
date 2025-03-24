from django.core.exceptions import ValidationError

from .base_test_classes import BaseTestClassMethods
from django_pdf_overlay import validators


class GeneralTests(BaseTestClassMethods):

    def test_validator_pdf_valid_file(self):
        doc = self.setup_test_document()
        self.assertIsNone(validators.validate_pdf(doc.file))

    def test_validator_pdf_invalid_file(self):

        with self.assertRaises(ValidationError):
            validators.validate_pdf('')

        with self.assertRaises(ValidationError):
            validators.validate_pdf(object)

    def test_validator_pdf_bad_filename(self):
        doc = self.setup_test_document()

        doc.file.name = 'test.jpg'

        with self.assertRaises(ValidationError):
            validators.validate_pdf(doc.file)
