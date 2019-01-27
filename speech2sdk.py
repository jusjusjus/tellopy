
import os
import glob
import argparse
from threading import Thread
from datetime import datetime

import numpy as np
from time import sleep
from tellopy.speech import PorcupineDemo
from tellopy.communications.control import Control

control = None

def init_drone():
    global control
    control = Control()
    control.init()

drone_ip = '192.168.10.1'
app_cmd_addr = (drone_ip, 8889)
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

def send_command(txt, test=False):
    print(cmd_map)
    txt = txt.lower().replace(' ', '')
    txt = cmd_map.get(txt, txt)
    print(txt)
    if txt is None:
        return True
    byts = txt.encode('utf-8')
    if test:
        print('sending', byts)
    else:
        control.send(byts)
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--keyword_file_dir', help='dirname to keyword files', type=str, default='./resources/porcupine')
    parser.add_argument('--sensitivities', help='detection sensitivity [0, 1]', default=0.5)
    parser.add_argument('--input_audio_device_index', help='index of input audio device', type=int, default=None)
    parser.add_argument( '--output_path', help='absolute path to where recorded audio will be stored. If not set, it will be bypassed.',
        type=str, default=None)
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--show_audio_devices_info', action='store_true')
    args = parser.parse_args()

    if not args.test:
        init_drone()

    if args.show_audio_devices_info:
        PorcupineDemo.show_audio_devices_info()
    else:
        keyword_file_paths = glob.glob(os.path.join(args.keyword_file_dir, '*'))
        if isinstance(args.sensitivities, float):
            sensitivities = [args.sensitivities] * len(keyword_file_paths)
        else:
            sensitivities = [float(x) for x in args.sensitivities.split(',')]

        def react(detected_word):
            print('[%s] detected %s' % (str(datetime.now()), detected_word))

        # initializing tello
        response = send_command('command', test=args.test)
        # if not response == 'ok':
        #     raise IOError("Unable to connect to Tello drone")

        # initialize and listen
        PorcupineDemo(lambda x: send_command(x, test=args.test),
            keyword_file_paths=keyword_file_paths,
            sensitivities=sensitivities,
            output_path=args.output_path,
            input_device_index=args.input_audio_device_index).run()
