# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import re
import openai
import random
import logging
import pathlib
import time
import pickle

from helpers import remove_awkward_comma_names, remove_thats_right

logger = logging.getLogger('Main_Logger')
root_dir_path = str(pathlib.Path(__file__).parent) + '/'


def send_request(messages):
    openai.api_key = "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"

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages
    )

    assistant_response = response['choices'][0]['message']['content']

    return assistant_response


def get_instruction():
    n = random.randint(0, 1)
    host_order = [('Giulia', 'Marc'), ('Marc', 'Giulia')]
    hosts = host_order[n]

    instruction = f"You are writing engaging and creative scripts for the podcast " \
                  f"'Sundry Hypes', a daily podcast discussing trending topics. " \
                  f"The co-hosts of this podcast are {hosts[0]} and {hosts[1]}. " \
                  f"I will provide you with a topic and you will provide me with " \
                  f"an extra long script in return. The script needs to discusses all " \
                  f"aspects of the topic in a critical fashion with valid information. Your goal " \
                  f"is to help listeners understand the topic and increase their knowledge. " \
                  f"The text should be formatted as dialog like the below:\n" \
                  f"{hosts[0]}: Welcome to our podcast. My name is {hosts[0]}.\n" \
                  f"{hosts[1]}: And, my name is {hosts[1]}."

    return instruction


# def get_initial_prompt(topic):
#     chained_prompt = f"The topic for the next episode is '{topic}'. " \
#                      f"First, provide me with a list of three important aspects which " \
#                      f"this episode should discuss. Ensure that the three items represent a" \
#                      f"balanced, critical view. The list should be formatted like the below:" \
#                      f"1. Title of the topic" \
#                      f"2. Title of the topic" \
#                      f"3. Title of the topic"
#     return chained_prompt


def get_initial_prompt(topic):
    chained_prompt = f"In the next episode, we want to discuss 'Increase of Private Jet Sales'." \
                     f"More specifically, we want to discuss the fact that the sales have been" \
                     f"constantly increasing over the last two decades and what this means" \
                     f"for the environment in the light of climate change. Take the below article" \
                     f"as an input and inspiration for the script." \
                     f"Private jet sales likely to reach highest ever level this year: https://www.theguardian.com/world/2023/may/01/private-jet-sales-likely-to-reach-highest-ever-level-this-year-report-says" \
                     f"\n\n" \
                     f"First, provide me with a list of three important aspects which " \
                     f"this episode should discuss. Ensure that the three items represent a" \
                     f"balanced, critical view. The list should be formatted like the below:" \
                     f"1. Title of the topic" \
                     f"2. Title of the topic" \
                     f"3. Title of the topic"
    return chained_prompt


def get_intro_prompt():
    intro_prompt = 'Now your task is to write the script. First provide the ' \
                   'dialog which introduces the episode.'

    return intro_prompt


def get_outro_prompt(starting_host):
    outro_prompt = f'Lastly, finish the dialog with an outro. The outro should invite the ' \
                   f'listeners to tune in again. ' \
                   f'Start with {starting_host}.'

    return outro_prompt


def chain_output_in_buffer(requests_buffer, output, prompt, dialog):
    requests_buffer.append({'role': 'assistant', 'content': output})
    requests_buffer.append({'role': 'user', 'content': prompt})
    request_output = send_request(requests_buffer)

    request_output = remove_awkward_comma_names(request_output)
    request_output = remove_thats_right(request_output)

    dialog += request_output + '\n\n'

    return requests_buffer, request_output, dialog


def get_numbered_part_prompt(number_part, content_store, starting_host):
    answer_all_questions_sentence = 'Make sure to answer all questions which a listener might ' \
                                    'potentially have about this aspect.'
    starting_host_sentence = f'Start with {starting_host}. '

    topic = content_store['sections'][f'{number_part}_topic'].title

    if number_part == 1:
        return f'Now continue the dialog discussing first item: {topic}. ' \
               + answer_all_questions_sentence + starting_host_sentence
    elif number_part == 2:
        return f'Continue the dialog with a discussion of the second item: {topic}. ' \
               + answer_all_questions_sentence + starting_host_sentence
    elif number_part == 3:
        return f'Now provide the section of the dialog discussing the third item: {topic}. ' \
               + answer_all_questions_sentence + starting_host_sentence + \
               'Do not provide an outro or any closing statement.'

    raise ValueError('So far only supporting three parts!')


