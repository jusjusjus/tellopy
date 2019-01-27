
from threading import Timer

class AbortTimer(Timer):

    def __init__(self, timeout):
        super().__init__(timeout, self.set_abort)
        self.abort = False
        self.start()

    def set_abort(self):
        self.abort = True
