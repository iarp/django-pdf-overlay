import traceback
from django.db.models.signals import post_save, post_delete

from .models import Document, Page


def clean_up_document_on_delete(instance, **kwargs):
    try:
        instance.file.delete(save=False)
    except:
        pass
post_delete.connect(clean_up_document_on_delete, sender=Document)


def clean_up_layout_images_on_delete(instance, **kwargs):
    try:
        instance.image.delete(save=False)
    except:
        pass
post_delete.connect(clean_up_layout_images_on_delete, sender=Page)
