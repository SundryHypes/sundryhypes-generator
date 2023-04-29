from audio_generator.speech_synthesiser import google_text_to_wav

import random


def text_ssml_converter(text):
    pause_paragraph = random.randint(650, 800)
    pause_full_stop = random.randint(450, 550)
    pause_comma = random.randint(175, 250)

    ssml = text.replace('. ', f'. <break time="{pause_full_stop}ms"/> ')
    ssml = ssml.replace(', ', f', <break time="{pause_comma}ms"/> ')

    ssml = f'<speak>{ssml}<break time="{pause_paragraph}ms"/></speak>'

    return ssml


text = "Welcome to our podcast where we discuss trending topics. Today, we will discuss rain."

google_text_to_wav(300, 'marc', text_ssml_converter(text))

# google_text_to_wav(300, 'marc', "Welcome to our podcast where we discuss trending "
#                                 "topics. Today, we will discuss rain.")
