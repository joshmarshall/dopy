import dopy.handlers
import dopy.router
import dopy.tree
import json
from tests.helpers.websocket_test_case import WebSocketTestCase
from tornado.web import Application


class Stub(object):

    @classmethod
    def fetch(cls, identifier):
        return cls(identifier)

    def __init__(self, identifier):
        self._identifier = identifier

    def foo(self):
        return self._identifier

    def add(self, x, y):
        return x + y


class TestRouter(WebSocketTestCase):

    def get_app(self):
        tree = dopy.tree.Tree()
        tree.register_class("stub", Stub)
        tree.register_function("subtract", lambda x, y: x - y)
        router = dopy.router.Router()
        router.register_tree("/messages", tree)
        application = Application(router.generate_routes())
        return application

    def test_tree_registration(self):
        response = self.send_receive(json.dumps({
            "method": "subtract",
            "jsonrpc": "2.0",
            "params": [42, 23],
            "id": "1"
        }))
        self.assertEqual({
            "jsonrpc": "2.0",
            "result": 19,
            "id": "1"
        }, json.loads(response))
