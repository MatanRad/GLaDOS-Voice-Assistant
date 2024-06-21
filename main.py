import json
from chat import Chat
from riva_wrap import RivaTTS
from assistant import Assistant
from wake_word import WakeWordDetector
from devices.mic_wrapper import Microphone

def main():
    with open("secrets.json", "r") as f:
        secrets = json.load(f)

    riva = RivaTTS(api_url=secrets["riva_url"], rate=22050)
    chat = Chat(secrets["openai_key"])
    wake = WakeWordDetector(secrets["picovoice_key"], sample_rate=16000, keyword_paths=["glados_de_windows_v3_0_0.ppn"], model_path="porcupine_params_de.pv")

    assistant = Assistant(chat, riva, wake)
    assistant.run()

if __name__ == "__main__":
    main()
