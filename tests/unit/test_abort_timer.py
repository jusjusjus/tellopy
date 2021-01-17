from time import sleep, time
from tellopy.device.abort_timer import AbortTimer
import pytest


@pytest.mark.parametrize("waiting_time", [0.1,  0.5])
def test_abort_timer(waiting_time):
    t0 = time()
    timer = AbortTimer(waiting_time)
    sleep(waiting_time / 2)
    assert timer.abort is False, "%.2g seconds passed" % (time() - t0)
    sleep(waiting_time / 2)
    assert timer.abort is True, "%.2g seconds passed" % (time() - t0)
