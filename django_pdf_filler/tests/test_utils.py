import datetime

from django.test import TestCase


from django_pdf_filler import utils


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

        self.assertEqual('here in test class', utils.get_field_data('name', obj=obj))
        self.assertEqual('here in test class', utils.get_field_data('name', 'obj', obj=obj))
        self.assertEqual('here in callable method', utils.get_field_data('custom_callable', 'obj', obj=obj))
        self.assertIsNone(utils.get_field_data('blah', obj=obj))

        self.assertEqual('here in default', utils.get_field_data('name', default='here in default'))

        def method_test():
            return 'here in method_test'

        d = {
            'name': 'here in dict type',
            'custom_callable': method_test,
        }
        self.assertEqual('here in dict type', utils.get_field_data('name', d=d))
        self.assertEqual('here in method_test', utils.get_field_data('custom_callable', 'd', d=d))
        self.assertEqual('here in method_test', utils.get_field_data('custom_callable', d=d))
        self.assertIsNone(utils.get_field_data('blah', d=d))

        self.assertIsNone(utils.get_field_data('name'))
