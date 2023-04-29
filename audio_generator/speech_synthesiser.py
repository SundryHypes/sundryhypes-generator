# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import os
import random
import logging
import pathlib
import google.cloud.texttospeech as tts
from pydub import AudioSegment

from audio_generator.audacity_enhancer import request_audacity_audio_enhancement
from audio_generator.dolby_enhancer import request_dolby_audio_enhancement

logger = logging.getLogger('Main_Logger')
root_dir_path = str(pathlib.Path(__file__).parent.parent) + '/'

credential_path = f'{root_dir_path}assets/google_key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


def text_to_ssml_converter(text):
    global ssml_text

    short_pause = random.randint(175, 250)
    long_pause = random.randint(450, 550)
    extra_long_pause = random.randint(750, 900)

    punctuation_signs = [',', ':']
    for sign in punctuation_signs:
        ssml_text = text.replace('{sign} ', f'{sign} <break time="{short_pause}ms"/> ')

    punctuation_signs = ['.', ';', '!', '?']
    for sign in punctuation_signs:
        ssml_text = text.replace(f'{sign} ', f'{sign} <break time="{long_pause}ms"/> ')


    ssml_text = f'<speak>{ssml_text}<break time="{extra_long_pause}ms"/></speak>'

    return ssml_text


def google_text_to_wav(count: int, host_name: str, text: str):
    logger.info(f'Synthesising "{text}"')

    if host_name == 'giulia':
        voice_name = 'en-GB-Neural2-A'
        speaking_rate = 0.93
        pitch = -2.8
    elif host_name == 'marc':
        # voice_name = 'en-GB-News-K'
        voice_name = 'en-GB-Wavenet-B'
        speaking_rate = 0.89
        pitch = -0.8
    else:
        ValueError(f'Unknown host for Google TTS: {host_name}')

    language_code = "-".join(voice_name.split('-')[:2])
    text_input = tts.SynthesisInput(ssml=text_to_ssml_converter(text))
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(
        audio_encoding=tts.AudioEncoding.LINEAR16, pitch=pitch, speaking_rate=speaking_rate,
        effects_profile_id=['large-home-entertainment-class-device']
    )

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input, voice=voice_params, audio_config=audio_config
    )

    filename = f'{root_dir_path}tmp/audio_files/{host_name}_{count}.wav'
    with open(filename, 'wb') as out:
        out.write(response.audio_content)

    return filename


def split_dialogue_into_lines(dialogue):
    lines = dialogue.split('\n')

    return lines


def request_audio_file_for_each_line(lines):
    wav_files = []
    count = 1

    for line in lines:
        line.strip()

        if line.startswith('Giulia'):
            name_stripped_line = line.split(' ', 1)[1]

            filename = google_text_to_wav(count, 'giulia', name_stripped_line)

            wav_files.append(filename)
            count += 1

        elif line.startswith('Marc'):
            name_stripped_line = line.split(' ', 1)[1]

            filename = google_text_to_wav(count, 'marc', name_stripped_line)

            wav_files.append(filename)
            count += 1

    return wav_files


def combine_audio_files(list_of_files):
    logger.info(f'Combining {len(list_of_files)} audio files')

    frame_rate = 44100
    channels = 2
    audio_format = 'wav'

    giulia = AudioSegment.empty().set_frame_rate(frame_rate)
    giulia += AudioSegment.silent(duration=2000, frame_rate=frame_rate)

    marc = AudioSegment.empty().set_frame_rate(frame_rate)
    marc += AudioSegment.silent(duration=2000, frame_rate=frame_rate)

    for i, file in enumerate(list_of_files):
        segment = AudioSegment.from_file(file, audio_format)
        if i == len(list_of_files) - 1:
            if 'giulia' in file:
                giulia += segment
            elif 'marc' in file:
                marc += segment

        else:
            if 'giulia' in file:
                giulia += segment
                marc += AudioSegment.silent(duration=len(segment), frame_rate=frame_rate)
            elif 'marc' in file:
                giulia += AudioSegment.silent(duration=len(segment), frame_rate=frame_rate)
                marc += segment

    giulia_all_right = giulia.pan(+1.0)
    marc_all_left = marc.pan(-1.0)

    joined_mono = marc_all_left.overlay(giulia_all_right)
    combined = marc.overlay(giulia)
    combined = combined.set_channels(channels)

    filepaths = {'Combined': '/output/dialog',
                 'Joined_Mono': '/tmp/audio_files/joined_mono',
                 'Giulia': '/tmp/audio_files/giulia_combined',
                 'Marc': '/tmp/audio_files/marc_combined'}

    combined.export(f'.{filepaths["Combined"]}.wav', format=audio_format)
    joined_mono.export(f'.{filepaths["Joined_Mono"]}.wav', format=audio_format)
    giulia.export(f'.{filepaths["Giulia"]}.wav', format=audio_format)
    marc.export(f'.{filepaths["Marc"]}.wav', format=audio_format)

    return filepaths


def convert_dialogue_to_audio(dialogue):
    logger.info(f'Starting synthesiser...')

    split_lines = split_dialogue_into_lines(dialogue)
    list_of_files = request_audio_file_for_each_line(split_lines)
    audio_file_paths = combine_audio_files(list_of_files)

    audio_file_paths['Audacity'] = request_audacity_audio_enhancement(audio_file_paths['Combined'])
    audio_file_paths['Enhanced'] = request_dolby_audio_enhancement(audio_file_paths['Audacity'])

    return audio_file_paths
