# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import pathlib
import os
import pickle

from config import set_up_logging
from ideas_finder import search_term_on_wikipedia
from ideas_finder import get_title_of_todays_trending_wiki_articles
from archive.archive_maintainer import check_if_topic_discussed_recently, add_entry_to_record
from content_generator import generate_dialog_based_on_topic
from audio_generator.speech_synthesiser import convert_dialog_to_audio
from audiogram_generator.main_generator import generate_audiogram
from description_generator import generate_video_description

logger = set_up_logging()
root_dir_path = str(pathlib.Path(__file__).parent) + '/'


def delete_tmp_files():
    folders = ['audio_files', 'video_files', 'text_files']

    for folder in folders:
        path = root_dir_path + f'tmp/{folder}'
        for file_name in os.listdir(path):
            file = f'{path}/{file_name}'
            if os.path.isfile(file):
                os.remove(file)


def update_content_store_to_file(content_store):
    logger.info('Updating content store file...')

    file_path = root_dir_path + f'output/content_store.bin'
    with open(file_path, 'wb') as output_file:
        pickle.dump(content_store, output_file)


def read_content_store_from_file():
    file_path = root_dir_path + f'output/content_store.bin'
    with open(file_path, 'rb') as file:
        content_store = pickle.load(file)

    return content_store


def main():
    logger.info('Start execution')

    # article_titles = get_title_of_todays_trending_wiki_articles()
    article_titles = search_term_on_wikipedia("Tori Bowie")
    # article_titles = ['Increase of Private Jet Sales']

    discussed_recently, article_title = check_if_topic_discussed_recently(article_titles)

    if not discussed_recently:
        episode_number = add_entry_to_record(article_title)

        content_store = generate_dialog_based_on_topic(article_title)
        # content_store = read_content_store_from_file()

        path_to_wav_files = convert_dialog_to_audio(content_store['dialog'])
        content_store = generate_audiogram(path_to_wav_files, content_store,
                                           article_title, episode_number)

        update_content_store_to_file(content_store)
        generate_video_description(content_store)

        # delete_tmp_files()

    logger.info('Finish execution')


if __name__ == '__main__':
    main()
