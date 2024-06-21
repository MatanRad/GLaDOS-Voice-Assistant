from speaker import Speaker
from byte_fifo import ByteFifo
import threading
import pyaudio

class AsyncPlayer(object):
    def __init__(self, speaker: Speaker, chunk_size=4000):
        self._speaker = speaker
        self._lock = threading.Lock()
        self._fifo = ByteFifo()
        self._chunk_size = chunk_size
        self._running = False
        self._thread = threading.Thread(target=self._run)

    def _run(self):
        while self._running:
            with self._lock:
                data = self._fifo.get(self._chunk_size)

            while len(data) > 0 and self._running:
                self._speaker.play(bytes(data[:self._chunk_size]))
                data = data[self._chunk_size:]
    
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join()

    def clear(self):
        with self._lock:
            self._fifo.clear()

    def is_playing(self):
        with self._lock:
            return len(self._fifo) > 0
    
    def play(self, samples):
        with self._lock:
            self._fifo.put(samples)
