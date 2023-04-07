# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import math
import wave
import struct
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip

from audiogram_generator.audio_visualiser_scripts.savitzky_golay import savitzky_golay
from audiogram_generator.audio_visualiser_scripts.polar_coordinates_converter \
    import convert_to_polar_coordinates

root = '/Users/SeverinBurg/Desktop/xPlain/code'

class AnimationClip(VideoClip):
    def __init__(self, make_frame, fps, duration, audio_file,
                 audio_buffersize=200000, audio_fps=44100, audio_nbytes=2,
                 has_mask=True, has_constant_size=True):
        VideoClip.__init__(self)

        self.has_constant_size=has_constant_size
        self.duration = duration
        self.end = duration
        self.fps = fps

        self.audio = AudioFileClip(
            audio_file,
            buffersize=audio_buffersize,
            fps=audio_fps,
            nbytes=audio_nbytes,
        )

        if has_mask:
            self.make_frame = lambda t: make_frame(t)[:, :, :3]
            self.size = self.get_frame(0).shape[:2][::-1]
            self.make_mask = lambda t: make_frame(t)[:, :, 3] / 255.0
            self.mask = (VideoClip(ismask=True, make_frame=self.make_mask)
                         .set_duration(self.duration))
            self.mask.fps = self.fps

        else:
            self.make_frame = lambda t: make_frame(t)[:, :, :3]
            self.size = self.get_frame(0).shape[:2][::-1]


