import datetime
from moviepy import editor
from moviepy.video.fx.resize import resize

from audiogram_generator.visualisation_generator import AnimationGenerator
from audiogram_generator.captions_generator import generate_text_clip

destination = '/Users/SeverinBurg/Desktop/moviepy_example.mp4'

generator = AnimationGenerator('/tmp/audio_files/joined_mono',
                               '/Users/SeverinBurg/Desktop/xPlain/code/tmp/audio_files/joined_mono')
visualisation_clip = generator.get_animation_clip()

subclips = []
text_fragments = {}

background_file_path = '/Users/SeverinBurg/Desktop/xPlain/code/assets/background.png'
background_clip = editor.ImageClip(background_file_path)
background_clip.set_start(0)
background_clip.set_duration(visualisation_clip.duration)
background_clip = resize(background_clip, width=1920, height=1080)

today = datetime.date.today()
episode_number = f'{1:03} / {today.year}'
episode_number_clip = generate_text_clip(
    0, visualisation_clip.duration, f'SUNDRY HYPES • {episode_number}', 'episode_number',
    fontsize=25
)
subclips.append(episode_number_clip)

title_clip = generate_text_clip(
    0, visualisation_clip.duration, 'Test', 'title', fontsize=40
)
subclips.append(title_clip)

subclips.append(generate_text_clip(0, visualisation_clip.duration,
                                   'Hi. I am Giulia. \n I hope you are good.', 'right_caption'))
subclips.append(generate_text_clip(0, visualisation_clip.duration,
                                   'Hi. I am Marc. \n I hope you are good.', 'left_caption'))

subclips.insert(0, background_clip)
subclips.insert(1, visualisation_clip)

final_clip = editor.CompositeVideoClip(subclips)
final_clip = final_clip.set_duration(visualisation_clip.duration)

#final_clip.save_frame('test.png', t=1)
final_clip.write_videofile(destination, preset='ultrafast', threads=8,
                           temp_audiofile="temp-audio.m4a", remove_temp=True,
                           codec="hevc_videotoolbox", audio_codec="aac")
