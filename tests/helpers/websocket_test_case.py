from tornado.testing import AsyncHTTPTestCase
from tornado_websocket_client import WebSocket


class WebSocketTestCase(AsyncHTTPTestCase):

    def make_client(
            self, path, on_open=None, on_message=None, on_close=None):

        url = "ws://localhost:%d%s" % (self.get_http_port(), path)

        if not on_open:
            on_open = lambda x: None
        if not on_message:
            on_message = lambda x, y: None
        if not on_close:
            on_close = lambda x: None

        class TempSocket(WebSocket):

            def on_open(self):
                on_open(self)

            def on_message(self, data):
                on_message(self, data)

            def on_close(self):
                on_close(self)

        return TempSocket(url, io_loop=self.io_loop)

    def send_receive(self, send_message, timeout=5):
        # shortcut for sending one message and receiving one message
        def on_open(client):
            client.write_message(send_message)

        messages = []

        def on_message(client, message):
            messages.append(message)
            self.stop()

        self.make_client(
            "/messages", on_open=on_open, on_message=on_message)

        self.wait(timeout=timeout)
        self.assertEqual(1, len(messages))
        return messages[0]
