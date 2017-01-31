# -*- coding: utf-8 -*-

import math
import struct
import sys
import argparse
import matplotlib.pyplot as plt
import array as arr
import numpy as np
from scipy import *
from scipy import signal
import _duty as duty
from _defs import *

HEADER = '<4sI4s4sIHHIIHH4sI'


def read_wav(**kwargs):

    print('Start WAV file reading')

    if 'file_name' in kwargs:
        file_name = kwargs['file_name']

    else:
        print('Имя файла не задано')
        return -1

    header = duty.read_header(file_name, HEADER)
    print(header)

    if header[0] != b'RIFF':
        print('Неверный формат файла. ''RIFF'' не найдено.')
        return -1

    if header[2] != b'WAVE':
        print('Неверный формат файла. ''WAVE'' не найдено')
        return -1

    if header[5] != 1:
        print('Неверный формат файла. Поддерживаются только файлы без сжатия.')
        return -1

    if header[6] != 1:
        print('Неверный формат файла. Поддерживаются только ''Моно'' файлы')
        return -1

    if header[10] != 8:
        print('Неверный формат файла. Поддерживаются только 8-битные фалы')
        return -1

    # if header[11] != b'data':
    #     print('Неверный формат файла. ''data'' не найдено.')
    #     return -1


    # читаем файл
    a = duty.read_file(file_name, 'b', struct.calcsize(HEADER), header[12])

    # преобразуем значения к типу double
    ad = arr.array('d')
    ad.fromlist(a.tolist())

    if 'to_file' in kwargs:
        f = open(kwargs['to_file'], 'wb')
        ad.tofile(f)
        f.close()

    print('WAV file reading finished')

    return ad


def write_wav(config, **kwargs):
    print('формируем wav файл ... ', end='')

    try:
        
        araw = None

        # если сигнал передан как массив, то используем его
        if 'data' in kwargs:
            araw = kwargs['data']
    
        else: # иначе читаем исходный файл
            try:
                
                araw = get_path(config, 'rawf')

                with open(raw, 'rb') as f:
                    araw = arr.array('d')
                    araw.fromfile(f, point_count)
            
            except:
                print("Ошибка чтения файла исходного сигнала", file=sys.stderr)
                return None

    
        if araw is None:
            raise Exception('Не указан источник исходного сигнала')


        wav_file_name = get_path(config, 'wav')  # путь к файлу в который будет записан сигнал

        sampling = config[c_sampling]
        bps = struct.calcsize('i')  # Количество байт для одного сэмпла, включая все каналы.
        max_val = config[c_amplitude]

        ttt = open("d:/testwav.dat", "wb")

        with open(wav_file_name, 'wb') as wav:
            wav.write(struct.pack(HEADER,
                                  b'RIFF',
                                  len(araw) * bps + struct.calcsize(HEADER) - 8,
                                  b'WAVE' ,
                                  b'fmt ',
                                  16,      # 16 для формата PCM
                                  1,       # Для PCM = 1
                                  1,       # Количество каналов. Моно = 1, Стерео = 2
                                  sampling,
                                  bps * sampling,
                                  bps,
                                  bps * 8,
                                  b'data',
                                  len(araw) * bps))

            for a in araw:
                val = int((a / max_val) * 0x7FFFFFFF)
                # print(val)
                wav.write(struct.pack('i', val))

                # with open("d:/testwav.dat", "ab") as ttt:
                ttt.write(struct.pack('i', val))




        print('ok')

    except Exception as E:
        print('ошибка:\n\t%s' % E, file=sys.stderr)
        return araw

