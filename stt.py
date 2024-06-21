from google.cloud import speech

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
