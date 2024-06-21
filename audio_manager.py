from mic_wrapper import Microphone
from stt import STT, STTAction
from wake_word import WakeWordDetector
import json

with open("secrets.json", "r") as f:
    secrets = json.load(f)

mic = Microphone()
stt = STT()
wake = WakeWordDetector(access_key=secrets["picovoice_key"], sample_rate=16000, model_path="porcupine_params_de.pv", keyword_paths=["glados_de_windows_v3_0_0.ppn"], sensitivities=[0.5])

current_stt: STTAction = None
with mic.record(chunk_size=512) as stream:
    for chunk in stream:
        if current_stt is not None:
            if current_stt.is_done():
                print("[STT] Done")
                print(f"[STT] Result: {current_stt.result}")
                current_stt = None
            else:
                current_stt.handle_chunk(chunk)


        if not wake.detect(chunk):
            continue

        print("[Wake Word] Detected")
        if current_stt is not None:
            print("Ditching current STT")
        current_stt = STTAction()

    command = stt.recognize_stream_command(stream)
    print(f"Command: {command}")