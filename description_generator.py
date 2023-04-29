# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import logging

logger = logging.getLogger('Main_Logger')


def generate_intro():
    """
    About the Video
    Detailed explanation of what the video is about, including important keywords.

    Example:
        Hi, thanks for watching our video about <>!
        In this video we’ll walk you through:
    """
    raise NotImplementedError


def find_start_times(table, text_fragments):

    def update_table(sub_table, section):
        first_speaker = sub_table[section]['first_speaker']
        for (from_t, to_t), txt in text_fragments[first_speaker]:
            if sub_table[section]['first_verbatim'] in txt.replace('\n', ' '):
                sub_table[section]['starts_at'] = from_t

    for part in ['introduction', 'outro']:
        sub = table
        update_table(sub, part)

    for i in range(table['main']['number_of_parts']):
        sub = table['main']
        update_table(sub, f'{i + 1}_topic')

    return table


def generate_timestamp(table, text_fragments):
    """
    TABLE OF CONTENT
    0:00 Intro
    1:00 First Topic Covered
    1:30 Second Topic Covered
    """
    table = find_start_times(table, text_fragments)

    description = 'TABLE OF CONTENT\n'

    description += f"{table['introduction']['starts_at']} Introduction\n"

    for section, details in table['main'].items():
        description += f"{details['starts_at']} {details['title']}\n"

    description += f"{table['outro']['starts_at']} Outro"

    return description


def generate_video_recommendations():
    """
    Example:
        CHECK OUT OUR OTHER VIDEOS
        https://www.youtube.com/watch?v=video1
        https://www.youtube.com/watch?v=video2
        https://www.youtube.com/watch?v=video3
    """
    raise NotImplementedError


def get_general_channel_description():
    """
    Example:
        ABOUT OUR CHANNEL
        Our channel is about <topic>. We cover lots of cool stuff such as <topic>, <topic> and
        <topic>

        FIND US AT
        https://www.website.com/

        GET IN TOUCH
        Contact us on info@company.com

        FOLLOW US ON SOCIAL
        Twitter: https://twitter.com/<profile>
        Facebook: https://facebook.com/<profile>
        Instagram: https://twitter.com/<profile>
        Spotify: http://spotify.com/<profile>
    """
    raise NotImplementedError


def generate_video_description(table_of_content, text_fragments):
    logger.info(f'Generating description...')

    description = ''
    # description += generate_intro()
    description += generate_timestamp(table_of_content, text_fragments) + '\n\n'
    # description += generate_video_recommendations()
    # description += get_general_channel_description()

    print(description)

    return description
