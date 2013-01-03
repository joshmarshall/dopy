from dopy.tree import Tree, asynchronous, IllegalAttributeLookup
import mock
import unittest


class Foo(object):
    """Mock class for testing instances, classmethods, etc."""

    def __init__(self, identifier=None):
        self.identifier = identifier

    @classmethod
    def class_method(klass, *args, **kwargs):
        return (klass, args, kwargs)

    def instance_method(self, *args, **kwargs):
        return (self, args, kwargs)

    @classmethod
    @asynchronous
    def async_class_method(klass, *args, **kwargs):
        callback = kwargs.pop("callback")
        callback((klass, args, kwargs))

    @asynchronous
    def async_instance_method(self, *args, **kwargs):
        callback = kwargs.pop("callback")
        callback((self, args, kwargs))


class TestTree(unittest.TestCase):

    def setUp(self):
        # Mock functions
        self._mock_bar = mock.Mock()
        self._mock_foo = mock.Mock()
        self._mock_bar.return_value = self._mock_foo
        self._mock_async = asynchronous(self.get_async_function())

        # registering with the tree
        self._tree = Tree()
        self._tree.register_class("foo", Foo)
        self._tree.register_function("bar", self._mock_bar)
        self._tree.register_function("async", self._mock_async)

    def call_method(self, method, *args, **kwargs):
        results = []

        def callback(result):
            results.append(result)
        self._tree.call_method(method, callback, *args, **kwargs)
        self.assertEqual(1, len(results))
        return results[0]

    def get_async_function(self):
        def async_function(*args, **kwargs):
            self.assertTrue("callback" in kwargs)
            callback = kwargs.pop("callback")
            callback((args, kwargs))
        return async_function

    def test_tree_function(self):
        self.call_method("bar", 5, 6)
        self._mock_bar.assert_called_with(5, 6)

    def test_tree_function_with_keyword_arguments(self):
        self.call_method("bar", foo="bar")
        self._mock_bar.assert_called_with(foo="bar")

    def test_tree_function_asynchronous(self):
        result = self.call_method("async", foo="bar")
        self.assertEqual(((), {"foo": "bar"}), result)

    def test_tree_class(self):
        result = self.call_method("foo")
        self.assertTrue(isinstance(result, Foo))
        self.assertEqual(result.identifier, None)

    def test_tree_class_method(self):
        result = self.call_method("foo.class_method", foo="bar")
        self.assertEqual((Foo, (), {"foo": "bar"}), result)

    def test_tree_class_method_asynchronous(self):
        result = self.call_method("foo.async_class_method", foo="bar")
        self.assertEqual((Foo, (), {"foo": "bar"}), result)

    def test_tree_instance(self):
        instance, args, kwargs = self.call_method("foo.@shoe.instance_method")
        self.assertEqual((), args)
        self.assertEqual({}, kwargs)
        self.assertEqual("shoe", instance.identifier)

    def test_tree_illegal_lookup(self):
        with self.assertRaises(IllegalAttributeLookup):
            self.call_method("foo.@what.__sizeof__")