class AnimationGenerator:
    def __init__(self, audio_joined_mono, audio_enhanced):
        self.audio_file_enhanced = f'{audio_enhanced}.wav'
        self.wavefile_path = f'{root}{audio_joined_mono}.wav'
        self.wavefile = wave.open(self.wavefile_path, 'rb')
        self.rate = 44100
        self.fps = 25
        self.sample_size = 2
        self.window = 0.5
        self.channels = 2

        self.width = 1920
        self.height = 1080

        self.plots = {}
        self.plot_positions = {
            'marc': {
                'small': {
                    'x': -38750,
                    'y': 6000
                },
                'large': {
                    'x': -34250,
                    'y': 3500
                }
            },
            'giulia': {
                'small': {
                    'x': 34200,
                    'y': 3500
                },
                'large': {
                    'x': 38700,
                    'y': 6000
                }
            }
        }
        self.basis_radius = {
            '095': 10000 * 0.95,
            '100': 10000,
            '110': 10000 * 1.1
        }

        self.__assert_audio_file()

        dpi = plt.rcParams['figure.dpi']
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['figure.figsize'] = (self.width / dpi, self.height / dpi)


    def __assert_audio_file(self):
        assert self.wavefile.getnchannels() == self.channels
        assert self.wavefile.getsampwidth() == self.sample_size
        assert self.wavefile.getframerate() == self.rate

    def __set_default_lines(self, ax, x):
        y_zeroes = np.zeros(x.shape)
        polar_radius = {
            '095': convert_to_polar_coordinates(x, y_zeroes, self.basis_radius['095']),
            '100': convert_to_polar_coordinates(x, y_zeroes, self.basis_radius['100']),
            '110': convert_to_polar_coordinates(x, y_zeroes, self.basis_radius['110']),
        }

        self.plots['marc'] = {
            'small': ax.plot(polar_radius['100']['x'] + self.plot_positions['marc']['small']['x'],
                             polar_radius['100']['y'] + self.plot_positions['marc']['small']['y'],
                             linewidth=5, color='#EF5224'),
            'large': ax.plot(polar_radius['110']['x'] + self.plot_positions['marc']['large']['x'],
                             polar_radius['110']['y'] + self.plot_positions['marc']['large']['y'],
                             linewidth=5, color='#05539E')
        }

        self.plots['giulia'] = {
            'small': ax.plot(polar_radius['095']['x'] + self.plot_positions['giulia']['small']['x'],
                             polar_radius['095']['y'] + self.plot_positions['giulia']['small']['y'],
                             linewidth=5, color='#EF5224'),
            'large': ax.plot(polar_radius['100']['x'] + self.plot_positions['giulia']['large']['x'],
                             polar_radius['100']['y'] + self.plot_positions['giulia']['large']['y'],
                             linewidth=5, color='#F2BB2A')
        }

    def __symmetrize_wave(self, y_channel):
        is_odd = False
        len_y = len(y_channel)
        if len_y % 2 != 0:
            idx = math.floor(len_y / 2)
            is_odd = True
        else:
            idx = int(len(y_channel) / 2)
        y_half = y_channel[idx]
        y_half_reversed = [y_half[-i] for i in range(1, len(y_half) + 1)]
        if is_odd:
            y_half_reversed.append(y_half_reversed[-1])
        y_symmetric = np.concatenate((y_half, np.array(y_half_reversed)))

        return y_symmetric

    def __get_symmetric_savitzky_data(self, waves):
        symmetric_savitzky_data = {
            'marc': {
                'small': savitzky_golay(self.__symmetrize_wave(waves['small'][0])),
                'large': savitzky_golay(self.__symmetrize_wave(waves['large'][0]))
            },
            'giulia': {
                'small': savitzky_golay(self.__symmetrize_wave(waves['small'][1])),
                'large': savitzky_golay(self.__symmetrize_wave(waves['large'][1]))
            }
        }
        return symmetric_savitzky_data

    def __get_polar_data(self, x, savitzky_symmetric_data):
        polar_data = {
            'marc': {
                'small': convert_to_polar_coordinates(
                    x, savitzky_symmetric_data['marc']['small'],
                    self.basis_radius['100']
                    + mean(savitzky_symmetric_data['marc']['small'])
                ),
                'large': convert_to_polar_coordinates(
                    x, savitzky_symmetric_data['marc']['large'],
                    self.basis_radius['110']
                )
            },
            'giulia': {
                'small': convert_to_polar_coordinates(
                    x, savitzky_symmetric_data['giulia']['small'],
                    self.basis_radius['095']
                    + mean(savitzky_symmetric_data['giulia']['small'])
                ),
                'large': convert_to_polar_coordinates(
                    x, savitzky_symmetric_data['giulia']['large'],
                    self.basis_radius['100']
                )
            }
        }
        return polar_data

    def __set_plot_data(self, polar_data):
        self.plots['marc']['small'][0].set_data(
            polar_data['marc']['small']['x'] + self.plot_positions['marc']['small']['x'],
            polar_data['marc']['small']['y'] + self.plot_positions['marc']['small']['y']
        )
        self.plots['marc']['large'][0].set_data(
            polar_data['marc']['large']['x'] + self.plot_positions['marc']['large']['x'],
            polar_data['marc']['large']['y'] + self.plot_positions['marc']['large']['y']
        )
        self.plots['giulia']['small'][0].set_data(
            polar_data['giulia']['small']['x'] + self.plot_positions['giulia']['small']['x'],
            polar_data['giulia']['small']['y'] + self.plot_positions['giulia']['small']['y']
        )
        self.plots['giulia']['large'][0].set_data(
            polar_data['giulia']['large']['x'] + self.plot_positions['giulia']['large']['x'],
            polar_data['giulia']['large']['y'] + self.plot_positions['giulia']['large']['y']
        )

    def __plot_to_npimage(self, fig):
        """ Converts a matplotlib figure to a RGB frame after updating the canvas"""
        #  only the Agg backend now supports the tostring_rgb function
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        canvas = FigureCanvasAgg(fig)
        canvas.draw()  # update/draw the elements

        # get the width and the height to resize the matrix
        l, b, w, h = canvas.figure.bbox.bounds
        w, h = int(w), int(h)

        #  exports the canvas to a string buffer and then to a numpy nd.array
        buf = canvas.buffer_rgba()
        image = np.frombuffer(buf, dtype=np.uint8)
        return image.reshape(h, w, 4)

    def __record_animation(self):
        fig = plt.figure(facecolor='none', edgecolor='white')
        fig.patch.set_alpha(0.0)
        ax = fig.add_subplot(xlim=(-100000, 100000), ylim=(-56250, 56250))
        ax.patch.set_alpha(0.0)
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

        ax.axis('off')
        ax.set_aspect('equal')

        duration = self.wavefile.getnframes() / self.wavefile.getframerate()
        n_for_x = int(1 * self.rate / self.fps) - self.wavefile.tell()
        x = np.linspace(0, self.window, n_for_x * 2)

        self.__set_default_lines(ax, x)

        def make_frame(t):
            N = (int(t * self.rate) - self.wavefile.tell())

            if N < 0:
                self.wavefile.close()
                self.wavefile = wave.open(self.wavefile_path, 'rb')
                N = (int(t * self.rate) - self.wavefile.tell())

            if not N:
                return self.__plot_to_npimage(fig)

            data = self.wavefile.readframes(N)
            y = np.array(struct.unpack("%dh" % (len(data) / self.sample_size), data))

            if len(y) != 2 * len(x):
                print('EARLY RETURN! -> len(y) =', len(y), 'len(x) =', len(x), 'N =', N, 't =', t)
                return self.__plot_to_npimage(fig)

            waves = {
                'small': [[] for channel in range(self.channels)],
                'large': [[] for channel in range(self.channels)]
            }

            for index, datum in enumerate(y):
                waves['small'][index % len(waves['small'])].append(np.abs(datum) / 7.5)
                waves['large'][index % len(waves['large'])].append(np.abs(datum) / 5.5)

            symmetric_savitzky_data = self.__get_symmetric_savitzky_data(waves)
            polar_data = self.__get_polar_data(x, symmetric_savitzky_data)
            self.__set_plot_data(polar_data)

            return self.__plot_to_npimage(fig)

        animation_clip = AnimationClip(
            make_frame, audio_file=self.audio_file_enhanced,
            has_mask=True, fps=self.fps, duration=duration
        )

        return animation_clip

    def get_animation_clip(self):
        return self.__record_animation()
