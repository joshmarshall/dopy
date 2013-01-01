class Tree(object):

    def __init__(self):
        self._registrations = {}

    def register_class(self, name, klass):
        self._registrations[name] = ("class", klass)

    def register_function(self, name, function):
        self._registrations[name] = ("function", function)

    def call_method(self, method, callback, *args, **kwargs):
        callee_type, callee = self._registrations[method]
        result = callee(*args, **kwargs)
        callback(result)
