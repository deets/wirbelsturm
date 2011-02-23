from __future__ import absolute_import

import bisect
import threading
from json import dumps
import tornado.httpserver
import tornado.ioloop
import tornado.web


class MessageInfo(object):

    def __init__(self, dispatcher, type, payload):
        self.payload = payload
        self.type = type
        self.id = dispatcher.message_id()
        


    def __json__(self):
        return dict(
            type=self.type,
            payload=self.payload)


    def __str__(self):
        return dumps(self.__json__())


    def __repr__(self):
        return "<%s\n%r\n%s\n>" % (self.__class__.__name__,
                                   self.id,
                                   str(self))
    
    
class CentralStation(object):

    LATEST_MESSAGE_ID_COOKIE = "Latest-Message-ID"

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance


    def __init__(self, ioloop=None):
        self.message_count = 0
        self.messages = []
        self.listeners = []
        self.lock = threading.Lock()
        if ioloop is None:
            ioloop = tornado.ioloop.IOLoop.instance()
        self.ioloop = ioloop
        

    def post(self, type, payload):
        with self.lock:
            mi = MessageInfo(self, type, payload)
            self.messages.append((mi.id, mi))
            self.message_count += 1
        self.ioloop.add_callback(self.ioloop_callback)
        

    def message_id(self):
        return self.message_count
    

    def listen(self, handler, message_id=None):
        with self.lock:
            if message_id is None:
                message_id = self.message_id()
            self.listeners.append((message_id, handler))


    def mid_to_cookie(self, mid):
        return str(mid)


    def cookie_to_mid(self, cookie):
        return int(cookie)
    

    def create_handler(self):
        central_station = self

        
        class MainHandler(tornado.web.RequestHandler):
            callbacks = []

            @tornado.web.asynchronous
            def get(self):
                lmid = self.get_cookie(central_station.LATEST_MESSAGE_ID_COOKIE)
                if lmid:
                    lmid = central_station.cookie_to_mid(lmid)
                else:
                    lmid = None
                central_station.listen(self, lmid)


            def dispatch_messages(self, messages):
                last_mid = messages[-1].id
                data = dumps({"messages" : [m.__json__() for m in messages]})
                self.set_header("Content-Type", "application/json")
                self.set_cookie(central_station.LATEST_MESSAGE_ID_COOKIE,
                                central_station.mid_to_cookie(last_mid))
                self.write(data)
                self.finish()

                
        return MainHandler


    def ioloop_callback(self):
        """
        This callback is set by the post-method which
        can be called in a different thread than the tornado-application,
        but this callback will then be called from within the tornado-event-loop.
        """
        with self.lock:
            messages = list(self.messages)

        new_listeners = []
        for mid, listener in self.listeners:
            offset = bisect.bisect(messages, (mid, None))
            if messages[offset:]:
                listener.dispatch_messages([m for _, m in messages[offset:]])
            else:
                # we didn't yet have enough messages to
                # dispatch, so we re-append this bugger.
                new_listeners.append((mid, listener))
                
        self.listeners[:] = new_listeners
        
        

application = tornado.web.Application([
    (r"/dispatch", CentralStation.instance().create_handler()),
])


def start_app(port):
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    threading.Thread(target=tornado.ioloop.IOLoop.instance().start).start()
