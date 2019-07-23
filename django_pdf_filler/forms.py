from django import forms

from .models import Document, Page, Field


class RegenPageLayouts(forms.ModelForm):

    def save(self, commit=True):
        obj = super(RegenPageLayouts, self).save(commit=commit)
        obj.generate_page_layout_images()
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

    def __init__(self, *args, current_page_id=None, **kwargs):
        super(FieldsCopyFromDocumentPageForm, self).__init__(*args, **kwargs)
        if current_page_id:
            self.fields['page'].queryset = Page.objects.all().exclude(pk=current_page_id)
