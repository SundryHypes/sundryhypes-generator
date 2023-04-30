# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import pathlib
import os
import json

from config import set_up_logging
from ideas_finder import search_term_on_wikipedia
from ideas_finder import get_title_of_todays_trending_wiki_articles
from archive.archive_maintainer import check_if_topic_discussed_recently, add_entry_to_record
from content_generator import generate_dialog_based_on_topic
from audio_generator.speech_synthesiser import convert_dialogue_to_audio
from audiogram_generator.main_generator import generate_audiogram
from description_generator import generate_video_description


def delete_tmp_files():
    folders = ['audio_files', 'video_files', 'text_files']

    for folder in folders:
        current_file_dir_path = str(pathlib.Path(__file__).parent) + '/'
        path = current_file_dir_path + f'tmp/{folder}'
        for file_name in os.listdir(path):
            file = f'{path}/{file_name}'
            if os.path.isfile(file):
                os.remove(file)


def read_content_store_from_file():
    root_dir_path = str(pathlib.Path(__file__).parent) + '/'
    file_path = root_dir_path + f'output/content_store.txt'
    with open(file_path, 'r') as file:
        data = file.read()
        content_store = json.loads(data)

    return content_store, None


def main():
    logger = set_up_logging()
    logger.info('Start execution')

    article_titles = get_title_of_todays_trending_wiki_articles()
    # article_titles = search_term_on_wikipedia("Tucker Carlson")
    # article_titles = ['Tucker Carlson 2024?']

    discussed_recently, article_title = check_if_topic_discussed_recently(article_titles)

    if not discussed_recently:
        episode_number = add_entry_to_record(article_title)

        # content_store = generate_dialogue_based_on_topic(article_title)
        content_store = read_content_store_from_file()

        path_to_wav_files = convert_dialogue_to_audio(content_store['dialog'])
        text_fragments_with_timestamps = generate_audiogram(path_to_wav_files, content_store,
                                                            article_title, episode_number)

        generate_video_description(content_store, text_fragments_with_timestamps)

        # delete_tmp_files()

    logger.info('Finish execution')


if __name__ == '__main__':
    main()
