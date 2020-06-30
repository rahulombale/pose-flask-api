from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
import io
from pydub import AudioSegment
import wave


def mp3_to_wav(audio_file_name):
    if audio_file_name.split('.')[1] == 'mp3':
        sound = AudioSegment.from_mp3(audio_file_name)
        audio_file_name = audio_file_name.split('.')[0] + '.wav'
        sound.export(audio_file_name, format="wav")


def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate, channels


def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")


def speech_to_text(audio_file_name):
    """
    Transcribe a short audio file using synchronous speech recognition

    Args:
      local_file_path Path to local audio file, e.g. /path/audio.wav
    """

    mp3_to_wav(audio_file_name)

    # The name of the audio file to transcribe

    audio_file_name = audio_file_name.split('.')[0] + '.wav'

    frame_rate, channels = frame_rate_channel(audio_file_name)

    # if channels > 1:

    stereo_to_mono(audio_file_name)

    client = speech_v1.SpeechClient()
    # local_file_path = 'resources/brooklyn_bridge.raw'

    # The language of the supplied audio
    language_code = "en-US"

    # Sample rate in Hertz of the audio data sent
    sample_rate_hertz = 16000

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "language_code": language_code,
        #         "sample_rate_hertz": sample_rate_hertz,
        "encoding": encoding,
    }


    with io.open(audio_file_name, "rb") as f:

        content = f.read()
    audio = {"content": content}
    response = client.recognize(config, audio)
    alternative = None
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]

        print("Transcript: {}".format(alternative.transcript))
    if alternative:
        return alternative.transcript
    else:
        return None


# print(sample_recognize('bad.mp3'))
