from mic_wrapper import Microphone
import numpy as np
import pvporcupine as pv

class WakeWordDetector(object):
    def __init__(self, access_key, sample_rate, model_path=None, keyword_paths=None, sensitivities=None):
        self._porcupine = pv.create(access_key=access_key, model_path=model_path, keyword_paths=keyword_paths, sensitivities=sensitivities)
        if sample_rate != self._porcupine.sample_rate:
            raise ValueError(f"[Wake Word] Mismatched sample rate. Expected {self._porcupine.sample_rate} but received {sample_rate}.")

    def detect(self, pcm):
        return self._porcupine.process(np.frombuffer(pcm, dtype=np.int16)) >= 0
