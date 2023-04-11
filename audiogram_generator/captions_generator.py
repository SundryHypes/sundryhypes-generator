# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import json
import random
import string
import logging
import pathlib
import datetime
from moviepy import editor
from aeneas.task import Task
from aeneas.executetask import ExecuteTask

logger = logging.getLogger('Main_Logger')
root_dir_path = str(pathlib.Path(__file__).parent.parent) + '/'


def generate_text_alignment_with_timestamps(audio_file_path, script_file_path):
    logger.info(f'Force alignment of text to audio')

    config_string = u"task_language=eng|is_text_type=subtitles|os_task_file_format=json" \
                    u"|task_adjust_boundary_nonspeech_min=0.0100" \
                    u"|task_adjust_boundary_nonspeech_string=REMOVE" \
                    u"|is_audio_file_detect_head_max=20.0" \
                    u"|is_audio_file_detect_head_min=0"
    task = Task(config_string=config_string)

    task.audio_file_path_absolute = root_dir_path + f'{audio_file_path}.wav'
    task.text_file_path_absolute = script_file_path

    filename = ''.join(random.choices(string.ascii_lowercase, k=5))

    alignment_file_path = root_dir_path + f'tmp/text_files/{filename}.json'
    task.sync_map_file_path_absolute = alignment_file_path

    ExecuteTask(task).execute()

    task.output_sync_map_file()

    return alignment_file_path


def generate_text_clip(from_t, to_t, txt, position, txt_color='#333335',
                       fontsize=50, font='SF-Pro'):
    logger.info(f'Generating text clip for "{txt}"')

    text_clip = editor.TextClip(txt, font_size=fontsize, font=font, color=txt_color)

    if position == 'left_caption':
        text_position = (0.21, 0.78)
    elif position == 'right_caption':
        text_position = (0.59, 0.78)
    elif position == 'episode_number':
        text_position = ('center', 0.042)
    elif position == 'title':
        text_position = ('center', 0.073)
    else:
        raise Exception('Unknown position for text')

    text_clip = text_clip.with_position(text_position, relative=True)
    text_clip = text_clip.with_start(from_t)
    text_clip = text_clip.with_end(to_t)

    return text_clip


def generate_video_with_captions(visualisation_clip, audio_files, text_files, title, number):
    subclips = []
    text_fragments = {}

    for key, file_path in text_files.items():
        text_fragments[key] = []

        text_alignment_file_path = generate_text_alignment_with_timestamps(
            audio_files[key], file_path
        )

        file = open(text_alignment_file_path)
        data = json.load(file)

        for fragment in data['fragments']:
            text_fragments[key].append(
                ((fragment['begin'], fragment['end']), '\n'.join(fragment['lines'])))

        file.close()

    today = datetime.date.today()
    episode_number = f'{number:03} / {today.year}'
    episode_number_clip = generate_text_clip(
        0, visualisation_clip.duration, f'SUNDRY HYPES • {episode_number}',
        'episode_number', fontsize=25
    )
    subclips.append(episode_number_clip)

    title_clip = generate_text_clip(
        0, visualisation_clip.duration, title, 'title', fontsize=40
    )
    subclips.append(title_clip)

    background_file_path = root_dir_path + 'assets/background.png'
    background_clip = editor.ImageClip(
        background_file_path,
        transparent=False,
        duration=visualisation_clip.duration
    )
    background_clip.with_start(0)

    for (from_t, to_t), txt in text_fragments['Giulia']:
        subclips.append(generate_text_clip(from_t, to_t, txt, 'right_caption'))

    for (from_t, to_t), txt in text_fragments['Marc']:
        subclips.append(generate_text_clip(from_t, to_t, txt, 'left_caption'))

    subclips.insert(0, background_clip)
    subclips.insert(1, visualisation_clip)
    final_clip = editor.CompositeVideoClip(subclips)
    final_clip = final_clip.with_duration(visualisation_clip.duration)

    logger.info(f'Saving final clip')

    # final_clip.save_frame('frame.png', t=1, with_mask=False)
    # final_clip.preview(fps=30)
    final_clip.write_videofile(f'{root_dir_path}output/final.mp4', threads=4, preset='ultrafast',
                               temp_audiofile="temp-audio.m4a", remove_temp=True,
                               codec="libx264", audio_codec="aac")
