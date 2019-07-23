from django.urls import path

from . import views

app_name = 'django_pdf_filler'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='index'),
    path('create/', views.DocumentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document-details'),
    path('<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document-delete'),
    path('<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document-edit'),
    path('page/<int:pk>/layout/', views.PageDetailView.as_view(), name='page-layout'),
    path('page/<int:pk>/fields/', views.page_fields, name='page-fields'),
    path('page/<int:pk>/fields/copy/', views.PageCopyFieldsView.as_view(), name='page-fields-copy'),
    path('page/<int:pk>/regen-image/', views.PageRegenerateImageView.as_view(), name='page-regen-image'),
]
