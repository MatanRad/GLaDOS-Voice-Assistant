from devices.speaker import Speaker
from byte_fifo import ByteFIFO
import threading
import time

class AsyncPlayer(object):
    def __init__(self, speaker: Speaker, chunk_size=16000*3, sample_rate=16000):
        self._speaker = speaker
        self._lock = threading.Lock()
        self._fifo = ByteFIFO()
        self._chunk_size = chunk_size
        self._running = False
        self._sample_rate = sample_rate
        self._thread = threading.Thread(target=self._run, daemon=True)

    def __del__(self):
        self.stop()

    def _run(self):
        with self._speaker.output_stream(self._sample_rate) as stream:
            while self._running:
                while len(self._fifo) == 0 and self._running:
                    time.sleep(0.1)

                with self._lock:
                    data = self._fifo.get(self._chunk_size)

                while len(data) > 0 and self._running:
                    stream.write(bytes(data[:self._chunk_size]))
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
