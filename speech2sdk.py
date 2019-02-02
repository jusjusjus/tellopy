
import argparse

# connect to mock drone
from tellopy.communications.config import Config
Config.drone_ip = '127.0.0.1'
Config.controller_port = 12345

from tellopy.speech import HotwordDetector  
from tellopy.speech2sdk import Speech2sdk
from tellopy.communications.control import Control

# control = Control().init()
# control.send(b'streamon')

parser = argparse.ArgumentParser()
parser.add_argument('--test', action='store_true')
args = parser.parse_args()

speech_control = Speech2sdk(args.test)
speech_control.run_hotword_detector()
