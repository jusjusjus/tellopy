import numpy as np
from .video import Video


def test_video():
    video = Video("/dev/video0")
    assert video.running is False
    video.start()
    assert video.running is True
    f = video.frame
    assert isinstance(f, np.ndarray) and f.shape[2] == 3, str(f)
    video.stop()
    assert video.running is False
    video.start()
    assert video.running is True
    f = video.frame
    assert isinstance(f, np.ndarray) and f.shape[2] == 3, str(f)
