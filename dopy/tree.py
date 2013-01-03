class Tree(object):

    def __init__(self):
        self._registrations = {}

    def register_class(self, name, klass):
        self._registrations[name] = ("class", klass)

    def register_function(self, name, function):
        self._registrations[name] = ("function", function)

    def call_method(self, method, callback, *args, **kwargs):
        # this is really ugly, especially when we need to make the
        # "@identifier" lookup asynchronous
        callee_type, callee = self._registrations.get(method, (None, None))
        if callee:
            # the exact function was registered, so call it
            _call_function(callee, args, kwargs, callback)
        else:
            method_parts = method.split(".")
            method_name = method_parts.pop(0)
            callee_type, callee = self._registrations[method_name]
            _crawl_attributes(method_parts, callee, args, kwargs, callback)


def _crawl_attributes(method_parts, callee, args, kwargs, callback):
    while method_parts:
        attribute_name = method_parts.pop(0)
        if attribute_name.startswith("@"):
            def lookup_callback(result):
                _crawl_attributes(method_parts, result, args, kwargs, callback)
            arguments = (attribute_name[1:],)
            return _call_function(callee, arguments, {}, lookup_callback)
        callee = getattr(callee, attribute_name)
    _call_function(callee, args, kwargs, callback)


def _call_function(callee, args, kwargs, callback):
    """Call a function (asynchronously if indicated) and pass the result
    to the callback.

    """
    async = getattr(callee, "_auto_finish", True) is False
    if async:
        kwargs["callback"] = callback
    result = callee(*args, **kwargs)
    if not async:
        callback(result)


def asynchronous(method):
    """Wrap a function or method so that the tree knows not to use
    the return value.

    """
    # TODO -- write tests and ExceptionStackContext stuff.
    method._auto_finish = False
    return method
