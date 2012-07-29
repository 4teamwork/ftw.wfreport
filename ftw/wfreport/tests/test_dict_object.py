from ftw.wfreport.dict_object import DictObject
from unittest2 import TestCase


class TestDictObject(TestCase):

    def test_argument_construction(self):
        obj = DictObject(foo='bar')
        self.assertEqual(obj, {'foo': 'bar'})

    def test_casting_construction(self):
        obj = DictObject({'foo': 'bar'})
        self.assertEqual(obj, {'foo': 'bar'})

    def test_dict_access(self):
        obj = DictObject(foo='bar')
        self.assertEqual(obj['foo'], 'bar')

        with self.assertRaises(KeyError):
            obj['missing']

        self.assertEqual(obj.get('missing', 'baz'), 'baz')

    def test_attribute_access(self):
        obj = DictObject(foo='bar')
        self.assertEqual(obj.foo, 'bar')

        with self.assertRaises(AttributeError):
            obj.missing

        self.assertEqual(getattr(obj, 'missing', 'baz'), 'baz')

    def test_in(self):
        obj = DictObject(foo='bar')
        self.assertTrue('foo' in obj)
        self.assertFalse('baz' in obj)

    def test_length(self):
        obj = DictObject(foo='bar')
        self.assertEqual(len(obj), 1)
        obj.baz = 1
        self.assertEqual(len(obj), 2)

    def test_iteration(self):
        obj = DictObject(foo=1, bar=2, baz=3)
        self.assertEqual(set(obj), set(obj.keys()))

    def test_updating(self):
        obj = DictObject(foo='bar')
        self.assertEqual(obj, {'foo': 'bar'})

        obj['foo'] = 1
        self.assertEqual(obj, {'foo': 1})

        obj['bar'] = 2
        self.assertEqual(obj, {'foo': 1, 'bar': 2})

        obj.foo = 3
        self.assertEqual(obj, {'foo': 3, 'bar': 2})

        obj.baz = 1
        self.assertEqual(obj, {'foo': 3, 'bar': 2, 'baz': 1})

        setattr(obj, 'baz', 3)
        self.assertEqual(obj, {'foo': 3, 'bar': 2, 'baz': 3})

    def test_deleting(self):
        obj = DictObject(foo=1, bar=2, baz=3)
        self.assertEqual(obj, {'foo': 1, 'bar': 2, 'baz': 3})

        del obj['baz']
        self.assertEqual(obj, {'foo': 1, 'bar': 2})

        delattr(obj, 'bar')
        self.assertEqual(obj, {'foo': 1})

    def test_conversion(self):
        a = {'foo': 1,
             'bar': 2}
        b = DictObject(a)
        c = dict(b)

        self.assertEqual(a, c)

    def test_acts_as_dict(self):
        a = {'foo': 1,
             'bar': 2}
        b = DictObject(a)
        self.assertEqual(a, b)

    def test_update(self):
        obj = DictObject(foo=1)
        obj.update(dict(bar=2))
        self.assertEqual(obj, {'foo': 1, 'bar': 2})

    def test_data_key(self):
        # data is used internally, so we need to explictly test it
        obj = DictObject(data=1)
        self.assertEqual(obj, {'data': 1})

        obj.data = 2
        self.assertEqual(obj, {'data': 2})

        obj.update(dict(data=3))
        self.assertEqual(obj, {'data': 3})
