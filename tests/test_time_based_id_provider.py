import time
from wirbelsturm.tornado import TimeBasedIdProvider



def test_incremental_ids():
    """
    Tests that if concurrent access below the timer resolution
    occures, we still get subsequent ids.
    """
    now = time.time()
    def fake_time():
        return now
    
    idp = TimeBasedIdProvider(fake_time)
    assert idp.next() != idp.next()


def test_cookie_formatting():
    idp = TimeBasedIdProvider()

    current = idp.current
    cookie = idp.to_cookie(current)
    assert current == idp.from_cookie(cookie)

    # also, make sure that this works for the smallest
    # increment
    next = idp.next(current)
    cookie = idp.to_cookie(next)
    assert next == idp.from_cookie(cookie)
