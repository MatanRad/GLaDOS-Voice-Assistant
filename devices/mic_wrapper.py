from typing import Generator, List
from contextlib import contextmanager
from .pyaudio_wrap import PyAudioDevice
import pyaudio

class Microphone(PyAudioDevice):
    def _get_default(self):
        return self._pyaudio.get_default_input_device_info()

    def __init__(self, mic_name=None):
        super().__init__(name=mic_name)

    def _get_devices(self) -> List[dict]:
        devices = super()._get_devices()
        return [d for d in devices if d["maxInputChannels"] > 0]

    @contextmanager
    def mic_stream(self, rate=16000, chunk_size=1024, format=pyaudio.paInt16) -> Generator[pyaudio.Stream, None, None]:
        stream = self._pyaudio.open(format=format, channels=1, rate=rate, input=True, frames_per_buffer=chunk_size, input_device_index=self._dev_info["index"])
        yield stream
        stream.stop_stream()
        stream.close()
    
    @contextmanager
    def record(self, rate=16000, chunk_size=4096, format=pyaudio.paInt16):
        stopped = False
        def _read_chunks(stream):
            while not stopped:
                yield stream.read(chunk_size)
        
        with self.mic_stream(rate=rate, chunk_size=chunk_size, format=format) as stream:
            yield _read_chunks(stream)

        stopped = True




