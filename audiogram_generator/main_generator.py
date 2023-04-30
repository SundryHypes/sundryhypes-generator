# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import random
import string
import pathlib

from audiogram_generator.visualisation_generator import AnimationGenerator
from audiogram_generator.captions_generator import generate_video_with_captions

root_dir_path = str(pathlib.Path(__file__).parent.parent) + '/'


def return_host_specific_phrases(name, lines, other_host_name):
    list_of_groups = []

    for line in lines:
        if line.startswith(name):
            tmp_list_of_groups = group_words(line, name)
            list_of_groups.extend(tmp_list_of_groups)
        else:
            if not line.startswith(other_host_name) and not len(line) == 0:
                raise ValueError('Found line of pure content, i.e. not starting with host name!')

    return list_of_groups


def group_words(line, name, min_length_string=17, max_length_string=25):
    words_to_exclude = [f'{name}:', '', '\n']
    list_of_words = line.split(' ')
    grouped_words = ['']
    for word in list_of_words:
        if word in words_to_exclude:
            continue
        last_word_group = grouped_words[-1]
        if len(last_word_group) < min_length_string \
                or len(last_word_group) + len(word) < max_length_string:
            grouped_words[-1] += word if len(last_word_group) == 0 else ' ' + word
        else:
            if len(grouped_words) % 2 == 0:
                grouped_words[-1] += '\n'
            grouped_words.append(word)
    if grouped_words[-1][-1] != '\n':
        grouped_words[-1] += '\n'

    return grouped_words


def write_text_to_file(host_name, text):
    file_path = root_dir_path + f'tmp/text_files/script_{host_name}.txt'
    output_file = open(file_path, "w")
    output_file.write(text)
    output_file.close()

    return file_path


def generate_text_files(content_store):
    giulia, marc = [], []

    for key, section in content_store['sections'].items():
        lines = section['dialog'].split('\n')
        lines = [line.strip() for line in lines]

        list_of_phrases = {'Giulia': return_host_specific_phrases('Giulia', lines, 'Marc'),
                           'Marc': return_host_specific_phrases('Marc', lines, 'Giulia')}

        section['first_verbatim'] = list_of_phrases[section['first_speaker']][0]
        section['last_verbatim'] = list_of_phrases[section['last_speaker']][-1]

        giulia.append('\n'.join(list_of_phrases['Giulia']))
        marc.append('\n'.join(list_of_phrases['Marc']))

    text_file_paths = {'Giulia': write_text_to_file('giulia', '\n'.join(giulia)),
                       'Marc': write_text_to_file('marc', '\n'.join(marc))}

    return text_file_paths, content_store


def generate_audiogram(audio_file_paths, content_store, title, episode_number):
    text_file_paths, content_store = generate_text_files(content_store)
    generator = AnimationGenerator(audio_file_paths['Joined_Mono'], audio_file_paths['Enhanced'])
    visualisation_clip = generator.get_animation_clip()

    generate_video_with_captions(visualisation_clip, audio_file_paths, text_file_paths,
                                 content_store, title, episode_number)

    return text_file_paths
