#
# Copyright 2018 Picovoice Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse
import os
import glob
import platform
import struct
import sys
from datetime import datetime
from threading import Thread

import numpy as np
import pyaudio
import soundfile

from third_party.porcupine import Porcupine


class PorcupineDemo(Thread):
    """
    Demo class for wake word detection (aka Porcupine) library. It creates an input audio stream from a microphone,
    monitors it, and upon detecting the specified wake word(s) prints the detection time and index of wake word on
    console. It optionally saves the recorded audio into a file for further review.
    """

    def __init__(
            self,
            callback,
            keyword_file_paths,
            sensitivities,
            input_device_index=None,
            output_path=None):

        """
        Constructor.

        :param keyword_file_paths: List of absolute paths to keyword files.
        :param sensitivities: Sensitivity parameter for each wake word. For more information refer to
        'include/pv_porcupine.h'. It uses the
        same sensitivity value for all keywords.
        :param input_device_index: Optional argument. If provided, audio is recorded from this input device. Otherwise,
        the default audio input device is used.
        :param output_path: If provided recorded audio will be stored in this location at the end of the run.
        """

        super().__init__()

        self._keyword_file_paths = keyword_file_paths
        self._sensitivities = sensitivities
        self._input_device_index = input_device_index
        self._callback = callback

        self._output_path = output_path
        if self._output_path is not None:
            self._recorded_frames = []

    def run(self):
        """
         Creates an input audio stream, initializes wake word detection (Porcupine) object, and monitors the audio
         stream for occurrences of the wake word(s). It prints the time of detection for each occurrence and index of
         wake word.
         """

        keyword_names = [
            os.path.basename(x).replace('.ppn', '').replace('_tiny', '').split('_')[0]
            for x in self._keyword_file_paths
        ]

        print('listening for:')
        for keyword_name, sensitivity in zip(keyword_names, sensitivities):
            print('- %s (sensitivity: %f)' % (keyword_name, sensitivity))

        porcupine = None
        pa = None
        audio_stream = None
        try:
            porcupine = Porcupine(
                keyword_file_paths=self._keyword_file_paths,
                sensitivities=self._sensitivities)

            pa = pyaudio.PyAudio()
            audio_stream = pa.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=porcupine.frame_length,
                input_device_index=self._input_device_index)

            while True:
                pcm = audio_stream.read(porcupine.frame_length)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

                if self._output_path is not None:
                    self._recorded_frames.append(pcm)

                result = porcupine.process(pcm)
                if result >= 0:
                    self._callback(keyword_names[result])

        except KeyboardInterrupt:
            print('stopping ...')
        finally:
            if porcupine is not None:
                porcupine.delete()

            if audio_stream is not None:
                audio_stream.close()

            if pa is not None:
                pa.terminate()

            if self._output_path is not None and len(self._recorded_frames) > 0:
                recorded_audio = np.concatenate(self._recorded_frames, axis=0).astype(np.int16)
                soundfile.write(self._output_path, recorded_audio, samplerate=porcupine.sample_rate, subtype='PCM_16')

    _AUDIO_DEVICE_INFO_KEYS = ['index', 'name', 'defaultSampleRate', 'maxInputChannels']

    @classmethod
    def show_audio_devices_info(cls):
        """ Provides information regarding different audio devices available. """

        pa = pyaudio.PyAudio()

        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            print(', '.join("'%s': '%s'" % (k, str(info[k])) for k in cls._AUDIO_DEVICE_INFO_KEYS))

        pa.terminate()


def _default_library_path():
    return os.path.join(os.path.dirname(__file__), 'libpv_porcupine.so')


from time import sleep
import logging
logging.basicConfig(level=logging.DEBUG)

from tellopy.control import UDPSocket

command_sock = None

def init_drone():
    global command_sock
    command_sock = UDPSocket(port=8889, listen=False, name='cmd')

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
    if txt is None:
        return True
    byts = txt.encode('utf-8')
    if test:
        print('sending', byts)
    else:
        command_sock.send(app_cmd_addr, byts)
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
