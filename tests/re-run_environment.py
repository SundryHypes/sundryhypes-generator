# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

from audiogram_generator.visualisation_generator import AnimationGenerator
from audiogram_generator.captions_generator import generate_video_with_captions

audio_file_paths = {
    'Combined': '/output/dialog',
    'Enhanced': '/Users/SeverinBurg/Documents/GitHub/sundryhypes-generator/output/dolby_enhancement',
    'Joined_Mono': '/tmp/audio_files/joined_mono',
    'Giulia': '/tmp/audio_files/giulia_combined',
    'Marc': '/tmp/audio_files/marc_combined'
}

text_file_paths = {
    'Giulia': '/Users/SeverinBurg/Documents/GitHub/sundryhypes-generator/tmp/text_files/woryv.txt',
    'Marc': '/Users/SeverinBurg/Documents/GitHub/sundryhypes-generator/tmp/text_files/sumfh.txt'
}

title = 'Dalai Lama'
episode_number = 5

generator = AnimationGenerator(audio_file_paths['Joined_Mono'], audio_file_paths['Enhanced'])
visualisation_clip = generator.get_animation_clip()

generate_video_with_captions(visualisation_clip, audio_file_paths, text_file_paths,
                             title, episode_number)
