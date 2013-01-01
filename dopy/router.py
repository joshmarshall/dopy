import json
from tornado.websocket import WebSocketHandler


class Router(object):

    def __init__(self):
        self._routes = []

    def register_tree(self, path, tree):
        self._routes.append((path, generate_tree_handler(tree)))

    def generate_routes(self):
        return self._routes


def generate_tree_handler(tree):

    class TreeHandler(WebSocketHandler):

        def on_message(self, data):
            jsonrpc_message = json.loads(data)
            arguments = jsonrpc_message["params"]
            method = jsonrpc_message["method"]
            if hasattr(arguments, "keys"):
                # goofy way of checking if we're a dictionary...
                keywords = arguments
                arguments = []
            else:
                keywords = {}
            callback = self._generate_callback(jsonrpc_message)
            tree.call_method(method, callback, *arguments, **keywords)

        def _generate_callback(self, jsonrpc_message):
            def callback(result):
                self.write_message({
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": jsonrpc_message["id"]
                })
            return callback

    return TreeHandler
