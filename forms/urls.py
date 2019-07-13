from django.urls import path

from . import views

app_name = 'forms'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document-index'),
    path('create/', views.DocumentCreateView.as_view(), name='document-create'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document-details'),
    path('<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document-delete'),
    path('<int:document_pk>/<int:pk>/layout/', views.DocumentPageDetailView.as_view(), name='document-page-layout'),
    path('<int:document_pk>/<int:pk>/fields/', views.document_page_fields, name='document-page-fields'),
]
