from __future__ import absolute_import
import time
import bisect
import threading
from json import dumps

import tornado.web

class MessageInfo(object):

    def __init__(self, dispatcher, scope, operation, payload):
        self.scope = scope
        self.operation = operation
        self.payload = payload
        self.id = dispatcher.next_message_id()


    def __json__(self):
        return dict(
            scope=self.scope,
            operation=self.operation,
            payload=self.payload)


    def __str__(self):
        return dumps(self.__json__())


    def __repr__(self):
        return "<%s\n%r\n%s\n>" % (self.__class__.__name__,
                                   self.id,
                                   str(self))


class TimeBasedIdProvider(object):

    
    def __init__(self, time=time.time):
        self.time = time
        self.current = self.time()
        self.lock = threading.RLock()
        

    def next(self, last_id=None):
        with self.lock:
            if last_id is None:
                candidate = self.time()
                # ups, two message in succession - create an arbirtrary
                # new id
                if self.current >= candidate:
                    candidate = self.next(self.current)
                self.current = candidate
            else:
                # increment the current by the tiniest amount possible
                # to yield a new number
                def inc(n):
                    o = n
                    while n + o != n:
                        a = o
                        o /= 2
                    return n + a
                self.current = inc(self.current)
            return self.current

    def to_cookie(self, id_):
        return repr(id_)


    def from_cookie(self, cookie):
        return float(cookie)
    
    
class CentralStation(object):


    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance


    def __init__(self, id_provider=None, ioloop=None):
        if id_provider is None:
            id_provider = TimeBasedIdProvider()
        self.id_provider = id_provider
        self.messages = []
        self.listeners = []

        self.lock = threading.Lock()
        if ioloop is None:
            ioloop = tornado.ioloop.IOLoop.instance()
        self.ioloop = ioloop
        

    def post(self, scope, operation, payload):
        with self.lock:
            mi = MessageInfo(self, scope, operation, payload)
            self.messages.append((mi.id, mi))
        self.ioloop.add_callback(self.ioloop_callback)
        

    def next_message_id(self, last_id=None):
        return self.id_provider.next(last_id)


    def current_message_id(self):
        return self.id_provider.current
    

    def listen(self, handler, message_id=None):
        with self.lock:
            if message_id is None:
                message_id = self.current_message_id()
            self.listeners.append((message_id, handler))


    def mid_to_cookie(self, mid):
        return self.id_provider.to_cookie(mid)


    def cookie_to_mid(self, cookie):
        return self.id_provider.from_cookie(cookie)
    

    def create_handler(self):
        central_station = self

        
        class MainHandler(tornado.web.RequestHandler):
            callbacks = []

            LATEST_MESSAGE_ID_COOKIE = "Latest-Message-ID"


            @tornado.web.asynchronous
            def get(self):
                last_message_id = None
                cookie = self.request.headers.get(self.LATEST_MESSAGE_ID_COOKIE)
                if cookie:
                    last_message_id = central_station.cookie_to_mid(cookie)
                central_station.listen(self, last_message_id)


            def dispatch_messages(self, messages):
                # we take the next message-id here, because the bisect
                # in the callback works as greater-equal, not strict greater
                last_mid = central_station.next_message_id(messages[-1].id)
                data = dumps({"messages" : [m.__json__() for m in messages]})
                self.set_header("Content-Type", "application/json")
                self.set_header(self.LATEST_MESSAGE_ID_COOKIE,
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
