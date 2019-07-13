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
