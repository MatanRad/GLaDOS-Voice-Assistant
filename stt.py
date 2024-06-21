from google.cloud import speech
import threading
from byte_fifo import ByteFIFO

def _requests_generator(stream):
    for chunk in stream:
        yield speech.StreamingRecognizeRequest(audio_content=chunk)

class STT(object):
    def __init__(self):
        self.client = speech.SpeechClient()

    def recognize_stream_command(self, stream) -> str:
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )
        streaming_config = speech.StreamingRecognitionConfig(config=config, single_utterance=True)
        responses = self.client.streaming_recognize(streaming_config, _requests_generator(stream))

        for response in responses:
            for result in response.results:
                if result.is_final:
                    return result.alternatives[0].transcript

class STTAction(object):
    def __init__(self, chunk_size=4096):
        self._stt = STT()
        self.result = None
        self._fifo = ByteFIFO()
        self._chunk_size = chunk_size
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._run, args=(self._chunks_generator(),), daemon=True)
        self._thread.start()

    def handle_chunk(self, chunk):
        with self._lock:
            self._fifo.put(chunk)

    def is_done(self) -> bool:
        return not self._thread.is_alive()

    def _chunks_generator(self):
        while True:
            chunk = None
            with self._lock:
                    chunk = self._fifo.get(self._chunk_size)
            
            if chunk is not None:
                yield bytes(chunk)

    def _run(self, generator) -> str:
        self.result = self._stt.recognize_stream_command(generator)
