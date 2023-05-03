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


def generate_timestamp(content_store):
    """
    TABLE OF CONTENT
    0:00 Intro
    1:00 First Topic Covered
    1:30 Second Topic Covered
    """
    timestamps = ''

    for key, section in content_store['sections'].items():
        time = section.starts_at
        if section.name == 'introduction':
            timestamps += '0:00 Introduction\n'
        if section.name == 'outro':
            timestamps += f'{int(time / 60)}:{int(time % 60)} Outro'
        else:
            timestamps += f'{int(time / 60)}:{int(time % 60)} {section.title}\n'

    return timestamps


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


def generate_video_description(content_store):
    logger.info(f'Generating description...')

    description = ''
    # description += generate_intro()
    description += generate_timestamp(content_store) + '\n\n'
    # description += generate_video_recommendations()
    # description += get_general_channel_description()

    print(description)

    return description
