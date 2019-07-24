from django.conf.urls import url

from . import views

app_name = 'django_pdf_filler'

urlpatterns = [
    url(r'^$', views.DocumentListView.as_view(), name='index'),
    url(r'^create/$', views.DocumentCreateView.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/$', views.DocumentDetailView.as_view(), name='document-details'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.DocumentDeleteView.as_view(), name='document-delete'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.DocumentUpdateView.as_view(), name='document-edit'),
    url(r'^page/(?P<pk>[0-9]+)/edit/$', views.PageEditView.as_view(), name='page-edit'),
    url(r'^page/(?P<pk>[0-9]+)/layout/$', views.PageDetailView.as_view(), name='page-layout'),
    url(r'^page/(?P<pk>[0-9]+)/fields/$', views.PageFieldsView.as_view(), name='page-fields'),
    url(r'^page/(?P<pk>[0-9]+)/fields/copy/$', views.PageCopyFieldsView.as_view(), name='page-fields-copy'),
    url(r'^page/(?P<pk>[0-9]+)/regen-image/$', views.PageRegenerateImageView.as_view(), name='page-regen-image'),
]
