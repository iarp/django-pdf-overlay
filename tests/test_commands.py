from django.test.utils import override_settings
from .base_test_classes import BaseTestClassMethods
from django_pdf_overlay.commands import get_commands


class CommandsTests(BaseTestClassMethods):

    @override_settings(
        DJANGO_PDF_OVERLAY_MAGICK_LOCATION=['MAGICK_LOC'],
        DJANGO_PDF_OVERLAY_MAGICK_DENSITY=300,
        DJANGO_PDF_OVERLAY_MAGICK_FLATTEN=True,
    )
    def test_command_get_pdf_to_image_command_all_settings(self):
        doc = self.setup_test_document()
        page = doc.pages.first()
        output, output_tmp_img_filepath = get_commands().get_pdf_to_image_command(document=doc, page=page)

        filepath_raw, ext = doc.file.path.rsplit('.', 1)
        temporary_image_filepath = '{}_{}.jpg'.format(filepath_raw, page.number)

        self.assertEqual(output_tmp_img_filepath, temporary_image_filepath)

        doc_path_page_num = '{}[{}]'.format(doc.file.path, page.number)
        self.assertEqual(
            ['MAGICK_LOC', '-density', '300', '-flatten', doc_path_page_num, temporary_image_filepath],
            output
        )

    @override_settings(
        DJANGO_PDF_OVERLAY_MAGICK_LOCATION='MAGICK_LOC',
        DJANGO_PDF_OVERLAY_MAGICK_DENSITY=300,
        DJANGO_PDF_OVERLAY_MAGICK_FLATTEN=False,
    )
    def test_command_get_pdf_to_image_command_no_flatten(self):
        doc = self.setup_test_document()
        page = doc.pages.first()
        output, _ = get_commands().get_pdf_to_image_command(document=doc, page=page)

        filepath_raw, ext = doc.file.path.rsplit('.', 1)
        temporary_image_filepath = '{}_{}.jpg'.format(filepath_raw, page.number)

        doc_path_page_num = '{}[{}]'.format(doc.file.path, page.number)
        self.assertEqual(
            ['MAGICK_LOC', '-density', '300', doc_path_page_num, temporary_image_filepath],
            output
        )

    @override_settings(
        DJANGO_PDF_OVERLAY_MAGICK_LOCATION='MAGICK_LOC',
        DJANGO_PDF_OVERLAY_MAGICK_DENSITY=600,
        DJANGO_PDF_OVERLAY_MAGICK_FLATTEN=False,
    )
    def test_command_get_pdf_to_image_command_differ_density(self):
        doc = self.setup_test_document()
        page = doc.pages.first()
        output, _ = get_commands().get_pdf_to_image_command(document=doc, page=page)

        filepath_raw, ext = doc.file.path.rsplit('.', 1)
        temporary_image_filepath = '{}_{}.jpg'.format(filepath_raw, page.number)

        doc_path_page_num = '{}[{}]'.format(doc.file.path, page.number)
        self.assertEqual(
            ['MAGICK_LOC', '-density', '600', doc_path_page_num, temporary_image_filepath],
            output
        )

    def test_get_layout_image_filename(self):
        doc = self.setup_test_document()
        page = doc.pages.first()

        output = get_commands().get_layout_image_filename(document=doc, page=page)

        tmp_image_name, _ = doc.file.name.rsplit('.', 1)
        expected = '{}_{}.jpg'.format(tmp_image_name, page.number)

        self.assertEqual(expected, output)
