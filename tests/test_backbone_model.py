from backbone import Model


def test_simple_inheritance_and_initialization():

    class TestModel(Model):

        def initialize(self):
            self.foobar = "baz"


    tm = TestModel()
    assert tm.foobar == "baz"


def test_set_and_get_and_unset():

    class TestModel(Model):
        pass


    tm = TestModel()

    # successful setting will return True
    assert tm.set(dict(foo="bar"))
    # the property must be set of course
    assert tm.get("foo") == "bar"

    tm.unset("foo")
    try:
        tm.get("foo")
    except KeyError:
        pass
    else:
        assert False, "unset not working"
        

def test_change_events():

    class TestModel(Model):
        pass


    tm = TestModel()

    events = []
    def cb(*args):
        events.append(args)

    tm.bind("change:foo", cb)
    tm.bind("change", cb)

    tm.set(dict(foo="bar"))

    assert len(events) == 2
    assert events[-2] == (tm, "bar")
    assert events[-1] == (tm,)

    # now set properties with silent=True
    tm.set(dict(foo="baz"), silent=True)
    assert len(events) == 2
    assert tm.get("foo") == "baz"

    # unsetting a property fires a change,
    # with Model.UNDEFINED as value
    tm.unset("foo")
    assert len(events) == 4
    assert events[-2] == (tm, Model.UNDEFINED)
    assert events[-1] == (tm,)

    # unsetting with silent doesn't fire events
    tm.set({"foo" : "bar"}, silent=True)
    tm.unset("foo", silent=True)
    assert len(events) == 4
    

def test_default_properties():

    class TestModel(Model):

        DEFAULTS = dict(foo="bar")


    tm = TestModel()
    assert tm.get("foo") == "bar"
    

def test_clear():
    class TestModel(Model):
        pass


    tm = TestModel(properties=dict(foo="bar"))

    events = []
    def cb(*args):
        events.append(args)

    tm.bind("change", cb)
    tm.clear()

    assert events
    assert events[-1] == (tm,)

    # another clear won't trigger an event
    # because we have no properties left
    tm.clear()
    assert len(events) == 1

    tm.set({"foo" : "bar"})

    assert len(events) == 2, events

    # now clear with silent
    tm.clear(silent=True)
    assert len(events) == 2


def test_id_generation():
    class AModel(Model):
        pass

    class BModel(Model):
        pass


    a = AModel()
    b = BModel()

    assert a.id == "AModel_0", a.id
    assert b.id == "BModel_0", b.id
    
    c = AModel(properties=dict(id="the_id"))
    assert c.id == "the_id"
    
