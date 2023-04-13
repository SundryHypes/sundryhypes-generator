# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import pathlib
import os

from config import set_up_logging
from ideas_finder import get_title_of_todays_trending_wiki_articles
from archive.archive_maintainer import check_if_topic_discussed_recently, add_entry_to_record
from content_generator import generate_dialogue_based_on_topic
from audio_generator.speech_synthesiser import convert_dialogue_to_audio
from audiogram_generator.main_generator import generate_audiogram


def delete_tmp_files():
    folders = ['audio_files', 'video_files', 'text_files']

    for folder in folders:
        current_file_dir_path = str(pathlib.Path(__file__).parent) + '/'
        path = current_file_dir_path + f'tmp/{folder}'
        for file_name in os.listdir(path):
            file = f'{path}/{file_name}'
            if os.path.isfile(file):
                os.remove(file)


def remove_awkward_comma_names(dialogue):
    punctuation_signs = ['.', ',', ';', ':', '!', '?', ' ']
    hosts = ['Marc', 'Giulia']
    for host in hosts:
        for sign in punctuation_signs:
            dialogue = dialogue.replace(f', {host}{sign}', sign)

    return dialogue


def main():
    logger = set_up_logging()
    logger.info('Start execution')

    trending_article_titles = get_title_of_todays_trending_wiki_articles()
    discussed_recently, article_title = check_if_topic_discussed_recently(trending_article_titles)

    if not discussed_recently:
        episode_number = add_entry_to_record(article_title)
        podcast_dialogue = generate_dialogue_based_on_topic(article_title)
        podcast_dialogue = remove_awkward_comma_names(podcast_dialogue)
        path_to_wav_files = convert_dialogue_to_audio(podcast_dialogue)
        generate_audiogram(path_to_wav_files, podcast_dialogue, article_title, episode_number)
        # delete_tmp_files()

    logger.info('Finish execution')


if __name__ == '__main__':
    main()
