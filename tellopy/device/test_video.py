import numpy as np
from .video import Video


def test_video():
    video = Video("/dev/video0")
    assert not video.running
    video.start()
    assert video.running
    f = video.frame
    assert isinstance(f, np.ndarray) and f.shape[2] == 3, str(f)
    video.stop()
    assert not video.running
    video.start()
    assert video.running
    f = video.frame
    assert isinstance(f, np.ndarray) and f.shape[2] == 3, str(f)
