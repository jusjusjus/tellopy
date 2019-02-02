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

from os.path import join, dirname, basename
import sys
from glob import glob
import struct
import argparse
import platform
from threading import Thread
from datetime import datetime

import pyaudio
import soundfile
import numpy as np

from .porcupine import Porcupine


class HotwordDetector(Thread):
    """ Demo class for wake word detection (aka Porcupine) library. It creates
    an input audio stream from a microphone, monitors it, and upon detecting
    the specified wake word(s) prints the detection time and index of wake word
    on console. It optionally saves the recorded audio into a file for further
    review.  """

    keyword_file_dir = join(dirname(__file__), 'resources')

    def __init__(self, callback, sensitivities=0.5, input_device_index=None):

        """
        Constructor.

        :param sensitivities: Sensitivity parameter for each wake word. For more information refer to
        'include/pv_porcupine.h'. It uses the
        same sensitivity value for all keywords.
        :param input_device_index: Optional argument. If provided, audio is recorded from this input device. Otherwise,
        the default audio input device is used.
        """

        super().__init__()

        self.input_device_index = input_device_index
        self.callback = callback
        self.keyword_file_paths = glob(join(self.keyword_file_dir, '*.ppn'))
        if isinstance(sensitivities, float):
            self.sensitivities = [sensitivities] * len(self.keyword_file_paths)
        else:
            assert len(self.sensitivities) == len(self.keyword_file_paths)

    def run(self):
        """ Creates an input audio stream, initializes wake word detection
        (Porcupine) object, and monitors the audio stream for occurrences of
        the wake word(s). It prints the time of detection for each occurrence
        and index of wake word.  """

        keyword_names = [
            basename(x).replace('.ppn', '').replace('_tiny', '').split('_')[0]
            for x in self.keyword_file_paths
        ]

        print('listening for:')
        for keyword_name, sensitivity in zip(keyword_names, self.sensitivities):
            print('- %s (sensitivity: %f)' % (keyword_name, sensitivity))

        pa = None
        porcupine = None
        audio_stream = None
        try:
            porcupine = Porcupine(
                keyword_file_paths=self.keyword_file_paths,
                sensitivities=self.sensitivities)

            pa = pyaudio.PyAudio()
            audio_stream = pa.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=porcupine.frame_length,
                input_device_index=self.input_device_index)

            while True:
                pcm = audio_stream.read(porcupine.frame_length)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

                result = porcupine.process(pcm)
                if result >= 0:
                    self.callback(keyword_names[result])

        except KeyboardInterrupt:
            print('stopping ...')
        finally:
            if porcupine is not None:
                porcupine.delete()

            if audio_stream is not None:
                audio_stream.close()

            if pa is not None:
                pa.terminate()

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
    return join(dirname(__file__), 'libpv_porcupine.so')
