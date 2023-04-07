#!/usr/bin/env python
# =================================
# Sound viewer
# ------------
# [May 2020] - Mina PECHEUX
#
# Based on the work by Yu-Jie Lin
# (Public Domain)
# Github: https://gist.github.com/manugarri/1c0fcfe9619b775bb82de0790ccb88da

import struct
import sys

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib import collections as mc
from statistics import mean
import numpy as np

from audiogram_generator.audio_visualiser_scripts.polar_coordinates_converter import \
    convert_to_polar_coordinates
from audiogram_generator.audio_visualiser_scripts.savitzky_golay import savitzky_golay


TITLE = ''

WIDTH = 1920
HEIGHT = 1080

SAMPLE_SIZE = 2
CHANNELS = 2
RATE = 44100
FPS = 25
nFFT = 512
basis_radius = 10000

WINDOW = 0.5  # in seconds

# ========================
# CONFIGURATION
# ========================

x_position_left = 40500
y_position_left = 5000

x_position_right = 37160
y_position_right = 5000

# ========================
# INITIALIZATION FUNCTIONS
# ========================
def init_color(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i + 2], 16) / 255 for i in (0, 2, 4))


def init_bars(lines, color):
    color = init_color(color)
    lines.set_color(color)
    return lines,


def init_spectrum(line, color):
    color = init_color(color)
    line.set_ydata(np.zeros(nFFT - 1))
    line.set_color(color)
    return line,


def init_wave(lines, color, x_polar, y_polar):
    lines[0][0].set_xdata(x_polar - x_position_left)
    lines[0][0].set_ydata(y_polar + y_position_left)
    lines[0][0].set_color('#EF5224')

    lines[1][0].set_ydata(x_polar + x_position_right)
    lines[1][0].set_ydata(y_polar + y_position_right)
    lines[1][0].set_color('#F2BB2A')

    lines[2][0].set_ydata(x_polar - x_position_left)
    lines[2][0].set_ydata(y_polar + y_position_left)
    lines[2][0].set_color('#05539E')

    lines[3][0].set_ydata(x_polar + x_position_right)
    lines[3][0].set_ydata(y_polar + y_position_right)
    lines[3][0].set_color('#EF5224')

    return lines,


