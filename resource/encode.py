# Import the base64 encoding library.
import base64


# Pass the audio data to an encoding function.
def encode_audio(audio):
    file = open(audio, "rb")
    binary_data = file.read()
    file.close()
    return base64.b64encode(binary_data)


def decode_audio_write_file(base64String):
    file = base64.b64decode(base64String)
    f = open('resource/abc.mp3', "wb")
    f.write(file)
