from typing import Generator, List
from contextlib import contextmanager
import wave
from .pyaudio_wrap import PyAudioDevice
import pyaudio

class Speaker(PyAudioDevice):
    def _get_default(self):
        return self._pyaudio.get_default_output_device_info()

    def __init__(self, name=None):
        super().__init__(name=name)

    def _get_devices(self) -> List[dict]:
        devices = super()._get_devices()
        return [d for d in devices if d["maxOutputChannels"] > 0]

    @contextmanager
    def output_stream(self, rate=16000, chunk_size=1024, channels=1, format=pyaudio.paInt16) -> Generator[pyaudio.Stream, None, None]:
        stream = self._pyaudio.open(format=format, channels=channels, rate=rate, output=True, frames_per_buffer=chunk_size, output_device_index=self._dev_info["index"])
        yield stream
        stream.stop_stream()
        stream.close()


    def play(self, samples, rate=16000, chunk_size=4096, format=pyaudio.paInt16):
        with self.output_stream(rate=rate, chunk_size=chunk_size, format=format) as stream:
            stream.write(samples)

    def play_wave(self, path):
        with wave.open(path, 'rb') as wf:
            with self.output_stream(rate=wf.getframerate(), 
                                    channels = wf.getnchannels(), 
                                    chunk_size=512, 
                                    format=self._pyaudio.get_format_from_width(wf.getsampwidth())) as stream:
                data = wf.readframes(512)
                while data:
                    stream.write(data)
                    data = wf.readframes(512)
