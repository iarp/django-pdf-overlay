=============================
Welcome to Django PDF Overlay
=============================

.. image:: https://badge.fury.io/py/django-pdf-overlay.svg
   :target: http://badge.fury.io/py/django-pdf-overlay

.. image:: https://travis-ci.org/iarp/django-pdf-overlay.svg
   :target: https://travis-ci.org/iarp/django-pdf-overlay

.. image:: https://coveralls.io/repos/iarp/django-pdf-overlay/badge.svg?branch=master
   :alt: Coverage Status
   :target: https://coveralls.io/r/iarp/django-pdf-overlay

Source code
  http://github.com/iarp/django-pdf-overlay

Documentation
  https://django-pdf-overlay.readthedocs.io/en/latest/

Overview
========

Designed to make it easy for developers working with PDF's to create views,
pass model data, and have an easy to use GUI for field CRUD and layout.

1. Supply a PDF document in the django-pdf-overlay admin screen.
2. Create fields that match what you need filled out on the document.
3. Using the layout tool, move the fields to their respective locations on the document.
4. In your view, add similar to the following::

    # In this example I will load a user and pass it
    # to the PDF which has user.username as a field.
    from django.contrib.auth import get_user_model
    u = get_user_model().objects.get(pk=1)

    from django_pdf_overlay.models import Document
    doc = Document.objects.get(name='My Document')

    # Here we render the page(s) on the PDF
    doc.render_pages(user=u)

    # You can call render_pages multiple times to generate a single
    # PDF containing multiple copies of the base document.
    u2 = get_user_model().objects.get(pk=2)
    doc.render_pages(user=u2)

    # If you wish to generate an actual file that you can store
    # in a model or somewhere on your system.
    file = doc.render_as_document(filename='users_1_2.pdf')

    # Or if you want the document to auto-download to the user
    return doc.render_as_response(filename='users_1_2.pdf')
