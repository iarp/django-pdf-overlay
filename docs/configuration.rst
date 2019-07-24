Configuration
=============

Available Settings
------------------

DJANGO_PDF_FILLER_MAGICK_LOCATION
    The location of ImageMagick's convert utility. Value must be a list,
    if you need to add options each option must be its own string entry
    see Windows Default for example.

    * Linux Default: `['/usr/bin/convert']`
    * Windows Default `['magick.exe', 'convert']`

    See: https://imagemagick.org/script/download.php for installation.

DJANGO_PDF_FILLER_MAGICK_DENSITY (='300')
    When creating the images for field layout purposes, what level of pixel
    quality do you want?

DJANGO_PDF_FILLER_LOCAL_DOCUMENT_STORAGE = os.path.join(BASE_DIR, 'media', 'django_pdf_filler', 'documents')
    The document uploaded MUST be located locally to the server itself.
    Where do we place these files?

    Regardless of default storage and media settings in django,
    this location takes precedence as the file must be on the server.
