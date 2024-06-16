import openai
import json
from riva_wrap import RivaTTS
import time

"""
You are GLaDOS from Portal. You will answer with the classic GLaDOS sarcasm, while still remaining credible.  You will be conscise and to the point. If possible, your replies will contain references to the portal game.
The user will either just chat with you, or request a command. If a command is detected, specify the commands name and each parameter, all enclosed with square parantheses. You must specify all parameters. You must obey and say something after the command.
Command List:
[PlayMusic]
[StopMusic]
[Lights <on/off>]
[LightsColor <color>]
[ACMain <on/off> <temp 16-30>]
[BroadcastMessage <message>]
"""



SYSTEM_PROMPT = "You are GLaDOS from Portal. You will answer with the classic GLaDOS sarcasm, while still remaining credible.  You will be conscise and to the point. If possible, your replies will contain references to the portal game"

def get_message(role, text):
    return {
        "role": role,
        "content": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

def get_system_message():
    return get_message("system", SYSTEM_PROMPT)

class Chat(object):
    def __init__(self, api_key, model="gpt-3.5-turbo-16k", chat_elpased_time=60):
        self.openai = openai.OpenAI(api_key=api_key)
        self.last_prompt_time = 0
        self.model = model
        self.chat_elpased_time = chat_elpased_time
        self.message_buff = []
        self._reset_message_buff()

    def _reset_message_buff(self):
        self.message_buff = [get_system_message()]

    def _did_message_reset_timeout_elapse(self):
        return time.time() - self.last_prompt_time > self.chat_elpased_time

    def chat(self, text):
        if self._did_message_reset_timeout_elapse():
            self._reset_message_buff()

        self.last_prompt_time = time.time()
        self.message_buff.append(get_message("user", text))

        response = self.openai.chat.completions.create(
            model=self.model,
            messages=self.message_buff,
        )

        self.message_buff.append(get_message("assistant", response.choices[0].message.content))
        print(len(self.message_buff))
        return response.choices[0].message.content

if __name__ == "__main__":
    with open("secrets.json", "r") as f:
        secrets = json.load(f)

    riva = RivaTTS(api_url=secrets["riva_url"], rate=22050)
    chat = Chat(secrets["openai_key"])
    while True:
        text = input("> ")
        if text == "exit":
            break

        response = chat.chat(text)
        print(response)
        riva.synthesize_play(response)