from typing import Optional
from devices.mic_wrapper import Microphone
from stt import STTAction
from wake_word import WakeWordDetector
from chat import Chat
from riva_wrap import RivaTTS

class Assistant(object):
    def __init__(self, chat: Chat, tts: RivaTTS, wake_word_detector: WakeWordDetector, mic_name: str = None):
        self.mic = Microphone(mic_name)
        self.wake = wake_word_detector
        self.current_stt: STTAction = None
        self.chat = chat
        self.tts = tts
    
    def _update_stt(self, chunk) -> Optional[str]:
        if self.current_stt is not None:
            if self.current_stt.is_done():
                result = self.current_stt.result
                print(f"[STT] Result: {result}")
                self.current_stt = None
                return result
            
            self.current_stt.handle_chunk(chunk)
        return None

    def handle_stt(self, text: str):
        resp = self.chat.chat(text)
        print(f"[Chat] Response: {resp}")
        self.tts.synthesize_play(resp)

    def run(self):
        with self.mic.record(chunk_size=512) as mic_stream:
            for chunk in mic_stream:
                stt_text = self._update_stt(chunk)
                if stt_text is not None:
                    self.handle_stt(stt_text)

                if self.wake.detect(chunk):
                    print("[Wake Word] Detected")
                    if self.current_stt is not None:
                        print("[Wake Word] Ditching current STT")
                    self.current_stt = STTAction()
