from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)

from . import forms
from .models import Document, Page


class DocumentListView(PermissionRequiredMixin, ListView):
    model = Document
    permission_required = 'django_pdf_filler.view_document'

    def get_queryset(self):
        return super(DocumentListView, self).get_queryset().order_by('-inserted')


class DocumentCreateView(PermissionRequiredMixin, CreateView):
    model = Document
    form_class = forms.DocumentCreateForm
    permission_required = 'django_pdf_filler.add_document'


class DocumentDetailView(PermissionRequiredMixin, DetailView):
    model = Document
    permission_required = 'django_pdf_filler.view_document'


class DocumentUpdateView(PermissionRequiredMixin, UpdateView):
    model = Document
    form_class = forms.DocumentUpdateForm
    permission_required = 'django_pdf_filler.change_document'


class DocumentDeleteView(PermissionRequiredMixin, DeleteView):
    model = Document
    success_url = reverse_lazy('django-pdf-filler:index')
    permission_required = 'django_pdf_filler.delete_document'


class PageDetailView(PermissionRequiredMixin, DetailView):
    model = Page
    permission_required = 'django_pdf_filler.change_page'

    template_name = 'django_pdf_filler/field_layout.html'

    def post(self, request, **kwargs):
        changeable_fields = ['x', 'y', 'font_size', 'font_color', 'font']
        page = self.get_object()

        for field in page.fields.all():

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


class PageEditView(PermissionRequiredMixin, UpdateView):
    model = Page
    permission_required = 'django_pdf_filler.change_page'
    form_class = forms.PageEditorForm


class PageCopyFieldsView(PermissionRequiredMixin, DetailView):
    model = Page
    http_method_names = ['post']
    permission_required = (
        'django_pdf_filler.change_page',
        'django_pdf_filler.change_field'
    )

    def post(self, request, pk):

        object = self.get_object()  # type: Page

        field_copy_form = forms.FieldsCopyFromDocumentPageForm(data=request.POST)
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


class PageFieldsView(PermissionRequiredMixin, UpdateView):
    model = Page
    permission_required = 'django_pdf_filler.change_field'
    fields = '__all__'

    template_name = 'django_pdf_filler/field_editor.html'

    def get_context_data(self, **kwargs):
        context = super(PageFieldsView, self).get_context_data(**kwargs)

        form = forms.page_fields_formset(
            can_delete=self.request.user.has_perm('django_pdf_filler.delete_field'),
            extra=self.request.user.has_perm('django_pdf_filler.add_field')
        )
        context['formset'] = form(
            data=self.request.POST if self.request.method == 'POST' else None,
            instance=self.object
        )

        context['field_copy_form'] = forms.FieldsCopyFromDocumentPageForm(current_page_id=self.object.pk)
        return context

    def post(self, request, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()

        if context['formset'].is_valid():
            context['formset'].save()

            return redirect(self.get_object().get_fields_editor_url())

        return self.form_invalid(form=None)


class PageRegenerateImageView(PermissionRequiredMixin, DetailView):
    model = Page
    permission_required = 'django_pdf_filler.view_page'

    def get(self, request, *args, **kwargs):
        page = self.get_object()  # type: Page
        page.convert_to_image()
        return redirect(page)
