class AppSettings(object):

    def __init__(self, prefix):
        self.prefix = prefix

        assert isinstance(self.FIELD_VALUE_JOINS, (str, list, set, tuple)), \
            "{}FIELD_VALUE_JOINS must be of type list, set, tuple, or str".format(prefix)
        assert self.FIELD_CHAIN_SPLITTER != self.FIELD_DATETIME_SPLITTER, \
            "{0}FIELD_CHAIN_SPLITTER and " \
            "{0}FIELD_DATETIME_SPLITTER cannot be the same value.".format(prefix)
        assert isinstance(self.MAGICK_LOCATION, list), \
            "{}MAGICK_LOCATION must be of type list or str".format(prefix)

    def _setting(self, name, default):
        from django.conf import settings
        return getattr(settings, self.prefix + name, default)

    @property
    def GENERATE_LAYOUT_IMAGE(self):
        return self._setting('GENERATE_LAYOUT_IMAGE', True)

    @property
    def LOCAL_DOCUMENT_STORAGE(self):
        from django.conf import settings
        import os
        return self._setting(
            'LOCAL_DOCUMENT_STORAGE',
            os.path.join(settings.BASE_DIR, 'media', 'django_pdf_overlay', 'documents')
        )

    @property
    def MAGICK_DENSITY(self):
        return str(self._setting('MAGICK_DENSITY', 300))

    @property
    def MAGICK_FLATTEN(self):
        return self._setting('MAGICK_FLATTEN', True)

    @property
    def MAGICK_LOCATION(self):
        import os
        location = self._setting('MAGICK_LOCATION', None)

        if location:
            if isinstance(location, str):
                location = [location]
        else:
            location = ['/usr/bin/convert']
            if os.name == 'nt':
                location = ['magick.exe', 'convert']

        return list(location)

    @property
    def FIELD_VALUE_JOINS(self):
        return self._setting('FIELD_VALUE_JOINS', ', .|-_')

    @property
    def FIELD_CHAIN_SPLITTER(self):
        return self._setting('FIELD_CHAIN_SPLITTER', '|')

    @property
    def FIELD_DATETIME_SPLITTER(self):
        return self._setting('FIELD_DATETIME_SPLITTER', ':')

    @property
    def COMMANDS(self):
        return self._setting('COMMANDS', 'django_pdf_overlay.commands.DefaultCommands')


import sys  # noqa

app_settings = AppSettings('DJANGO_PDF_OVERLAY_')
app_settings.__name__ = __name__
sys.modules[__name__] = app_settings
