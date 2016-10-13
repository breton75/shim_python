import math
import struct
import sys
import argparse
import matplotlib.pyplot as plt
import array as arr
import numpy as np
from scipy import *
from scipy import signal

HEADER = '<4sI4s4sIHHIIHH4sI'

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-fname', '--file_name', type=str, required=False)

    namespace = parser.parse_args(sys.argv[1:])

    if (namespace.file_name == None):

        return None

    else:
        return namespace


def read_header(file_name):
    

    try:
        f = open(file_name, 'rb')

    except (OSError) as msg:
        print(msg, file=sys.stderr)
        return None

    h = struct.unpack(HEADER, f.read(struct.calcsize(HEADER)))
    f.close()

    return h


def read_file(file_name, dtype, offset, count):
    try:

        f = open(file_name, 'rb')
        f.seek(offset)
        a = arr.array(dtype)
        a.fromfile(f, count)
        if count != len(a):
            raise ValueError()

        f.close()

    except (OSError) as msg:
        print(msg, file=sys.stderr)
        return None

    except (ValueError, EOFError):
        print('wrong size: estimated %i, got %i' % (count, len(a)), file=sys.stderr)
        # print('Ошибка чтения данных. Ожидалось значений: %i, получено: %i' % (count, len(a)), file=sys.stderr)
        f.close()
        return None

    return a


def wav(**kwargs):

    print('Start WAV file reading')

    if 'file_name' in kwargs:
        file_name = kwargs['file_name']

    else:
        print('Имя файла не задано')
        return -1

    header = read_header(file_name)
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
    a = read_file(file_name, 'b', struct.calcsize(HEADER), header[12])

    # преобразуем значения к типу double
    ad = arr.array('d')
    ad.fromlist(a.tolist())

    if 'to_file' in kwargs:
        f = open(kwargs['to_file'], 'wb')
        ad.tofile(f)
        f.close()

    print('WAV file reading finished')

    return ad


#####################################################################  

if __name__ == "__main__":

    parser = createParser()

    if parser == None:

        # путь к файлу c исходным сигналом
        FILE_NAME = "D:/c++/AME/imperia march r.wav"


    else:
        FILE_NAME = parser.file_name # путь к файлу c исходным сигналом
        

    wav(file_name=FILE_NAME)
