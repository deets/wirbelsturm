from __future__ import absolute_import
import time
import logging
import bisect
import threading
from json import dumps
from pprint import pformat

import tornado.web

logger = logging.getLogger(__name__)

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


            @tornado.web.asynchronous
            def get(self):
                logger.debug("/dispatch called")
                last_message_id = None
                arguments = self.request.arguments
                if "latest_message_id" in arguments:
                    lmid = self.get_argument("latest_message_id")
                    last_message_id = central_station.cookie_to_mid(lmid)
                logger.debug("waiting for messages, lmid: %r", last_message_id)
                central_station.listen(self, last_message_id)
                # in the meantime, there might have been messages
                # which we want to dispatch immediatly of course.
                # So we invoke the ioloop-callback. It will
                # either dispatch to this handler, or keep
                # it around until something arrives.
                central_station.ioloop_callback()


            def dispatch_messages(self, messages):
                # we take the next message-id here, because the bisect
                # in the callback works as greater-equal, not strict greater
                last_mid = central_station.next_message_id(messages[-1].id)
                lmid = central_station.mid_to_cookie(last_mid)
                logger.debug("dispatch_messages, future lmid: %r", last_mid)
                data = dumps(
                    {"messages" : [m.__json__() for m in messages],
                     "latest_message_id" : lmid
                 })
                self.set_header("Content-Type", "application/json")
                self.write(data)
                logger.debug("data: %r", data)
                self.finish()

                
        return MainHandler


    def ioloop_callback(self):
        """
        This callback is set by the post-method which
        can be called in a different thread than the tornado-application,
        but this callback will then be called from within the tornado-event-loop.
        """

        logger.debug("ioloop_callback")
        with self.lock:
            messages = list(self.messages)

        logger.debug(repr(messages))
        new_listeners = []
        smallest_offset = None
        for mid, listener in self.listeners:
            logger.debug("listener, waiting for lmid: %r", mid)
            offset = bisect.bisect(messages, (mid, None))
            if messages[offset:]:
                logger.debug("offset: %i", offset)
                listener.dispatch_messages([m for _, m in messages[offset:]])
                smallest_offset = min(offset, smallest_offset) if smallest_offset is not None else offset
            else:
                # we didn't yet have enough messages to
                # dispatch, so we re-append this bugger.
                logger.debug("re-appended listener")
                new_listeners.append((mid, listener))
                
        self.listeners[:] = new_listeners
        logger.debug("remaining listeners: %r", self.listeners)
        # if smallest_offset is not None:
        #     with self.lock:
        #         self.messages = self.messages[smallest_offset+1:]
