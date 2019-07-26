VERSION = (1, 0, 3, 'final', 0)

__title__ = 'django-pdf-filler'
__version_info__ = VERSION
__version__ = '.'.join(map(str, VERSION[:3])) + ('-{}{}'.format(
    VERSION[3], VERSION[4] or '') if VERSION[3] != 'final' else '')
__author__ = 'IARP'
__license__ = 'MIT'
__copyright__ = 'Copyright 2019 IARP and contributors'
