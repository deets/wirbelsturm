import weakref
import types
from collections import defaultdict

class WeakMethod(object):

    def __init__(self, callback):
        self.obj = weakref.ref(callback.im_self)
        self.func = weakref.ref(callback.im_func)

    def __call__(self):
        obj = self.obj()
        func = self.func()
        if obj is not None and func is not None:
            return types.MethodType(func, obj)


    def __eq__(self, other):
        if isinstance(other, WeakMethod):
            return self.obj() == other.obj() and self.func() == other.func()
        return self() == other
    

    def __hash__(self):
        return hash(self())
    
        
class Event(object):

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self._event_bindings = defaultdict(set)
        
    
    def bind(self, event_name, callback):
        if not isinstance(callback, types.MethodType):
            callback = weakref.ref(callback)
        else:
            callback = WeakMethod(callback)

            
        self._event_bindings[event_name].add(callback)


    def trigger(self, event_name, *args, **kwargs):
        listeners = set(self._event_bindings[event_name])
        listeners = listeners | set(self._event_bindings["all"])
        for listener in listeners:
            # resolve weak reference
            cb = listener()
            if cb is not None:
                cb(*args, **kwargs)
            else:
                try:
                    self._event_bindings[event_name].remove(listener)
                except KeyError:
                    pass
                try:
                    self._event_bindings["all"].remove(listener)
                except KeyError:
                    pass
                

    def unbind(self, event_name, callback):
        if not isinstance(callback, types.MethodType):
            callback = weakref.ref(callback)
        self._event_bindings[event_name].remove(callback)