def retrieve_next_host(dialog, female_host_name='Giulia', male_host_name='Marc'):
    last_occurrence_of_female_host = dialog.rfind(female_host_name + ':')
    last_occurrence_of_male_host = dialog.rfind(male_host_name + ':')

    if last_occurrence_of_male_host > last_occurrence_of_female_host:
        return female_host_name
    else:
        return male_host_name


def write_content_store_to_file(content_store):
    logger.info('Saving content store to file...')

    file_path = root_dir_path + f'output/content_store.bin'
    with open(file_path, 'wb') as output_file:
        pickle.dump(content_store, output_file)


def update_content_store(store, section, content):
    lines = content.split('\n')

    if lines[0].startswith('Giulia'):
        store['sections'][section].first_speaker = 'Giulia'
    elif lines[0].startswith('Marc'):
        store['sections'][section].first_speaker = 'Marc'

    if lines[-1].startswith('Giulia'):
        store['sections'][section].last_speaker = 'Giulia'
    elif lines[-1].startswith('Marc'):
        store['sections'][section].last_speaker = 'Marc'

    store['sections'][section].dialog = content

    return store


class Section:
    def __init__(self, name, first_speaker=None, last_speaker=None, dialog='', starts_at=None,
                 ends_at=None, first_verbatim=None, last_verbatim=None, title=None,
                 description=None):
        self.name = name
        self.first_speaker = first_speaker
        self.last_speaker = last_speaker
        self.dialog = dialog
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.first_verbatim = first_verbatim
        self.last_verbatim = last_verbatim
        self.title = title
        self.description = description

def create_content_store(list_of_items, number_of_parts=None):
    lines = list_of_items.split('\n')

    content = {
        'dialog': '',
        'sections': {'introduction': Section(name='introduction')}
    }

    for line in lines:
        line = line.strip()

        for i in range(number_of_parts):
            i += 1

            if line.startswith(f'{i}.'):
                if ':' in line:
                    title = re.sub(r':.*', '', line)
                    description = re.sub(r'^.*: ?', '', line)

                else:
                    title = line
                    description = None

                content['sections'][f'{i}_topic'] = Section(name=f'{i}_topic',
                                                            title=title.replace(f'{i}. ', ''),
                                                            description=description)

    content['sections']['outro'] = Section(name='outro')

    return content


def generate_dialog_based_on_topic(topic):
    logger.info(f'Generating dialog for topic: "{topic}"')

    number_of_parts = 3

    instruction = get_instruction()
    prompt = get_initial_prompt(topic)

    requests_buffer = [
        {'role': 'system', 'content': instruction},
        {'role': 'user', 'content': prompt}
    ]

    list_of_items_to_treat = send_request(requests_buffer)
    content_store = create_content_store(list_of_items_to_treat, number_of_parts)

    requests_buffer, introduction, content_store['dialog'] = chain_output_in_buffer(
        requests_buffer, list_of_items_to_treat, get_intro_prompt(), content_store['dialog'])
    content_store = update_content_store(content_store, 'introduction', introduction)

    time.sleep(60)

    last_part = introduction
    for i in range(number_of_parts):
        next_host = retrieve_next_host(content_store['dialog'])
        requests_buffer, next_part, content_store['dialog'] = chain_output_in_buffer(
            requests_buffer, last_part,
            get_numbered_part_prompt(i + 1, content_store, next_host), content_store['dialog']
        )
        last_part = next_part
        content_store = update_content_store(content_store, f'{i + 1}_topic', next_part)

    time.sleep(60)

    next_host = retrieve_next_host(content_store['dialog'])
    requests_buffer, next_part, content_store['dialog'] = chain_output_in_buffer(
        requests_buffer, last_part, get_outro_prompt(next_host), content_store['dialog'])
    content_store = update_content_store(content_store, 'outro', next_part)

    logger.info(f'Successfully generated dialog with {len(content_store["dialog"])} characters')

    write_content_store_to_file(content_store)
    print(content_store)

    return content_store
