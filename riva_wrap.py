#!/usr/bin/env python3
from riva.client.tts import SpeechSynthesisService
from riva.client import Auth
from IPython.display import Audio
from num2words import num2words
import numpy as np
import wave
import pyaudio
import re

class RivaTTS:
    """
    A class that provides text-to-speech functionality using RivaTTS API.

    Attributes:
        SAMPLE_WIDTH (int): The sample width in bytes for the audio data (default: 2).
        NUM_CHANNELS (int): The number of audio channels (default: 1).

    Args:
        api_url (str): The URL of the RivaTTS API (default: "172.24.42.218:50051").
        rate (int): The sample rate in Hz for the audio data (default: 22050).
    """

    SAMPLE_WIDTH = 2
    NUM_CHANNELS = 1
    MAX_CHARACTERS = 400

    def __init__(self, api_url="172.24.42.218:50051", rate=22050):
        """
        Initializes a new instance of the RivaTTS class.

        Args:
            api_url (str): The URL of the RivaTTS API (default: "172.24.42.218:50051").
            rate (int): The sample rate in Hz for the audio data (default: 22050).
        """
        self.s = SpeechSynthesisService(Auth(uri=api_url))
        self.rate = rate

    def _normalize_text(self, text):
        def convert_punctuated(m):
            return num2words(m.group(1).replace(",", ""))
        text = re.sub(r'(\d{0,3}(,\d{3})+)($|\D)', lambda m: f" {convert_punctuated(m)} {m.group(3)}", text)
        text = re.sub(r'\d+', lambda m: f" {num2words(m.group())} ", text)

        text = re.sub(r'([a-zA-Z])\.([a-zA-Z])', lambda m: f"{m.group(1)} dot {m.group(2)}", text)
        text = text.replace("$", " dollars ")
        text = text.replace("%", " percent ")
        text = text.replace("€", " euros ")
        text = text.replace("£", " pounds ")
        text = text.replace("¥", " yen ")
        text = text.replace("₪", " shekels ")
        text = text.replace("*", " asterisk ")
        text = text.replace("@", " at ")
        text = text.replace("’", "'")
        
        text = text.replace("NTFS", "N T F S")
        
        text = text.replace(" °", "degrees")
        text = text.replace("°", " degrees")

        text = re.sub(r'(\s|^)([Mm][Rr]\.)(\s|$)', lambda m: f"{m.group(1)}mister{m.group(3)}", text)
        text = re.sub(r'(\s|^)([Mm][Ss]\.)(\s|$)', lambda m: f"{m.group(1)}miss{m.group(3)}", text)
        text = re.sub(r'(\s|^)([Mm][Rr][Ss]\.)(\s|$)', lambda m: f"{m.group(1)}missus{m.group(3)}", text)

        text = re.sub(r'(\s|^)(USA|usa)(\s|$|\?|!|,)', lambda m: f"{m.group(1)}U S AY{m.group(3)}", text)
        text = re.sub(r'(\s|^)(UK|uk)(\s|$|\?|!|,)', lambda m: f"{m.group(1)}U KAY{m.group(3)}", text)
        
        text = re.sub(r'(\s|^)(AI|ai)(\s|$|\?|!|,|\.)', lambda m: f"{m.group(1)}AY IY{m.group(3)}", text)

        return text
        

    def _split_text(self, text):
            """
            Splits the given text into a list of strings, each with a maximum length of 400 characters.

            Args:
                text (str): The text to split.

            Returns:
                list: The list of split strings.

            Raises:
                ValueError: If it is not possible to split the text.
            """
            if len(text) <= self.MAX_CHARACTERS:
                return [text]

            words = text.split()
            result = []
            current_string = ""
            for word in words:
                if len(current_string) + len(word) + 1 <= self.MAX_CHARACTERS:
                    current_string += word + " "
                else:
                    if not current_string:
                        raise ValueError("Unable to split input string so that it is less than 400 characters.")
                    result.append(current_string.strip())
                    current_string = word + " "

            if not current_string:
                raise ValueError("Unable to split input string so that it is less than 400 characters.")
            result.append(current_string.strip())

            return result

    def synthesize_raw(self, text):
        """
        Synthesizes the given text into raw audio data.

        Args:
            text (str): The text to synthesize.

        Returns:
            bytes: The raw audio data.
        """
        text = self._normalize_text(text)
        texts = self._split_text(text)

        audio_segments = [self.s.synthesize(t, sample_rate_hz=self.rate).audio for t in texts]

        return b"".join(audio_segments)
    
    def synthesize_display(self, text, autoplay=False):
        """
        Synthesizes the given text and returns an Audio object for display.

        Args:
            text (str): The text to synthesize.
            autoplay (bool): Whether to autoplay the audio (default: False).

        Returns:
            Audio: The Audio object for display.
        """
        return Audio(np.frombuffer(self.synthesize_raw(text), dtype=np.int16), rate=self.rate, autoplay=autoplay)

    def synthesize_wave_stream(self, text, stream):
        """
        Synthesizes the given text into a wave file and writes to a stream.

        Args:
            text (str): The text to synthesize.
            filename (str): The filename of the wave file to save.
        """
        f = wave.Wave_write(stream)
        f.setnchannels(self.NUM_CHANNELS)
        f.setsampwidth(self.SAMPLE_WIDTH)
        f.setframerate(self.rate)
        f.writeframes(self.synthesize_raw(text))
        f.close()

    def synthesize_wave_file(self, text, filename):
        """
        Synthesizes the given text and saves the audio as a wave file.

        Args:
            text (str): The text to synthesize.
            filename (str): The filename of the wave file to save.
        """
        with wave.open(filename, "wb") as f:
            f.setnchannels(self.NUM_CHANNELS)
            f.setsampwidth(self.SAMPLE_WIDTH)
            f.setframerate(self.rate)
            f.writeframes(self.synthesize_raw(text))

    def synthesize_play(self, text):
        """
        Synthesizes the given text and plays the audio.

        Args:
            text (str): The text to synthesize.
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=self.NUM_CHANNELS, rate=self.rate, output=True)
        stream.write(self.synthesize_raw(text))
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Text-to-Speech Wrapper")
    parser.add_argument("--stdin", dest="stdin", action="store_const", const=True, default=False, help="Read text from stdin (Otherwise is interactive)")
    parser.add_argument("--api_url", dest="api_url", type=str, help="The URL of the RivaTTS API", default="172.24.42.218:50051")
    parser.add_argument("--rate", dest="rate", type=int, help="The sample rate in Hz for the audio data", default=22050)
    args = vars(parser.parse_args())

    riva_tts = RivaTTS(api_url=args["api_url"], rate=args["rate"])
    if args["stdin"]:
        text = sys.stdin.read()
        riva_tts.synthesize_wave_stream(text, sys.stdout.buffer)
        exit()

    while True:
        text = input("> ")
        riva_tts.synthesize_play(text)