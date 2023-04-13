# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import os
import sys
import time
import logging
import pathlib
import psutil

logger = logging.getLogger('Main_Logger')
root_dir_path = str(pathlib.Path(__file__).parent.parent) + '/'

EOL = '\n'


def send_command(command):
    logger.info(f'>>> {command.strip()}')
    sender_file.write(command + EOL)
    sender_file.flush()


def get_response():
    result = ''
    line = ''

    while True:
        result += line
        line = receiver_file.readline()
        if line == '\n' and len(result) > 0:
            break

    return result


def do_command(command):
    send_command(command)

    response = get_response()
    logger.info(f'<<< {response.strip()}')

    return response


def open_pipes():
    global sender_file, receiver_file

    if 'Audacity' not in (i.name() for i in psutil.process_iter()):
        os.system('open /Applications/Audacity.app')
        logger.info('Waiting for Audacity to start...')
        time.sleep(10)

    sender_name = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
    receiver_name = '/tmp/audacity_script_pipe.from.' + str(os.getuid())

    if not os.path.exists(sender_name):
        logger.info(f'{sender_name} does not exist. Ensure Audacity is running with pipe.')
        sys.exit()

    if not os.path.exists(receiver_name):
        logger.info(f'{receiver_name} does not exist. Ensure Audacity is running with pipe.')
        sys.exit()

    logger.info(f'Audacity pipes ok. – Sender: {sender_name}, Receiver: {receiver_name}')

    sender_file = open(sender_name, 'w')
    receiver_file = open(receiver_name, 'rt')


def close_pipes():
    receiver_file.close()
    sender_file.close()


def request_audacity_audio_enhancement(file_path):
    open_pipes()

    do_command(f'Import2: Filename={root_dir_path}{file_path}.wav')
    do_command('SelectAll')

    eq_setting_macro = open(f'{root_dir_path}assets/audacity_presets/eq_settings.txt', 'r')
    big_voice_macro = open(f'{root_dir_path}assets/audacity_presets/big_voice.txt', 'r')

    for command in eq_setting_macro:
        do_command(command)

    for command in big_voice_macro:
        do_command(command)

    export_path = 'output/audacity_enhancement'
    do_command(f'Export2: Filename={root_dir_path}{export_path}.wav NumChannels=2')

    do_command('TrackClose')
    do_command('Exit')

    close_pipes()

    return export_path
