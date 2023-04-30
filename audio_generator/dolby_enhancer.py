# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import json
import shutil
import logging
import pathlib
import requests
from requests.auth import HTTPBasicAuth
from time import sleep

logger = logging.getLogger('Main_Logger')
root_dir_path = str(pathlib.Path(__file__).parent.parent) + '/'


def get_api_token():
    app_key = '8vQroENnljJYI9AUqYHhkg=='
    app_secret = 'Ik2PNUG8hiT3eQLvSaSz6abBCuCcqc9AK0MACvUpTBI='
    payload = {'grant_type': 'client_credentials', 'expires_in': 3600}

    logger.info('Getting API token...')

    response = requests.post('https://api.dolby.io/v1/auth/token', data=payload,
                             auth=HTTPBasicAuth(app_key, app_secret))

    response_json = json.loads(response.content)

    return response_json['access_token']


def get_headers():
    headers = {
        'Authorization': f'Bearer {get_api_token()}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    return headers


def upload_file(headers, file_path):
    request_url = 'https://api.dolby.com/media/input'

    dolby_input_path = f'dlb://in/{file_path}'

    body = {
        'url': dolby_input_path,
    }

    response = requests.post(request_url, json=body, headers=headers)
    response.raise_for_status()
    response_json = response.json()
    signed_url = response_json['url']

    logger.info(f'Uploading {file_path} to {signed_url}')

    with open(f'{root_dir_path}{file_path}', "rb") as input_file:
        requests.put(signed_url, data=input_file)

    return dolby_input_path


def initiate_audio_enhancement(headers, file_path, dolby_input_path):
    request_url = 'https://api.dolby.com/media/enhance'

    dolby_output_path = f'dlb://out/{file_path}'

    payload = {
        'input': dolby_input_path,
        'output': dolby_output_path,
        'content': {'type': 'podcast'},
        'audio': {
            'loudness': {
                'enable': True,
                'dialog_intelligence': True
            },
            'dynamics': {
                'range_control': {
                    'enable': True,
                    'amount': 'medium'
                }
            },
            'filter': {
                'dynamic_eq': {
                    'enable': False
                }
            },
            'speech': {
                'sibilance': {'reduction': {
                    'enable': True,
                    'amount': 'high'
                }},
                'plosive': {'reduction': {
                    'enable': True,
                    'amount': 'medium'
                }}
            }
        }
    }

    response = requests.post(request_url, json=payload, headers=headers)
    response.raise_for_status()
    job_id = response.json()['job_id']

    return dolby_output_path, job_id


def check_status(headers, job_id):
    request_url = "https://api.dolby.com/media/enhance"

    params = {
        "job_id": job_id
    }

    response = requests.get(request_url, params=params, headers=headers)
    response.raise_for_status()

    return response.json()['status'], response.json()['progress']


def wait_for_completion(headers, job_id):
    status, progress = check_status(headers, job_id)

    while status != 'Success':
        logger.info(f'Job incomplete. Status: {status}, Progress: {progress}')

        sleep(10)
        status, progress = check_status(headers, job_id)


def download_file(headers, dolby_output_path):
    request_url = 'https://api.dolby.com/media/output'

    output_path = root_dir_path + 'output/final_audio'

    args = {
        'url': dolby_output_path,
    }

    with requests.get(request_url, params=args, headers=headers, stream=True) as response:
        response.raise_for_status()
        response.raw.decode_content = True

        logger.info(f'Downloading file to {output_path}')

        with open(f'{output_path}.wav', "wb") as output_file:
            shutil.copyfileobj(response.raw, output_file)

    return output_path


def request_dolby_audio_enhancement(file_path):
    file = f'{file_path}.wav'

    headers = get_headers()
    dolby_input_path = upload_file(headers, file)
    dolby_output_path, job_id = initiate_audio_enhancement(headers, file, dolby_input_path)
    wait_for_completion(headers, job_id)
    output_file_path = download_file(headers, dolby_output_path)

    return output_file_path
