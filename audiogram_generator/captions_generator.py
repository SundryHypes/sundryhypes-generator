# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import json
import random
import string
import logging
import pathlib
import datetime
from aeneas.task import Task
from aeneas.executetask import ExecuteTask
from moviepy import editor, VideoFileClip

logger = logging.getLogger('Main_Logger')
root_dir_path = str(pathlib.Path(__file__).parent.parent) + '/'


def generate_text_alignment_with_timestamps(audio_file_path, script_file_path):
    logger.info(f'Force alignment of text to audio')

    config_string = u"task_language=eng|is_text_type=subtitles|os_task_file_format=json" \
                    u"|task_adjust_boundary_nonspeech_min=0.0100" \
                    u"|task_adjust_boundary_nonspeech_string=REMOVE" \
                    u"|is_audio_file_detect_head_max=32.0" \
                    u"|is_audio_file_detect_head_min=2.0"
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
        text_position = (0.57, 0.78)
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


def generate_text_fragments(text_files, audio_files, visualisation_start_at, content_store):
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
                ((float(fragment['begin']) + visualisation_start_at,
                  float(fragment['end']) + visualisation_start_at),
                 '\n'.join(fragment['lines']))
            )

        file.close()

    for key, section in content_store['sections'].items():
        for (from_t, to_t), txt in text_fragments[section['first_speaker']]:
            if txt == section['first_verbatim']:
                section['start_at'] = from_t
        for (from_t, to_t), txt in text_fragments[section['last_speaker']]:
            if txt == section['last_verbatim']:
                section['ends_at'] = to_t

    return text_fragments, content_store


def generate_title_section(title, number, visualisation_clip, visualisation_start_at):
    today = datetime.date.today()
    episode_number = f'{number:03} / {today.year}'
    episode_number_clip = generate_text_clip(
        visualisation_start_at, visualisation_clip.duration,
        f'SUNDRY HYPES • {episode_number}',
        'episode_number', fontsize=25
    )

    episode_number_clip = episode_number_clip.crossfadein(1.0)

    title_clip = generate_text_clip(
        visualisation_start_at, visualisation_clip.duration,
        title, 'title', fontsize=40
    )

    title_clip = title_clip.crossfadein(1.0)

    return [episode_number_clip, title_clip]


def generate_video_with_captions(visualisation_clip, audio_files, text_files,
                                 content_store, title, number):
    subclips = []

    intro_duration = 7
    visualisation_start_at = intro_duration - 1

    text_fragments, content_store = generate_text_fragments(text_files, audio_files,
                                                            visualisation_start_at, content_store)
    print(content_store)

    title_section = generate_title_section(title, number,
                                           visualisation_clip, visualisation_start_at)
    subclips.extend(title_section)

    intro_clip = VideoFileClip(root_dir_path + 'assets/intro.mp4', target_resolution=(1920, 1080))
    intro_clip = intro_clip.subclip(0, intro_duration)

    background_file_path = root_dir_path + 'assets/background.png'
    background_clip = editor.ImageClip(
        background_file_path,
        transparent=False,
        duration=visualisation_clip.duration
    )
    background_clip = background_clip.with_start(visualisation_start_at).crossfadein(1.0)

    for (from_t, to_t), txt in text_fragments['Giulia']:
        subclips.append(generate_text_clip(from_t, to_t, txt, 'right_caption'))

    for (from_t, to_t), txt in text_fragments['Marc']:
        subclips.append(generate_text_clip(from_t, to_t, txt, 'left_caption'))

    visualisation_clip = visualisation_clip.with_start(visualisation_start_at).crossfadein(1.0)

    subclips.insert(0, intro_clip)
    subclips.insert(1, background_clip)
    subclips.insert(2, visualisation_clip)
    final_clip = editor.CompositeVideoClip(subclips)
    final_clip = final_clip.with_duration(visualisation_clip.duration + intro_duration)

    logger.info(f'Saving final clip')

    # final_clip.save_frame('frame.png', t=1, with_mask=False)
    # final_clip.preview(fps=30)
    final_clip.write_videofile(f'{root_dir_path}output/video.mp4', threads=4, preset='ultrafast',
                               temp_audiofile="temp-audio.m4a", remove_temp=True,
                               codec="libx264", audio_codec="aac")

    return text_fragments
