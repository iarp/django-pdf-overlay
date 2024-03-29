Configuration
=============

Available Settings
------------------

DJANGO_PDF_OVERLAY_GENERATE_LAYOUT_IMAGE (=True)
    Enable or disable whether or not the system will auto-generate layout images from PDF.

    Useful when you cannot or don't want to install ImageMagic.

    Disabling this does require you to manually create the image and attach
    it to the page accordingly before field layout is possible.

DJANGO_PDF_OVERLAY_MAGICK_LOCATION
    The location of ImageMagick's convert utility. Value must be a list,
    if you need to add options each option must be its own string entry
    see Windows Default for example.

    * Linux Default: `['/usr/bin/convert']`
    * Windows Default `['magick.exe', 'convert']`

    See: https://imagemagick.org/script/download.php for installation.

DJANGO_PDF_OVERLAY_MAGICK_DENSITY (='300')
    When creating the images for field layout purposes, what level of pixel
    quality do you want?

DJANGO_PDF_OVERLAY_MAGICK_FLATTEN (=True)
    Pass -flatten to magick conversion? True or False.

DJANGO_PDF_OVERLAY_LOCAL_DOCUMENT_STORAGE (=os.path.join(BASE_DIR, 'media', 'django_pdf_overlay', 'documents'))
    The document uploaded MUST be located locally to the server itself.
    Where do we place these files?

    Regardless of default storage and media settings in django,
    this location takes precedence as the file must be on the server.

DJANGO_PDF_OVERLAY_FIELD_VALUE_JOINS (=', .-_')
    When you chain object attributes in "obj name" on a field, you can select what
    value to join the chained values on. Default is a space, supply a string, list,
    tuple, or set to customize this.

    * Comma
    * Space
    * Period
    * Dash
    * Underscore

DJANGO_PDF_OVERLAY_FIELD_CHAIN_SPLITTER (='|')
    Value used to split chained object.attributes on fields obj name value. Default is Pipe.

DJANGO_PDF_OVERLAY_FIELD_DATETIME_SPLITTER (=':')
    Value used to split object.attribute from its datetime formatting.

    This value MUST be different than DJANGO_PDF_OVERLAY_FIELD_CHAIN_SPLITTER.

DJANGO_PDF_OVERLAY_COMMANDS (='django_pdf_overlay.commands.DefaultCommands')
    Dot notated path to the Commands class allowing you to alter certain methods used within the program.
