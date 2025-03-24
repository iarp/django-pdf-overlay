from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile
from pypdf import PdfReader


def validate_pdf(value):
    """ Ensure the value supplied is a proper PDF by checking its given extension
        AND whether or not it can be read by PyPDF2

    :param value: FieldFile object of the uploaded file.
    """

    if not isinstance(value, FieldFile):
        raise ValidationError('Object supplied is not a File.')

    if not value.name.endswith('.pdf'):
        raise ValidationError('File supplied is not a PDF')

    try:
        PdfReader(value)
    except: # noqa, bypass bare except
        raise ValidationError('File supplied failed to validate as a proper Document')
