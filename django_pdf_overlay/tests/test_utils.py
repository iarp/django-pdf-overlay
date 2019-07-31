import datetime

from django.test import TestCase
from django_pdf_overlay import forms, utils


class UtilsTests(TestCase):

    def test_startswith_many(self):
        items = ['d:', 'dt:', 'datetime:']
        self.assertTrue(utils.startswith_many('dt:%Y-%m-%d', items))
        self.assertFalse(utils.startswith_many('non-existent:%Y-%m-%d', items))

    def test_convert_datetime_objects(self):
        now = datetime.datetime.now()
        self.assertEqual(now.strftime('%Y-%m-%d'), utils.convert_datetime_objects('dt:%Y-%m-%d'))
        self.assertEqual('%Y-%m-%d', utils.convert_datetime_objects('%Y-%m-%d'))
        self.assertEqual(now.strftime('%B'), utils.convert_datetime_objects('month_long'))
        self.assertEqual(utils.ordinal(now.day), utils.convert_datetime_objects('day'))
        self.assertEqual(str(now.year)[2:], utils.convert_datetime_objects('year_short'))

    def test_ordinal(self):
        self.assertEqual('1st', utils.ordinal(1))
        self.assertEqual('2nd', utils.ordinal(2))
        self.assertEqual('3rd', utils.ordinal(3))
        self.assertEqual('4th', utils.ordinal(4))
        self.assertEqual('5th', utils.ordinal(5))

    def test_get_field_data(self):
        class TestClass(object):
            name = 'here in test class'

            def custom_callable(self):
                return 'here in callable method'

        obj = TestClass()

        self.assertIsNone(utils.get_field_data('name'))
        self.assertIsNone(utils.get_field_data('blah', obj=obj))

        self.assertEqual('here in test class', utils.get_field_data('name', obj=obj))
        self.assertEqual('here in test class', utils.get_field_data('obj.name', obj=obj))
        self.assertEqual('here in callable method', utils.get_field_data('custom_callable', obj=obj))
        self.assertEqual('here in callable method', utils.get_field_data('obj.custom_callable', obj=obj))

        self.assertEqual('here in default', utils.get_field_data('missing', default='here in default', obj=obj))
        self.assertEqual('here in default', utils.get_field_data('obj.missing', default='here in default', obj=obj))

        def method_test():
            return 'here in method_test'

        d = {
            'name': 'here in dict type',
            'custom_callable': method_test,
        }
        self.assertEqual('here in dict type', utils.get_field_data('name', d=d))
        self.assertEqual('here in method_test', utils.get_field_data('custom_callable', d=d))
        self.assertEqual('here in method_test', utils.get_field_data('d.custom_callable', d=d))

    def test_split_and_strip(self):
        self.assertEqual('', forms.split_and_strip(' '))
        self.assertEqual('asd', forms.split_and_strip('asd '))
        self.assertEqual('asd| ', forms.split_and_strip('asd| '))
        self.assertEqual('asd|blahs', forms.split_and_strip('asd|blahs '))
        self.assertEqual('asd|blahs| ', forms.split_and_strip('asd|blahs| '))