# ========================
# ANIMATION FUNCTIONS
# ========================
def animate_bars(i, lines, lines_x, wf, color, max_y, bar_min):
    N = (int((i + 1) * RATE / FPS) - wf.tell()) // nFFT
    if not N:
        return lines,
    N *= nFFT
    data = wf.readframes(N)
    print('{:5.1f}% - V: {:5,d} - A: {:10,d} / {:10,d}'.format(
        100.0 * wf.tell() / wf.getnframes(), i, wf.tell(), wf.getnframes()
    ))

    # Unpack data, LRLRLR...
    y = np.array(struct.unpack("%dh" % (len(data) / SAMPLE_SIZE), data)) / max_y
    y_L = y[::2]
    y_R = y[1::2]

    Y_L = np.fft.fft(y_L, nFFT)
    Y_R = np.fft.fft(y_R, nFFT)

    # Sewing FFT of two channels together, DC part uses right channel's
    Y = abs(np.hstack((Y_L[-nFFT // 2:-1], Y_R[:nFFT // 2])))
    Y_v = Y[::2]

    lines_data = []
    for i, x in enumerate(lines_x):
        lines_data.append([(x, min(-bar_min, -Y_v[i])), (x, max(bar_min, Y_v[i]))])

    lines.set_segments(lines_data)

    return lines,


def animate_spectrum(i, line, wf, color, max_y):
    N = (int((i + 1) * RATE / FPS) - wf.tell()) // nFFT
    if not N:
        return line,
    N *= nFFT
    data = wf.readframes(N)
    print('{:5.1f}% - V: {:5,d} - A: {:10,d} / {:10,d}'.format(
        100.0 * wf.tell() / wf.getnframes(), i, wf.tell(), wf.getnframes()
    ))

    # Unpack data, LRLRLR...
    y = np.array(struct.unpack("%dh" % (len(data) / SAMPLE_SIZE), data)) / max_y
    y_L = y[::2]
    y_R = y[1::2]

    Y_L = np.fft.fft(y_L, nFFT)
    Y_R = np.fft.fft(y_R, nFFT)

    # Sewing FFT of two channels together, DC part uses right channel's
    Y = abs(np.hstack((Y_L[-nFFT // 2:-1], Y_R[:nFFT // 2])))

    line.set_ydata(Y)
    return line,

def normalize_values(values, max_value):
    if len(values) == 0:
        return values
    max = values.max()

    if max <= 1e-6:
        return values

    # return (values / max) * max_value
    return values

def animate_wave(i, lines, wavefile, x):
    N = (int((i + 1) * RATE / FPS) - wavefile.tell())
    print('i =', i, ' - N =', N)
    if not N:
        return lines,
    data = wavefile.readframes(N)
    y = np.array(struct.unpack("%dh" % (len(data) / SAMPLE_SIZE), data))
    print('{:5.1f}% - V: {:5,d} - A: {:10,d} / {:10,d}'.format(
        100.0 * wavefile.tell() / wavefile.getnframes(), i, wavefile.tell(), wavefile.getnframes()
    ))

    max_value = 10
    y = normalize_values(y, max_value)
    if len(y) != 2 * len(x):
        return lines,

    # Split the data into channels
    small_waves = [[] for channel in range(CHANNELS)]
    for index, datum in enumerate(y):
        decrease_size_by_factor = 7.5
        small_waves[index % len(small_waves)].append(np.abs(datum) / decrease_size_by_factor)

    big_waves = [[] for channel in range(CHANNELS)]
    for index, datum in enumerate(y):
        decrease_size_by_factor = 5.5
        big_waves[index % len(big_waves)].append(np.abs(datum) / decrease_size_by_factor)

    y_l_small_waves = savitzky_golay(symmetrize_wave(small_waves[0]))
    y_l_big_waves = savitzky_golay(symmetrize_wave(big_waves[0]))

    y_r_big_waves = savitzky_golay(symmetrize_wave(big_waves[1]))
    y_r_small_waves = savitzky_golay(symmetrize_wave(small_waves[1]))

    x_l_1, y_l_1 = convert_to_polar_coordinates(x, y_l_small_waves, basis_radius+mean(
        y_l_small_waves))
    x_l_2, y_l_2 = convert_to_polar_coordinates(x, y_l_big_waves, basis_radius * 1.1)

    x_r_1, y_r_1 = convert_to_polar_coordinates(x, y_r_big_waves, basis_radius)
    x_r_2, y_r_2 = convert_to_polar_coordinates(x, y_r_small_waves, basis_radius * 0.95
                                                        + mean(y_r_small_waves))

    lines[0][0].set_xdata([c - x_position_left for c in x_l_1])
    lines[0][0].set_ydata([c + y_position_left for c in y_l_1])

    lines[1][0].set_xdata([c + x_position_right for c in x_r_1])
    lines[1][0].set_ydata([c + y_position_right for c in y_r_1])

    lines[2][0].set_xdata([c - x_position_left + 4500 for c in x_l_2])
    lines[2][0].set_ydata([c + y_position_left - 2500 for c in y_l_2])

    lines[3][0].set_xdata([c + x_position_right - 4500 for c in x_r_2])
    lines[3][0].set_ydata([c + y_position_right - 2500 for c in y_r_2])

    return lines


def symmetrize_wave(y_channel):
    idx = len(y_channel) / 2
    y_half = y_channel[:int(idx)]
    y_half_reversed = [y_half[-i] for i in range(1, len(y_half) + 1)]
    y_symmetric = np.concatenate((y_half, np.array(y_half_reversed)))
    return y_symmetric


# ========================
# COMPUTE FUNCTIONS
# ========================
def compute_bars(fig, wf, color):
    bar_step = 2
    bar_min = 0.05

    # Frequency range
    x_f = 1.0 * np.arange(-nFFT / 2 + 1, nFFT / 2) / nFFT * RATE
    x_range = x_f[-1] - x_f[0]
    ax = fig.add_subplot(111, title=TITLE, xlim=(x_f[0], x_f[-1]),
                         ylim=(-np.pi * nFFT ** 2 / RATE, np.pi * nFFT ** 2 / RATE))
    ax.set_yscale('symlog')
    plt.axis('off')
    plt.subplots_adjust(left=0, bottom=0.1, right=1, top=0.9, wspace=0, hspace=0.1)

    lines_data = []
    lines_x = []
    for i in range(-nFFT // (bar_step * 2), nFFT // (bar_step * 2)):
        ix = i * bar_step * x_range / float(nFFT)
        lines_x.append(ix)
        lines_data.append([(ix, -bar_min), (ix, bar_min)])

    lines = mc.LineCollection(lines_data, linewidths=2)
    ax.add_collection(lines)

    max_y = 2.0 ** (SAMPLE_SIZE * 8 - 1)

    return animation.FuncAnimation(
        fig, animate_bars, int(wf.getnframes() / RATE * FPS),
        init_func=lambda: init_bars(lines, color),
        fargs=(lines, lines_x, wf, color, max_y, bar_min),
        interval=1000.0 / FPS, blit=False
    )


def compute_spectrum(fig, wf, color):
    # Frequency range
    x_f = 1.0 * np.arange(-nFFT / 2 + 1, nFFT / 2) / nFFT * RATE
    ax = fig.add_subplot(111, title=TITLE, xlim=(x_f[0], x_f[-1]),
                         ylim=(0, 2 * np.pi * nFFT ** 2 / RATE))
    ax.set_yscale('symlog', linthreshy=nFFT ** 0.5)
    plt.axis('off')
    plt.subplots_adjust(left=0, bottom=0.1, right=1, top=0.9, wspace=0, hspace=0.1)

    line, = ax.plot(x_f, np.zeros(nFFT - 1))
    max_y = 2.0 ** (SAMPLE_SIZE * 8 - 1)

    return animation.FuncAnimation(
        fig, animate_spectrum, int(wf.getnframes() / RATE * FPS),
        init_func=lambda: init_spectrum(line, color),
        fargs=(line, wf, color, max_y),
        interval=1000.0 / FPS, blit=False
    )


def compute_wave(fig, wavefile, color):
    # Time range
    N = int(1 * RATE / FPS) - wavefile.tell()
    x = np.linspace(0, WINDOW, N)

    ax = fig.add_subplot(111, title=TITLE, xlim=(-100000, 100000), ylim=(-56250, 56250))

    ax.axis('off')
    ax.set_aspect('equal')

    # img = plt.imread('/Users/SeverinBurg/Desktop/xPlain/code/assets/background.jpg')
    # ax.imshow(img, extent=[-100000, 100000, -56250, 56250])

    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    y_zeroes = np.zeros(x.shape)
    x_polar, y_polar = convert_to_polar_coordinates(x, y_zeroes, basis_radius)

    lines = []
    lines.append(ax.plot(x_polar + x_position_left, y_polar + y_position_left, linewidth=3,
                         color='#EF5224'))
    lines.append(ax.plot(x_polar + x_position_right, y_polar + y_position_right, linewidth=3,
                         color='#F2BB2A'))
    lines.append(ax.plot(x_polar + x_position_left, y_polar + y_position_left, linewidth=3,
                         color='#05539E'))
    lines.append(ax.plot(x_polar + x_position_right, y_polar + y_position_right, linewidth=3,
                         color='#EF5224'))

    return animation.FuncAnimation(
        fig, animate_wave, int(wavefile.getnframes() / RATE * FPS),
        init_func=lambda: init_wave(lines, color, x_polar, y_polar),
        fargs=(lines, wavefile, x),
        interval=1000.0 / FPS, blit=False,
    )


# global computation function
def compute(method, color, fig, wavefile):
    if method == 'bars':
        return compute_bars(fig, wavefile, color)
    elif method == 'spectrum':
        return compute_spectrum(fig, wavefile, color)
    elif method == 'wave':
        return compute_wave(fig, wavefile, color)
    else:
        print('Unknown method. Try one of the following:')
        print('"bars"', '"spectrum"', '"wave"')
        return None
