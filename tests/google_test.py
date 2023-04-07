import google.cloud.texttospeech as tts
import os


credential_path = "/Users/SeverinBurg/Desktop/xPlain/code/assets/google_key.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


def google_text_to_wav(count: int, host_name: str, voice_name: str, text: str):
    language_code = "-".join(voice_name.split('-')[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16, pitch=-2.8)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input, voice=voice_params, audio_config=audio_config
    )

    filename = f'/Users/SeverinBurg/Desktop/xPlain/code/tests/{host_name}_{count}.wav'
    with open(filename, 'wb') as out:
        out.write(response.audio_content)

    return filename


google_text_to_wav(300, 'Giulia', 'en-GB-Neural2-A', "Welcome to our podcast where we discuss "
                                                     "trending topics.")
