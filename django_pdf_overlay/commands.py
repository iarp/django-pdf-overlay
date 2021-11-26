import logging
import os
import subprocess

from . import app_settings
from .utils import import_attribute

log = logging.getLogger('django_pdf_overlay.comments')


class DefaultCommands(object):

    def get_pdf_to_image_command(self, document, page):
        """ Builds the command(s) to be used in self.execute

        As we are working with an external application to generate the layout
        images, that external application will need to save it somewhere
        temporarily. We also need to return that temporary filepath for use later.
        """
        filepath_raw, ext = document.file.path.rsplit('.', 1)
        temporary_image_filepath = '{}_{}.jpg'.format(filepath_raw, page.number)

        commands = app_settings.MAGICK_LOCATION

        if app_settings.MAGICK_DENSITY:
            commands.extend(['-density', app_settings.MAGICK_DENSITY])
        if app_settings.MAGICK_FLATTEN:
            commands.append('-flatten')

        wanted_page = '{}[{}]'.format(document.file.path, page.number)
        commands.extend([wanted_page, temporary_image_filepath])

        return commands, temporary_image_filepath

    def execute(self, document, page, commands):  # pragma: no cover
        """ Executes the commands built in self.get_page_to_image_command.

        It is expected that when this method finishes running,
        the image should be created.
        """
        try:
            log.debug(commands)
            process = subprocess.Popen(commands)
            process.wait()
        except FileNotFoundError:
            if document:
                document.delete()
            raise FileNotFoundError('Unable to locate ImageMagick installation.')

    def get_layout_image_filename(self, document, page):
        """ Return a string that represents the name of the final layout image filename. """
        tmp_image_name, _ = document.file.name.rsplit('.', 1)
        return '{}_{}.jpg'.format(tmp_image_name, page.number)

    def convert_to_image(self, document, page):  # pragma: no cover
        """ Brings together all the methods above and saves the image to the page object. """
        if page.image:
            page.image.delete(save=False)

        commands, temporary_image_filepath = self.get_pdf_to_image_command(
            document=document,
            page=page,
        )

        self.execute(
            document=document,
            page=page,
            commands=commands,
        )

        if os.path.isfile(temporary_image_filepath):

            final_image_filename = self.get_layout_image_filename(
                document=document,
                page=page,
            )

            with open(temporary_image_filepath, 'rb') as fo:
                page.image.save(final_image_filename, fo)

            os.remove(temporary_image_filepath)
            return True

        return False


def get_commands():
    return import_attribute(app_settings.COMMANDS)()
