
import argparse

from tellopy.speech import HotwordDetector  
from tellopy.communications.control import Control
from tellopy.speech2sdk import Speech2sdk

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
}

def send_command(txt, control):
    print(cmd_map)
    txt = txt.lower().replace(' ', '')
    txt = cmd_map.get(txt, txt)
    byts = txt.encode('utf-8')
    if control is None:
        print('sending', byts)
        return 'ok'
    else:
        return control.send(byts)

parser = argparse.ArgumentParser()
parser.add_argument('--test', action='store_true')
args = parser.parse_args()

speech_control = Speech2sdk(args.test)
speech_control.run_hotword_detector()
