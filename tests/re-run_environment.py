# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

from audiogram_generator.visualisation_generator import AnimationGenerator
from audiogram_generator.captions_generator import generate_video_with_captions
from audiogram_generator.main_generator import generate_audiogram

from main import read_content_store_from_file

audio_file_paths = {
    'Combined': '/output/raw_audio',
    'Enhanced': '/Users/SeverinBurg/Documents/GitHub/sundryhypes-generator/output/final_audio',
    'Joined_Mono': '/tmp/audio_files/joined_mono',
    'Giulia': '/tmp/audio_files/giulia_combined',
    'Marc': '/tmp/audio_files/marc_combined'
}

text_file_paths = {
    'Giulia': '/Users/SeverinBurg/Documents/GitHub/sundryhypes-generator/tmp/text_files'
              '/script_giulia.txt',
    'Marc': '/Users/SeverinBurg/Documents/GitHub/sundryhypes-generator/tmp/text_files/'
            'script_marc.txt'
}

title = 'Deplatforming of Tucker Carlson'
episode_number = 23

generator = AnimationGenerator(audio_file_paths['Joined_Mono'], audio_file_paths['Enhanced'])
visualisation_clip = generator.get_animation_clip()

content_store = read_content_store_from_file()
generate_audiogram(audio_file_paths, content_store, title, episode_number)
# generate_video_with_captions(visualisation_clip, audio_file_paths, text_file_paths,
#                              content_store, title, episode_number)
