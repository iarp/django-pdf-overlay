import subprocess

from . import app_settings
from .utils import import_attribute


class DefaultCommands(object):

    def get_pdf_to_image_command(self, document, page):

        filepath_raw, ext = document.file.path.rsplit('.', 1)
        image_file = '{}_{}.jpg'.format(filepath_raw, page.number)

        commands = app_settings.MAGICK_LOCATION.copy()

        if app_settings.MAGICK_DENSITY:
            commands.extend(['-density', app_settings.MAGICK_DENSITY])
        if app_settings.MAGICK_FLATTEN:
            commands.append('-flatten')

        wanted_page = '{}[{}]'.format(document.file.path, page.number)
        commands.extend([wanted_page, image_file])

        return commands, image_file

    def execute(self, commands, document, page):
        try:
            process = subprocess.Popen(commands, shell=True)
            process.wait()
        except FileNotFoundError:
            if document:
                document.delete()
            raise FileNotFoundError('Unable to locate ImageMagick installation.')


def get_commands():
    return import_attribute(app_settings.COMMANDS)()
