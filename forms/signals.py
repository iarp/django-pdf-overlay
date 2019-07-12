import traceback
from django.db.models.signals import post_save, post_delete

from .models import PDF, PDFPage


def create_page_images_new_pdf(instance: PDF, created, **kwargs):
    print(instance, created)
    if created:
        instance.generate_page_layout_images()
post_save.connect(create_page_images_new_pdf, sender=PDF)


def clean_up_pdf(instance: PDF, **kwargs):
    try:
        instance.file.delete(save=False)
    except:
        pass
post_delete.connect(clean_up_pdf, sender=PDF)


def clean_up_layout_images(instance: PDFPage, **kwargs):
    try:
        instance.image.delete(save=False)
    except:
        pass
post_delete.connect(clean_up_layout_images, sender=PDFPage)
