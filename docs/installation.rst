Installation
============

Requirements
------------

- Python 2.7, 3.3, 3.4, 3.5, 3.6, 3.7

- Django (1.11+)

- PyPDF2

- reportlab

- django-bootstrap4

- `ImageMagick <https://imagemagick.org/script/download.php>`__

  - Only required if you want auto-generated layout images.
  - If you do not want to or cannot install ImageMagick see `GENERATE_LAYOUT_IMAGE <configuration.html>`__
  - Theres an issue with Imagemagick disallowing PDF interactions, you need to edit the policy.xml file (linux
        location: /etc/ImageMagick-6/policy.xml) and change the line `<policy domain="coder" rights="none" pattern="PDF" />` changing "none" to "read|write".

Django
------

Python package::

    pip install django-pdf-overlay

settings.py::

    INSTALLED_APPS = (
        ...
        'django_pdf_overlay',
        'bootstrap4',
        ...
    )

urls.py::

    urlpatterns = [
        ...
        path('django-pdf-overlay/', include('django_pdf_overlay.urls', namespace='django-pdf-overlay')),
        ...
    ]


Development Settings
--------------------

django-pdf-overlay requires your project to have media settings configured for
the layout images to appear properly.

During development (`DEBUG=True`) that means you may not see the layout image at all.

The settings provided below are meant to be used in development ONLY, do not use these on production!

settings.py::

    if DEBUG:
        MEDIA_URL = '/media/'
        MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

urls.py::

    from django.conf import settings

    if settings.DEBUG:
        from django.urls import re_path
        from django.views.static import serve
        urlpatterns = urlpatterns + [
            re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,}),
        ]


Post-Installation
-----------------

Run migrate to create the necessary tables::

    ./manage.py migrate

Start your server and then head to the Django PDF Overlay
admin area (e.g. http://127.0.0.1:8000/django-pdf-overlay/)

Django PDF Overlay Admin uses built-in django permissions, superusers
will always have full access, everyone else will require permissions.

Create a new group called `PDF Editors` and add the wanted Permissions for
any user added to this group.
