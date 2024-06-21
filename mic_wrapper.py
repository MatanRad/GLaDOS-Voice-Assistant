from typing import Generator, List
from contextlib import contextmanager
import pyaudio

class Microphone(object):
    def _get_mics(self):
        device_count = self._pyaudio.get_device_count()
        devices = [self._pyaudio.get_device_info_by_index(i) for i in range(device_count)]
        input_devices = [i for i in devices if i["maxInputChannels"] > 0]
        return input_devices
    
    def _get_mic_by_name(self, name: str):
        mics = self._get_mics()
        matching_candidates = [m for m in mics if name == m["name"]]
        
        if len(matching_candidates) == 1:
            return matching_candidates[0]

        contained_candidates = [m for m in mics if name in m["name"]]
        if len(contained_candidates) > 1:
            raise ValueError(f"Multiple microphones contain the name '{name}'.")
        
        if len(contained_candidates) == 1:
            return contained_candidates[0]
        
        raise ValueError(f"No microphone found with the name '{name}'.")
    
    def _get_default_mic(self):
        return self._pyaudio.get_default_input_device_info()

    def __init__(self, mic_name=None):
        self._pyaudio = pyaudio.PyAudio()
        self._mic_info = self._get_default_mic() if mic_name is None else self._get_mic_by_name(mic_name)

    @contextmanager
    def mic_stream(self, rate=16000, chunk_size=1024, format=pyaudio.paInt16) -> Generator[pyaudio.Stream, None, None]:
        stream = self._pyaudio.open(format=format, channels=1, rate=rate, input=True, frames_per_buffer=chunk_size, input_device_index=self._mic_info["index"])
        yield stream
        stream.stop_stream()
        stream.close()
    
    @contextmanager
    def record(self, rate=16000, chunk_size=4096, format=pyaudio.paInt16) -> Generator[bytes, None, None]:
        stopped = False
        def _read_chunks(stream):
            while not stopped:
                yield stream.read(chunk_size)
        
        with self.mic_stream(rate=rate, chunk_size=chunk_size, format=format) as stream:
            yield _read_chunks(stream)

        stopped = True




