from django import forms

from .models import Document, Page, Field
from django_pdf_filler import app_settings


class RegenPageLayouts(forms.ModelForm):

    def save(self, commit=True):
        obj = super(RegenPageLayouts, self).save(commit=commit)
        obj.setup_document()
        return obj


class DocumentCreateForm(RegenPageLayouts):
    class Meta:
        model = Document
        fields = ['name', 'file']

    name = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(DocumentCreateForm, self).clean()

        if not cleaned_data.get('name') and cleaned_data.get('file'):
            cleaned_data['name'] = cleaned_data['file'].name.replace('.pdf', '')

        return cleaned_data


class DocumentUpdateForm(RegenPageLayouts):
    class Meta:
        model = Document
        fields = ['file']


def split_and_strip(value):
    # Check if the value supplied is permitted to have a whitespace at the end.
    if not value.strip():
        return ''
    split_values = value.split(app_settings.FIELD_CHAIN_SPLITTER)

    # Only 1 value in the split means the last character is not
    # a possible joiner to be used in field rendering.
    if len(split_values) <= 1:
        return value.strip()

    # However if the last item in the list is NOT a possible field value joiner, then just strip
    elif split_values[-1] not in app_settings.FIELD_VALUE_JOINS:
        return value.strip()

    return value


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
        }

    name = forms.CharField(strip=False, required=True)
    obj_name = forms.CharField(strip=False, required=False)

    def clean_obj_name(self):
        return split_and_strip(self.cleaned_data['obj_name'])

    def clean_name(self):
        return split_and_strip(self.cleaned_data['name'])


def page_fields_formset(can_delete=True, extra=1, **kwargs):
    return forms.inlineformset_factory(
        Page,
        Field,
        form=FieldEditorForm,
        extra=extra,
        can_delete=can_delete,
        **kwargs
    )


class FieldsCopyFromDocumentPageForm(forms.Form):
    page = forms.ModelChoiceField(Page.objects.all())

    exclude_matching_fields = forms.BooleanField(
        initial=True,
        help_text='Do not import fields from selected Page where field name exists in the current page.',
        required=False
    )

    def __init__(self, current_page_id=None, *args, **kwargs):
        super(FieldsCopyFromDocumentPageForm, self).__init__(*args, **kwargs)
        if current_page_id:
            self.fields['page'].queryset = Page.objects.all().exclude(pk=current_page_id)
