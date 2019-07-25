Installation
============

Requirements
------------

- `ImageMagick <https://imagemagick.org/script/download.php>`__

- Python 2.7, 3.3, 3.4, 3.5, 3.6, 3.7

- Django (1.11+)

- PyPDF2

- reportlab

- django-bootstrap4

Django
------

Python package::

    pip install django-pdf-filler

settings.py::

    INSTALLED_APPS = (
        ...
        'django_pdf_filler',
        ...
    )

urls.py::

    urlpatterns = [
        ...
        url(r'^django-pdf-filler/', include('django_pdf_filler.urls')),
        ...
    ]

Post-Installation
-----------------

Run migrate to create the necessary tables::

    ./manage.py migrate

Start your server and then head to the Django PDF Filler
admin area (e.g. http://127.0.0.1:8000/django-pdf-filler/)

Django PDF Filler Admin uses built-in django permissions, superusers
will always have full access, everyone else will require permissions.

Create a new group called `PDF Editors` and add the wanted Permissions for
any user added to this group.
