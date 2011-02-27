from __future__ import absolute_import, with_statement

import threading
from json import dumps

import tornado.httpserver
import tornado.ioloop
import tornado.web

from .chat import CHAT
from .centralstation import CentralStation        

class ChatHandler(tornado.web.RequestHandler):

    def post(self):
        arguments = self.request.arguments
        usercookie = self.get_argument("usercookie")
        userinfo = CHAT[usercookie]
        if "typing" in arguments:
            userinfo.typing(True if self.get_argument("typing") == "true" else False)
        if "message" in arguments:
            userinfo.send_message(arguments["message"])


        data = dumps({"status" : "ok"})
        self.set_header("Content-Type", "application/json")
        self.write(data)

        

application = tornado.web.Application([
    (r"/chat_dispatch", ChatHandler),
    (r"/dispatch", CentralStation.instance().create_handler()),
])


def start_app(port):
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    threading.Thread(target=tornado.ioloop.IOLoop.instance().start).start()
