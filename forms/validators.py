from PyPDF2 import PdfFileReader
from django.core.exceptions import ValidationError


def validate_pdf(value):

    if not value.name.endswith('.pdf'):
        raise ValidationError('File supplied is not a PDF')

    try:
        PdfFileReader(value)
    except:
        raise ValidationError('File supplied failed to validate as a proper PDF')
