# -*- coding: utf-8 -*-

import codecs
import math
import struct
import sys
import argparse
import matplotlib.pyplot as plt
import array as arr
import numpy as np
from scipy import *
from scipy import signal
import _shim_main as shim
import _duty as duty
from _spectrum_main import signal2spectrum

from matplotlib import rc
rc('font', family='Courier New') # для отображения русского шрифта

from scipy.fftpack import rfft
# from scipy.fftpack import fft
from matplotlib.lines import Line2D

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-raw', '--raw_file_name', type=str, required=False)
    parser.add_argument('-rawf', '--rawf_file_name', type=str, required=False)
    parser.add_argument('-shim', '--shim_file_name', type=str, required=False)
    parser.add_argument('-p1', '--from_point', type=int, required=False)
    parser.add_argument('-p2', '--to_point', type=int, required=False)
    parser.add_argument('-s', '--sampling', type=int, required=False)
    parser.add_argument('-d', '--duration', type=int, required=False)
    parser.add_argument('-flg', '--flags', type=int, required=False)

    namespace = parser.parse_args(sys.argv[1:])

    if (namespace.raw_file_name == None and namespace.rawf_file_name == None and namespace.shim_file_name == None and
        namespace.sampling == None and namespace.duration == None and
        namespace.from_point == None and namespace.to_point == None):

        return None

    else:
        return namespace


