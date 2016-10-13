import math
import struct
import sys
import argparse
import array as arr
from scipy import *
from scipy import signal
from scipy.fftpack import fft
from _spectrum_main import signal2spectrum

def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-fmin', '--filter_frequency_min', type=int, required=False)
    parser.add_argument('-fmax', '--filter_frequency_max', type=int, required=False)
    parser.add_argument('-s', '--sampling', type=int, required=False)
    parser.add_argument('-raw', '--raw_file_name', type=str, required=False)
    parser.add_argument('-rawf', '--rawf_file_name', type=str, required=False)

    namespace = parser.parse_args(sys.argv[1:])
    
    if (namespace.filter_frequency_min is None or namespace.filter_frequency_max is None or 
        namespace.sampling is None or 
        namespace.raw_file_name is None or namespace.rawf_file_name is None):

        return None
    
    else:
        return namespace


def filtrate(**kwargs): #fmin, fmax, s, ifn, ofn, data, 

    print('Start signal fourier filtering')
    
    fmin = kwargs['fmin']    # нижняя граница полосы фильтрации
    fmax = kwargs['fmax']     # верхняя граница полосы фильтрации
    raw = kwargs['raw']      # путь к файлу из которого будет считан исходный сигнал
    rawf = kwargs['rawf']      # путь к файлу в который будет записан отфильтрованный сигнал
    sampling = kwargs['s']
    duration = kwargs['d']

    fsdpcnt = int((sampling / 2) * (duration / 1000)) # point_count / 2
    fpcnt = int(sampling / 2)

    fmin_n = int(fmin * fsdpcnt / fpcnt)
    fmax_n = int(fmax * fsdpcnt / fpcnt)
    # print('fsdpcnt=%i  fpcnt=%i  fmin_n=%i  fmax_n=%i' % (fsdpcnt, fpcnt, fmin_n, fmax_n))

    # получаем спектр сигнала
    spectrum, aspec, araw = signal2spectrum(**kwargs)
    
    # print('len(spectrum)=%i' % len(spectrum))

    # обнуляем все значения, которые не входят в диапазон частот
    spectrum[:fmin_n] = 0.0   # в основной части спектра
    spectrum[-fmin_n:] = 0.0  # в зеркальной части спектра
    
    spectrum[fmax_n:fsdpcnt] = 0.0   # в основной части спектра
    spectrum[fsdpcnt:-fmax_n] = 0.0  # в зеркальной части спектра

    # print(spectrum[:fsdpcnt])
    # print(spectrum[fsdpcnt:])

    aflt = arr.array('d', ifft(spectrum).real) #, n=int(sampling * duration / 1000)
    # print('len(aflt)=%i' % len(aflt))

    # сохраняем отфильтрованный сигнал в файл
    try:
        
        fflt = open(rawf, 'wb')
        aflt.tofile(fflt)
        fflt.close()

    except:
        print("Error while saving file", file=sys.stderr)
        return None


    print('Filtration completed successfully')

    return aflt


      

#####################################################################  

if __name__ == "__main__":

    parser = createParser()

    ##############  параметры фильтра  ##############

    if parser == None:

        # параметры для фильтрации
        FILTER_FREQUENCY_MIN = 2000
        FILTER_FREQUENCY_MAX = 4000
        SIGNAL_SAMPLING = 80000 # должна быть минимум в 2 раза больше макс. частоты
        #SIGNAL_AMP = 255

        # путь к файлу из которого будет считан исходный сигнал
        RAW_FILE_NAME = "d:/c++/AME/Generators/test_main.raw"
        
        # путь к файлу в который будет записан отфильтрованный сигнал
        RAWF_FILE_NAME = "d:/c++/AME/Generators/test_main.rawf"
        
    else:

        # параметры для фильтрации
        FILTER_FREQUENCY_MIN = parser.filter_frequency_min
        FILTER_FREQUENCY_MAX = parser.filter_frequency_max
        SIGNAL_SAMPLING = parser.sampling

        # путь к файлу из которого будет считан исходный сигнал
        RAW_FILE_NAME = parser.in_file_name
        
        # путь к файлу в который будет записан отфильтрованный сигнал
        RAWF_FILE_NAME = parser.out_file_name
 
    filtrate(fmin=FILTER_FREQUENCY_MIN,
             fmax=FILTER_FREQUENCY_MAX,
             s=SIGNAL_SAMPLING,
             raw=RAW_FILE_NAME,
             rawf=RAWF_FILE_NAME)
