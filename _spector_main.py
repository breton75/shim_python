import math
import struct
import sys
import argparse
import matplotlib.pyplot as plt
import matplotlib.axes as axs
import array as arr
import numpy as np
from scipy import *
from scipy import signal

def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-raw', '--raw_file_name', type=str, required=False)
    parser.add_argument('-rawf', '--rawf_file_name', type=str, required=False)
    parser.add_argument('-p1', '--from_point', type=int, required=False)
    parser.add_argument('-p2', '--to_point', type=int, required=False)
    parser.add_argument('-s', '--sampling', type=float, required=False)

    namespace = parser.parse_args(sys.argv[1:])
    
    if (namespace.raw_file_name == None or namespace.rawf_file_name == None or
        namespace.sampling == None or
        namespace.from_point == None or namespace.to_point == None):

        return None
    
    else:
        return namespace


def spector(**kwargs):

    print('Start signal plotting')

    RAW_FILE_NAME = kwargs['raw'] # путь к файлу c исходным сигналом
    RAWF_FILE_NAME = kwargs['rawf'] # путь к файлу с отфильтрованным сигналом
    SIGNAL_SAMPLING = kwargs['s'] # дискретизация
    POINT_1 = kwargs['p1'] # начальная точка
    POINT_2 = kwargs['p2'] # конечная точка



    # читаем файл c исходным сигналом
    try:

        fraw = open(RAW_FILE_NAME, 'rb')
        araw = arr.array('d')
        araw.fromstring(fraw.read())
        fraw.close()
        
    except:
        print("Error while opening raw signal file", file=sys.stderr)
        sys.exit (1)

    # читаем файл c отфильтрованным сигналом
    try:

        fflt = open(RAWF_FILE_NAME, 'rb')
        aflt = arr.array('d')
        aflt.fromstring(fflt.read())
        fflt.close()
        
    except:
        print("Error while opening filtered signal file", file=sys.stderr)
        sys.exit (1)    

    # рисуем спектры
    plt.subplot(211)
    f, Pxx_den = signal.welch(araw, SIGNAL_SAMPLING, scaling='density', nperseg=1024)
    plt.semilogy(f, Pxx_den)
    plt.grid()
    
    plt.subplot(212)
    f, Pxx_den = signal.welch(aflt, SIGNAL_SAMPLING, scaling='density', nperseg=1024)
    plt.semilogy(f, Pxx_den, )
    plt.grid()
    
    plt.show()

    print('Signal plotting finished')


#####################################################################  

if __name__ == "__main__":

    parser = createParser()

    if parser == None:

        # путь к файлу c исходным сигналом
        RAW_FILE_NAME = "D:/c++/AME/Generators/test_main.raw"
        
        # путь к файлу с отфильтрованным сигналом
        RAWF_FILE_NAME = "D:/c++/AME/Generators/test_main.rawf"

        SIGNAL_SAMPLING = 8000 # дискретизация
        POINT_1 = 0 # начальная точка
        POINT_2 = 2000 # конечная точка
        
    else:
        RAW_FILE_NAME = parser.raw_file_name # путь к файлу c исходным сигналом
        RAWF_FILE_NAME = parser.rawf_file_name # путь к файлу с отфильтрованным сигналом
        SIGNAL_SAMPLING = parser.sampling # дискретизация
        POINT_1 = parser.from_point # начальная точка
        POINT_2 = parser.to_point # конечная точка

    plot(raw=RAW_FILE_NAME,
         rawf=RAWF_FILE_NAME,
         s=SIGNAL_SAMPLING,
         p1=POINT_1,
         p2=POINT_2)
