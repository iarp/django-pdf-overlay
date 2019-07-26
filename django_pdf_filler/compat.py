
try:
    from django.utils import six
except ImportError:
    class six:
        PY3 = True
        PY2 = False
        integer_types = (int,)
        string_types = (str,)
