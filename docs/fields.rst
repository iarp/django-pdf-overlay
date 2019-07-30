Fields Configuration
====================

Available Options
-----------------

name
    Visual name for the layout page.

default (='')
    If no value was found on the model instance, do you have a default you want to supply?

    To print the current datetime as a field on the document, leave obj name blank and
    supply dt:<datetime format> (e.g. dt:%Y-%m-%d), the field will print YYYY-mm-dd.

obj name (='')
    Where to find the data from the parameters passed to `render_pages` in your code.
    Format: object.attribute

    Leave blank if using datetime in the default field as noted above.

    When you call `render_pages` you will be passing model instances::

        doc.render_pages(user=user)

    If you wish to access a field on the user instance, supply `user.<attribute>` to obj name
    (e.g. user.username or user.email).

    It is possible to chain object.attributes (see Field Chaining below).

    If the value of the object.attribute is a date or datetime object, you must supply a
    format to be used as such::

        user.date_joined:%Y-%m-%d

    You can chain that too::

        user.date_joined:%Y-%m-%d|user.first_name|user.last_name

font size (=12)
    Size of font used on the render.

font (='Helvetica')
    The font used must be installed on the server doing the rendering.

font color (='black')
    English name, hashed hex code, OR comma separated RGB values (e.g. 230,230,250)

render_pages parameters explained
---------------------------------

As noted above, obj name field should match the format `object.attribute` where object
is supplied as a named parameter to `render_pages`. (e.g. `render_pages(user=user)`).

It will also match against dict keys using the same dot notation (user.username).
So you can supply your own dict of values instead of a model instance.

Dot notation only works at the first level user.username and no farther.

If the attribute is callable, it will be called with no parameters supplied.

Example 1::

    # Document has a field with obj name of my_dict.val1

    my_dict = {
        'val1': 'Here in dict',
    }

    doc.render_pages(my_dict=my_dict)

Example 2::

    # Document has a field with user.username

    user = User.objects.get(pk=1)

    doc.render_pages(user=user)


Field Chaining
--------------

You can chain object.attributes together by supplying multiples separated by a pipe(`|`)::

    >>> user.first_name|user.last_name
    John Doe

The resulting values from both attributes will be joined by a space.

You can change the character used for joining the chained values by supplying it
after the chained object attributes::

    >>> user.first_name|user.last_name|-
    John-Doe

See `django_pdf_overlay_FIELD_VALUE_JOINS <configuration.html>`__ on configuration for all possible join
values permitted by default.
