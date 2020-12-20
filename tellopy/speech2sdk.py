#!/usr/bin/env python

from tellopy.speech import HotwordDetector
from tellopy.communications.control import Control
from tellopy.communications.video import Video
from tellopy.communications.config import Config


class Speech2sdk:

    cmd_map = {
        'flyback': 'back 100',
        'forward': 'forward 100',
        'lowdown': 'down 100',
        'riseup': 'up 100',
        'sitdown': 'land',
        'takeoff': 'takeoff',
        'turnleft': 'ccw 45',
        'turnright': 'cw 45',
        'backflip': 'flip b',
        'video': 'streamon',
    }

    def __init__(self, test=False):
        self.initialize_control(test)
        self.actions = {
            b'streamon': self.init_video,
        }

    def initialize_control(self, test):
        self.control = None if test else Control().init()

    def init_video(self):
        self.video = Video("udp://%s:%s" %
                           (Config.drone_ip, Config.video_port))
        self.video.start(timeout=600.0, blocking=False)

    def send_command(self, txt):
        txt = txt.lower().replace(' ', '')
        txt = self.cmd_map.get(txt, txt)
        byts = txt.encode('utf-8')
        self.actions.get(byts, lambda: None)()
        if self.control is None:
            return b'ok'
        else:
            return self.control.send(byts)

    def run_hotword_detector(self):
        self.speech = HotwordDetector(lambda x: self.send_command(x))
        self.speech.start()
