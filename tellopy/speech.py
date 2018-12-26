
import time
import logging
import threading
import speech_recognition

speech_recognition.Microphone.get_pyaudio()

class Speech(speech_recognition.Recognizer):

    logger = logging.getLogger(name="Speech")

    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_time = time.time()
        self.continue_listening = False
        self.audio_source = speech_recognition.Microphone()
        self.text_processing_fn = self._default_processor if callback is None else callback
        self.listen_speak_lock = threading.Lock()

    def OnStartSay(self, name):
        self.listen_speak_lock.acquire()

    def OnFinishedSay(self, name, completed):
        self.listen_speak_lock.release()

    # Thread function
    def _default_processor(self, text):
        self.logger.debug("recognized utterance '%s'"%text)
        return True

    def start_listening(self):
        if self.continue_listening: # already listening
            return
        self.continue_listening = True
        self.listener = threading.Thread(name='listener', target=self.listen_and_recognize)
        self.listener.start()

    def stop_listening(self):
        self.continue_listening = False
        self.listener.join()

    def recognize(self, audio):
        for recognize in [#self.recognize_google,
                          #self.recognize_bing,
                          self.recognize_sphinx]:
            try:
                self.logger.debug("using {}".format(recognize.__name__))
                recognized_text = recognize(audio)
                break
            except Exception as e:
                print('error using %s:'%recognize.__name__, e)
        else:
            self.logger.debug("No recognizer available")
            return None
        return recognized_text

    def listen_and_recognize(self):
        while self.continue_listening:
            self.listen_speak_lock.acquire()
            self.logger.debug("listening..")
            with self.audio_source as source:
                self.adjust_for_ambient_noise(source)
                audio = self.listen(source, timeout=None, phrase_time_limit=5.0)
            self.listen_speak_lock.release()
            recognized_text = self.recognize(audio)
            if recognized_text is not None:
                self.continue_listening = self.text_processing_fn(recognized_text)
            self.logger.debug("I think you said '{}'".format(recognized_text))
            time.sleep(0.3)

    def adjust_for_ambient_noise(self, source):
        this_time = time.time()
        if this_time - self.last_time > 10.: # sec
            super().adjust_for_ambient_noise(source)
            self.last_time = this_time
