Commands
--------

You can override the following class and its methods to change certain behavior

Create your custom class extending DefaultCommands and supply the dot
notation path to your class with ``DJANGO_PDF_FILLER_COMMANDS`` in your
project settings:

- ``django_pdf_filler.commands.DefaultCommands``

  - ``get_pdf_to_image_command(self, document, page)``
    returns a list of prepared commands to be used in the ``execute`` method below.

  - ``execute(self, document, page, commands)``
    Executes the commands given on the system. Commands is the output
    from get_pdf_to_image_command above. No return needed. document and page are the
    objects being worked on.

  - ``get_layout_image_filename(self, document, page)``
    Returns a string containing the filename of the layout image
    about to be saved to page.layout. Default is ``{document filename}_{page number}.jpg``

  - ``convert_to_image(self, document, page)``
    Combines all methods above and does the actual processing of data.

Example
-------
my_proj/overrides.py::

    from django_pdf_filler.commands import DefaultCommands

    class OverriddenCommands(DefaultCommands):
        def execute(self, document, page, commands):
            # You can now change the system call used from our default of
            # subprocess.Popen to whatever you want.

my_proj/settings.py::

    DJANGO_PDF_FILLER_COMMANDS = 'my_proj.overrides.OverriddenCommands'
