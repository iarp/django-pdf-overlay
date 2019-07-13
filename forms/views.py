from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.forms import inlineformset_factory

from .models import Document, Page, Field
from .forms import DocumentForm, FieldEditorForm


class DocumentListView(ListView):
    model = Document


class DocumentCreateView(CreateView):
    model = Document
    form_class = DocumentForm


class DocumentDetailView(DetailView):
    model = Document


class DocumentDeleteView(DeleteView):
    model = Document
    success_url = reverse_lazy('forms:document-index')


class DocumentPageDetailView(DetailView):
    model = Page

    def post(self, request, **kwargs):
        changeable_fields = ['x', 'y', 'default', 'font_size', 'font_color', 'font']
        page = self.get_object()

        for field in page.fields.all():
            print(field.name, field.pk, field.inserted)

            changed = False

            for f in changeable_fields:
                x = f'{field.pk}_{f}'

                if x in request.POST:

                    fx = request.POST[x]

                    try:
                        fx = int(fx)
                    except (ValueError, TypeError):
                        pass

                    if getattr(field, f) != fx:
                        setattr(field, f, fx)
                        changed = True

            if changed:
                print('saving', field)
                field.save()

        return redirect(self.get_object().get_absolute_url())


def document_page_fields(request, document_pk, pk):
    document = get_object_or_404(Document, pk=document_pk)
    page = get_object_or_404(document.pages.all(), pk=pk)

    document_fields_formset = inlineformset_factory(
        Page,
        Field,
        form=FieldEditorForm,
        extra=2,
        can_delete=True,
    )
    formset = document_fields_formset(data=request.POST if request.method == 'POST' else None, instance=page)

    if request.method == 'POST' and formset.is_valid():
        formset.save()

        return redirect(page.get_fields_editor_url())

    return render(request, 'forms/field_editor.html', {
        'document': document,
        'page': page,
        'formset': formset
    })
