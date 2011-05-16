import weakref
import types
from collections import defaultdict

class Event(object):

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self._event_bindings = defaultdict(set)
        
    
    def bind(self, event_name, callback):
        if not isinstance(callback, types.MethodType):
            callback = weakref.ref(callback)
        self._event_bindings[event_name].add(callback)


    def trigger(self, event_name, *args, **kwargs):
        listeners = set(self._event_bindings[event_name])
        listeners = listeners | set(self._event_bindings["all"])
        for listener_ref in listeners:
            cb = listener_ref()
            if cb is not None:
                cb(*args, **kwargs)
        

    def unbind(self, event_name, callback):
        if not isinstance(callback, types.MethodType):
            callback = weakref.ref(callback)
        self._event_bindings[event_name].remove(callback)
