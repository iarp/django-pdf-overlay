from django import forms

from .models import Document, Field


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = '__all__'


class FieldEditorForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ['name', 'default', 'obj_name', 'font_size', 'font', 'font_color']

        help_texts = {
            'obj_name': "object.attribute usage when rending data in the pdf. "
                        "Uses name if obj_name is not supplied. "
                        "See documentation for more information.",
            'default': 'If no value is found, is there a default value you wish '
                       'to supply? See documentation for more options.',
            'font_color': 'hex code of the color you want. You can also supply '
                          'english names of simple colours (red, black, blue... etc)',
            'font': 'The font must be installed on the server if you plan on using a non-standard font',
            'name': 'Must be unique to this page.'
        }
