from django.db.models.signals import post_delete

from .models import Document, Page


def clean_up_document_on_delete(instance, **kwargs):
    try:
        if instance.file:
            instance.file.delete(save=False)
    except:  # noqa, bypass bare except
        pass


post_delete.connect(clean_up_document_on_delete, sender=Document)


def clean_up_layout_images_on_delete(instance, **kwargs):
    try:
        if instance.image:
            instance.image.delete(save=False)
    except:  # noqa, bypass bare except
        pass


post_delete.connect(clean_up_layout_images_on_delete, sender=Page)