def plot(**kwargs):

    # print('Start signal plotting')
    try:
        SIGNAL_SAMPLING = kwargs['s'] # дискретизация
        SIGNAL_DURATION = kwargs['d']
        POINT_1 = kwargs['p1'] # начальная точка
        POINT_2 = kwargs['p2'] # конечная точка
        FLAGS = kwargs['flags'] # флаги, указывающие что рисовать

        POINT_COUNT = int(SIGNAL_SAMPLING * SIGNAL_DURATION / 1000)
    
        if not POINT_1 or (POINT_1 not in range(POINT_COUNT)): POINT_1 = 0
        if not POINT_2 or (POINT_2 not in range(POINT_1, POINT_COUNT)): POINT_2 = POINT_COUNT

        flag_signal = FLAGS & 1
        flag_filtered = (FLAGS >> 1) & 1
        flag_signal_spectrum = (FLAGS >> 2) & 1
        flag_filtered_spectrum = (FLAGS >> 3) & 1
        flag_shim = (FLAGS >> 4) & 1
        pcnt = flag_signal + flag_filtered + flag_signal_spectrum + flag_filtered_spectrum + flag_shim
    
        if not pcnt:
            return False
    
        num = 1
        araw = None  # переделать!!
        arawf = None
        ashim = None
    
        # рисуем исходный сигнал
        if flag_signal:
            try:
                if araw is None:
                    if 'raw' in kwargs:
                        araw = duty.read_file(kwargs['raw'], 'd', 0, POINT_COUNT)

                if araw is None:
                    raise Exception('raw signal data not specified')
    
                plt.subplot(pcnt, 1, num)
                plt.plot(araw[POINT_1:POINT_2], label='Исходный сигнал')
                plt.legend(loc='upper left', shadow=True, frameon=True, fontsize='small')
                plt.xticks(arange(0, (POINT_2 - POINT_1), 50), arange(POINT_1, POINT_2, 50))
                plt.grid()
                num += 1
    
            except Exception as E:
                print('error on plotting raw signal: ', file=sys.stderr, end='')
                print(E, file=sys.stderr)
    
        # рисуем спектр исходного сигнала
        if flag_signal_spectrum:
            try:
                if araw is None:
                    if 'raw' in kwargs:
                        araw = duty.read_file(kwargs['raw'], 'd', 0, POINT_COUNT)
    
                if araw is None:
                    raise Exception('raw signal data not specified')
    
                plt.subplot(pcnt, 1, num)
                
                spectrum, aspec, araw = signal2spectrum(s=SIGNAL_SAMPLING, d=SIGNAL_DURATION, signal_data=araw)
    
                if aspec is None:
                    raise Exception('no raw signal spectrum for plotting')

                # plt.plot(aspec, label='Signal spectrum', color='g')
                plt.vlines(range(len(aspec)), 0, aspec, label='Спектр исходного сигнала', color='g')
                plt.legend(loc='upper left', shadow=True, frameon=True, fontsize='small')
                plt.grid()
                num += 1
    
            except Exception as E:
                print('error on plotting raw signal spectrum: ', file=sys.stderr, end='')
                print(E, file=sys.stderr)
    
    
        # рисуем отфильтрованный сигнал
        if flag_filtered:
            try:
                if 'rawf' in kwargs:
                    arawf = duty.read_file(kwargs['rawf'], 'd', 0, POINT_COUNT)
    
                if arawf is None:
                    raise Exception('filtered signal data not specified')

                plt.subplot(pcnt, 1, num)
                plt.plot(arawf[POINT_1:POINT_2], label='Отфильтрованный сигнал')
                plt.legend(loc='upper left', shadow=True, frameon=True, fontsize='small')
                plt.xticks(arange(0, (POINT_2 - POINT_1), 50), arange(POINT_1, POINT_2, 50))
                plt.grid()
                num += 1

            except Exception as E:
                print('error on plotting filtered signal: ', file=sys.stderr, end='')
                print(E, file=sys.stderr)
    
        # рисуем спектр отфильтрованного сигнала
        if flag_filtered_spectrum:
            try:
                if arawf is None:
                    if 'rawf' in kwargs:
                        arawf = duty.read_file(kwargs['rawf'], 'd', 0, POINT_COUNT)
    
                if arawf is None:
                    raise Exception('filtered signal data not specified')

                plt.subplot(pcnt, 1, num)
                # f, Pwelch_spec = signal.welch(arawf, SIGNAL_SAMPLING, scaling='spectrum')
                # plt.semilogy(f, Pwelch_spec)
    
                spectrum, aspec, araw = signal2spectrum(s=SIGNAL_SAMPLING, d=SIGNAL_DURATION, signal_data=arawf)
    
                if aspec is None:
                    raise Exception('no spectrum for plotting')
    
                # plt.plot(aspec, label='Filtered signal spectrum', color='g')
                plt.vlines(range(len(aspec)), 0, aspec, label='Спектр отфильтрованного сигнала', color='g')
                plt.legend(loc='upper left', shadow=True, frameon=True, fontsize='small')
                plt.grid()
                num += 1
    
            except Exception as E:
                print('error on plotting filtered signal spectrum: ', file=sys.stderr, end='')
                print(E, file=sys.stderr)
    
        # рисуем шим
        if flag_shim:
            try:
                if not 'shim' in kwargs:
                    raise Exception('shim file is not specified')
    
                # читаем заголовок файла
                header = duty.read_header(kwargs['shim'], shim.HEADER_PACK)
        
                if header is None:
                    raise Exception('wrong header of shim file')
                
                sampling = int(header[shim.HEADER_PACK_KEYS.index('signal_sampling')])
                duration = int(header[shim.HEADER_PACK_KEYS.index('signal_duration')])
                sawpp = int(header[shim.HEADER_PACK_KEYS.index('saw_count_per_point')])
                ch_count = int(header[shim.HEADER_PACK_KEYS.index('shim_channel_count')])
                R = float(header[shim.HEADER_PACK_KEYS.index('shim_R')])
        
                point_count = int(sampling * duration / 1000)
                shim_count = point_count * sawpp * 4
                
                # читаем значения
                ashim = duty.read_file(kwargs['shim'], 'H', struct.calcsize(shim.HEADER_PACK), shim_count)
    
                if ashim is None:
                    raise Exception('error on reading shim file')
    
                SHIM_HEIGHT = 20 * pcnt
                SHIM_WIDTH = 10
    
                if (POINT_1 == None) or (POINT_1 not in range(len(ashim) // 4)): POINT_1 = 0
                if (POINT_2 == None) or (POINT_2 not in range(POINT_1, len(ashim) // 4)): POINT_2 = len(ashim) // 4
    
                lefts_a = []
                widths_a = []
                heights_a = []
                bottoms_a = []
    
                lefts_b = []
                widths_b = []
                heights_b = []
                bottoms_b = []

                step = 4 * sawpp
                for i in range(POINT_1, POINT_2):
    
                    _xa = ashim[i * step]
                    x_b = ashim[i * step + 1]
                    x_a = ashim[i * step + 2]
                    _xb = ashim[i * step + 3]
    
                    # канал a
                    k1 = x_a / R
                    k2 = 1 - k1
                    
                    w = SHIM_WIDTH * k1
        
                    if w: # нулевые значения не добавляем (не отрисовываем)
                        lefts_a.append((i - POINT_1) * SHIM_WIDTH + SHIM_WIDTH * k2 / 2)
                        widths_a.append(w)
        ##              print(w)

                    # если используется два канала, то считаем и для канала b
                    if ch_count == 2:
                        k1 = x_b / R
                        k2 = 1 - k1
    
                        w = SHIM_WIDTH * k1
    
                        if w: # нулевые значения не добавляем (не отрисовываем)
                            lefts_b.append((i - POINT_1) * SHIM_WIDTH + SHIM_WIDTH * k2 / 2)
                            widths_b.append(w)
        
    
                for i in range(len(lefts_a)):
                    heights_a.append(SHIM_HEIGHT)
                    bottoms_a.append(0)
        
    
                for i in range(len(lefts_b)):
                    heights_b.append(SHIM_HEIGHT)
                    bottoms_b.append(-SHIM_HEIGHT)
        
                plt.subplot(pcnt, 1, num)
                plt.bar(left=lefts_a, width=widths_a, height=heights_a, bottom=bottoms_a, color='g', edgecolor='g', label='Положительные значения')
                plt.bar(left=lefts_b, width=widths_b, height=heights_b, bottom=bottoms_b, color='r', edgecolor='r', label='Отрицательные значения')
                plt.legend(loc='upper left', shadow=True, frameon=True, fontsize='small', title='Шим')
                plt.ylim(ymin=-100, ymax=100)
                plt.xticks(arange(0, (POINT_2 - POINT_1) * SHIM_WIDTH, SHIM_WIDTH * 50 * POINT_COUNT // 200), arange(POINT_1, POINT_2, 50 * POINT_COUNT // 200))
                plt.grid()
    
    
            except Exception as E:
                print('error on plotting shim: ', file=sys.stderr, end='')
                print(E, file=sys.stderr)
        
    
        plt.show()

    except Exception as E:
        print('error in func plot: {}', file=sys.stderr, end='')
        print(E, file=sys.stderr)
    
    # print('Signal plotting finished')

#####################################################################  

if __name__ == "__main__":

    parser = createParser()

    if parser == None:

        # путь к файлу c исходным сигналом
        RAW_FILE_NAME = "D:/c++/AME/Generators/test_main.raw"

        # путь к файлу с отфильтрованным сигналом
        RAWF_FILE_NAME = "D:/c++/AME/Generators/test_main.rawf"

        # путь к файлу шим
        SHIM_FILE_NAME = "D:/c++/AME/Generators/test_main.shim"

        FLAGS = int('00001111', 2)
        print(FLAGS)

        SIGNAL_SAMPLING = 2000 # дискретизация
        SIGNAL_DURATION = 1000
        POINT_1 = 0 # начальная точка
        POINT_2 = 1000 # конечная точка

    else:
        RAW_FILE_NAME = parser.raw_file_name # путь к файлу c исходным сигналом
        RAWF_FILE_NAME = parser.rawf_file_name # путь к файлу с отфильтрованным сигналом
        SHIM_FILE_NAME = parser.shim_file_name # путь к файлу шим
        SIGNAL_SAMPLING = parser.sampling # дискретизация
        SIGNAL_DURATION = parser.duration
        POINT_1 = parser.from_point # начальная точка
        POINT_2 = parser.to_point # конечная точка
        FLAGS = parser.flags

    plot(raw=RAW_FILE_NAME,
         rawf=RAWF_FILE_NAME,
         shim=SHIM_FILE_NAME,
         s=SIGNAL_SAMPLING,
         d=SIGNAL_DURATION,
         p1=POINT_1,
         p2=POINT_2,
         flags=FLAGS)
