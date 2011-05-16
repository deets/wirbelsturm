from backbone import Event

def cb_factory(c):
    def cb(*args, **kwargs):
        c.append((args, kwargs))
    return cb


def test_weakrefs_work():
    events = []
    callback = cb_factory(events)

    class Test(Event):
        pass

    t = Test()
    t.bind("all", callback)
    t.trigger("all")
    assert len(events) == 1
    del callback
    events[:] = []
    t.trigger("all")
    assert not events


def test_all_triggering():
    events = []
    callback = cb_factory(events)

    class Test(Event):
        pass

    t = Test()
    t.bind("all", callback)
    t.trigger("foo")
    assert len(events) == 1
    t.trigger("bar")
    assert len(events) == 2


def test_argument_passing():
    events = []
    callback = cb_factory(events)

    class Test(Event):
        pass

    t = Test()
    t.bind("foo", callback)
    t.trigger("foo", 1, 2, bar="baz")
    assert len(events) == 1
    event = events[0]
    assert event == ((1, 2), dict(bar="baz"))


def test_unbinding():
    events = []
    callback = cb_factory(events)

    class Test(Event):
        pass

    t = Test()
    t.bind("foo", callback)
    t.trigger("foo", 1, 2, bar="baz")
    assert len(events) == 1
    t.unbind("foo", callback)
    t.trigger("foo", 1, 2, bar="baz")
    assert len(events) == 1
    

def test_bound_methods_are_bound_once_only():

    class Listener(object):

        def __init__(self):
            self.events = []

            
        def callback(self, *args, **kwargs):
            self.events.append((args, kwargs))

            
    class Test(Event):
        pass

    listener = Listener()
    
    t = Test()
    t.bind("foo", listener.callback)
    t.trigger("foo")
    assert len(listener.events) == 1
    
