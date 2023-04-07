# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

# https://github.com/MinaPecheux/py-sound-viewer

import os
import wave
import logging

from deprecated.compute import plt, compute, WIDTH, \
    HEIGHT, SAMPLE_SIZE, CHANNELS, RATE, FPS

logger = logging.getLogger('Main_Logger')


def generate_audio_visualisation(audio_file_path, color='#009dff', output=False, method='wave'):
    root = '/Users/SeverinBurg/Desktop/xPlain/code'

    logger.info(f'Generating wave visualisation. File: {audio_file_path}')

    dpi = plt.rcParams['figure.dpi']
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['figure.figsize'] = (WIDTH / dpi, HEIGHT / dpi)

    audio_file = wave.open(f'{root}/tmp/audio_files/joined_mono.wav', 'rb')
    assert audio_file.getnchannels() == CHANNELS
    assert audio_file.getsampwidth() == SAMPLE_SIZE
    assert audio_file.getframerate() == RATE

    fig = plt.figure(edgecolor='white')
    fig.patch.set_alpha(0.0)

    animation = compute(method, color, fig, audio_file)
    if animation is None:
        audio_file.close()
        return

    tmp_video_file_path = f'{root}/tmp/video_files/dialog'

    if output:
        animation.save(f'{tmp_video_file_path}.mp4', fps=FPS, codec='png',
                       savefig_kwargs={'facecolor': 'none', 'transparent': True})
    else:
        plt.show()

    audio_file.close()

    os.system(
        f'bash {root}/audiogram_generator/audio_visualiser_scripts/bash_scripts/add_audio_to_video.sh -a {root}/output/dolby_enhancement -v {tmp_video_file_path}')

    video_file_path = f'{audio_file_path}.mp4'

    return video_file_path
