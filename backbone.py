"""
A Python-implementation of the backbone.js framework.

  http://documentcloud.github.com/backbone/

It's purpose is to deliver a serverside implementation
that follows the same patterns.
"""
import threading
from itertools import count
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


class Model(Event):
    """
    A very literal translation of the backbone.js Model-class.
    """

    UNDEFINED = object()
    """
    A sentinel value used to convey the undefined state
    of e.g. unset properties - something JS has, but Python lacks.
    """

    DEFAULTS = UNDEFINED
    """
    If defined as a dictionary in a subclass, used as default-values
    for properties.
    """

    ID_CREATORS = {}

    ID_LOCK = threading.Lock()
    

    def __init__(self, properties=None):
        super(Model, self).__init__()
        self.initialize()
        self._properties = {}
        if self.DEFAULTS is not self.UNDEFINED:
            self._properties.update(self.DEFAULTS)
        if properties is not None:
            self._properties.update(properties)

        if not "id" in self._properties:
            self._properties["id"] = self.create_id()
        self.id = self._properties["id"]
        

    @classmethod
    def create_id(cls):
        with cls.ID_LOCK:
            if cls not in cls.ID_CREATORS:
                cls.ID_CREATORS[cls] = count()
                
        return "%s_%i" % (cls.__name__ , cls.ID_CREATORS[cls].next())
        
        

    def initialize(self):
        """
        Stub implementation to make super() work.
        """
        pass


    def set(self, properties, silent=False):
        changed = False
        for key, value in properties.iteritems():
            if key in self._properties and self._properties[key] == value:
                continue
            changed = True
            self._properties[key] = value
            if not silent:
                self.trigger("change:" + key, self, value)
            
        if changed and not silent:
            self.trigger("change", self)

        return True
    
    
    def get(self, name):
        return self._properties[name]

    
    def unset(self, name, silent=False):
        if name in self._properties:
            del self._properties[name]
            if not silent:
                self.trigger("change:" + name, self, self.UNDEFINED)
            
            if not silent:
                self.trigger("change", self)


    def clear(self, silent=False):
        if self._properties:
            self._properties = {}
            if not silent:
                self.trigger("change", self)
                
