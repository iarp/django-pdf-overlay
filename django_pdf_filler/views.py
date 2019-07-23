from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from django.views.generic import View, ListView, DetailView, CreateView, DeleteView, UpdateView
from django.forms import inlineformset_factory
from django.contrib import messages
from django.db.utils import IntegrityError

from .models import Document, Page, Field
from .forms import DocumentCreateForm, DocumentUpdateForm, FieldEditorForm, FieldsCopyFromDocumentPageForm


class DocumentListView(ListView):
    model = Document

    def get_queryset(self):
        return super().get_queryset().order_by('-inserted')


class DocumentCreateView(CreateView):
    model = Document
    form_class = DocumentCreateForm


class DocumentDetailView(DetailView):
    model = Document


class DocumentUpdateView(UpdateView):
    model = Document
    form_class = DocumentUpdateForm


class DocumentDeleteView(DeleteView):
    model = Document
    success_url = reverse_lazy('django-pdf-filler:index')


class PageDetailView(DetailView):
    model = Page

    template_name = 'django_pdf_filler/field_layout.html'

    def post(self, request, **kwargs):
        changeable_fields = ['x', 'y', 'font_size', 'font_color', 'font']
        page = self.get_object()

        for field in page.fields.all():
            print(field.name, field.pk, field.inserted)

            changed = False

            for f in changeable_fields:
                x = '{}_{}'.format(field.pk, f)

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


class PageCopyFieldsView(DetailView):
    model = Page
    http_method_names = ['post']

    def post(self, request, pk):

        object = self.get_object()  # type: Page

        field_copy_form = FieldsCopyFromDocumentPageForm(data=request.POST)
        if field_copy_form.is_valid():
            selected_page = field_copy_form.cleaned_data['page']

            for field in selected_page.fields.all():

                if field_copy_form.cleaned_data['exclude_matching_fields']:

                    # Ensure field we're about to copy does not already exist on the current page
                    if object.fields.filter(name=field.name).exists():
                        messages.info(request, '{} already exists'.format(field.name))
                        continue

                field.pk = None
                field.page = object
                field.save()
                messages.success(request, '{} successfully copied from "{}"'.format(field.name, selected_page))

        return redirect(object.get_fields_editor_url())


def page_fields(request, pk):
    page = get_object_or_404(Page, pk=pk)

    field_copy_form = FieldsCopyFromDocumentPageForm(current_page_id=page.pk)

    document_fields_formset = inlineformset_factory(
        Page,
        Field,
        form=FieldEditorForm,
        extra=1,
        can_delete=True,
    )
    formset = document_fields_formset(data=request.POST if request.method == 'POST' else None, instance=page)

    if request.method == 'POST' and formset.is_valid():
        formset.save()

        return redirect(page.get_fields_editor_url())

    return render(request, 'django_pdf_filler/field_editor.html', {
        'object': page,
        'formset': formset,
        'field_copy_form': field_copy_form,
    })


class PageRegenerateImageView(DetailView):
    model = Page

    def get(self, request, *args, **kwargs):
        page = self.get_object()  # type: Page
        page.convert_to_image()
        return redirect(page)
