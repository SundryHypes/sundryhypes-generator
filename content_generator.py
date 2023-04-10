# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import openai
import logging

logger = logging.getLogger('Main_Logger')


def send_request(messages):
    openai.api_key = "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"

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages
    )

    assistant_response = response['choices'][0]['message']['content']

    return assistant_response


def get_instruction():
    instruction = "You are a writer who writes scripts for podcasts. You will develop an engaging " \
                  "and creative script for the podcast 'Sundry Hypes', a daily podcast which " \
                  "discusses trending topics. The hosts of this podcast are Giulia and Marc. I will " \
                  "provide you with a topic and your task is to write an extra long script which " \
                  "discusses all aspects of the topic and presents valid information. Your goal is " \
                  "to help listeners come away from the podcast episode with increased knowledge and " \
                  "insight into the topic. Thus, it is important that your script is comprehensive " \
                  "and answers any question which a listener might have about the topic. The text " \
                  "should be formatted as dialogue like the below:\n" \
                  f"Marc: Welcome to our podcast. My name is Marc.\n" \
                  f"Giulia: And, my name is Giulia."

    return instruction


def get_initial_prompt(topic):
    chained_prompt = f"The topic for the next episode is '{topic}'. " \
                     f"First provide me with a list of the three most important " \
                     f"aspects which this episode must discuss."
    return chained_prompt


def get_intro_prompt():
    intro_prompt = 'Now your task is to write the script. First provide the ' \
                   'dialogue which introduces the episode.'

    return intro_prompt


def get_outro_prompt(starting_host):
    outro_prompt = f'Lastly, finish the dialogue with an outro. The outro should contain a ' \
                   f'summary of the episode and invite the listeners to tune in again. ' \
                   f'Start with {starting_host}.'

    return outro_prompt


def chain_output_in_buffer(requests_buffer, output, prompt, dialogue):
    requests_buffer.append({'role': 'assistant', 'content': output})
    requests_buffer.append({'role': 'user', 'content': prompt})
    request_output = send_request(requests_buffer)
    dialogue += request_output + '\n\n'

    return requests_buffer, request_output, dialogue


def get_numbered_part_prompt(number_part, starting_host):
    starting_host_sentence = f'Start with {starting_host}. '
    if number_part == 1:
        return 'Now continue the dialogue discussing the first item. '\
               + starting_host_sentence
    elif number_part == 2:
        return 'Continue the dialogue with a discussion of the second item. '\
               + starting_host_sentence
    elif number_part == 3:
        return 'Now provide the section of the dialogue discussing the third item. '\
               + starting_host_sentence + 'Do not provide an outro or any closing statement.'

    raise ValueError('So far only supporting three parts!')


def retrieve_next_host(dialogue, female_host_name='Giulia', male_host_name='Marc'):
    last_occurrence_of_female_host = dialogue.rfind(female_host_name + ':')
    last_occurrence_of_male_host = dialogue.rfind(male_host_name + ':')

    if last_occurrence_of_male_host > last_occurrence_of_female_host:
        return female_host_name
    else:
        return male_host_name


def generate_dialogue_based_on_topic(topic):
    logger.info(f'Generating dialogue for topic: "{topic}"')

    dialogue = ''

    instruction = get_instruction()
    prompt = get_initial_prompt(topic)

    requests_buffer = [
        {'role': 'system', 'content': instruction},
        {'role': 'user', 'content': prompt}
    ]

    list_of_items_to_treat = send_request(requests_buffer)

    requests_buffer, introduction, dialogue = chain_output_in_buffer(
        requests_buffer, list_of_items_to_treat, get_intro_prompt(), dialogue)

    last_part = introduction
    number_of_parts = 3
    for i in range(number_of_parts):
        next_host = retrieve_next_host(dialogue)
        requests_buffer, next_part, dialogue = chain_output_in_buffer(
            requests_buffer, last_part, get_numbered_part_prompt(i + 1, next_host), dialogue
        )
        last_part = next_part

    next_host = retrieve_next_host(dialogue)
    requests_buffer, next_part, dialogue = chain_output_in_buffer(
        requests_buffer, last_part, get_outro_prompt(next_host), dialogue)

    logger.info(f'Successfully generated dialogue with {len(dialogue)} characters')

    return dialogue
