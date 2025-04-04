VERSION = (2025, 3, 24, "alpha", 0)

__title__ = 'django-pdf-overlay'
__version_info__ = VERSION
__version__ = '.'.join(map(str, VERSION[:3])) + ('-{}{}'.format(
    VERSION[3], VERSION[4] or '') if VERSION[3] != 'final' else '')
__author__ = 'IARP'
__license__ = 'MIT'
__copyright__ = 'Copyright 2019 IARP and contributors'

default_app_config = 'django_pdf_overlay.apps.DjangoPDFOverlayConfig'
