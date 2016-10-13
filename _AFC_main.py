import math
import struct
import sys
import argparse
import matplotlib.pyplot as plt 
import array as arr
import numpy as np
from scipy import *
from scipy import signal
import _filters_design as fd


def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-fmin', '--frequency_min', type=int, required=False)
    parser.add_argument('-fmax', '--frequency_max', type=int, required=False)
    parser.add_argument('-s', '--sampling', type=int, required=False)
    parser.add_argument('-falg', '--filter_algorithm', type=int, required=False)
    parser.add_argument('-ftype', '--filter_type', type=int, required=False)
    parser.add_argument('-rp', '--maximum_ripple', type=float, required=False)
    parser.add_argument('-rs', '--minimum_attenuation', type=float, required=False)
    parser.add_argument('-tb', '--transition_band', type=int, required=False)
    
    namespace = parser.parse_args(sys.argv[1:])
    
    if (namespace.frequency_min == None or namespace.frequency_max == None or
        namespace.sampling == None or namespace.filter_type == None or
        namespace.maximum_ripple == None or namespace.minimum_attenuation == None):

        return None
    
    else:
        return namespace


def afc(**kwargs):

    print('Filter AFC determining')

    SIGNAL_FREQUENCY_MIN = kwargs['fmin']
    SIGNAL_FREQUENCY_MAX = kwargs['fmax']
    SIGNAL_SAMPLING = kwargs['s'] # дискретизация

    FILTER_ALGORITHM = kwargs['falg']
    FILTER_TYPE = kwargs['ftype']

    Rp = kwargs['rp']   # максимальные потери в полосе пропускания в dB
    Rs = kwargs['rs']   # Уровень ослабления сигнала на частотах задержания в dB

    TRANSITION_BAND = kwargs['tb']

    # Получаем требуемый 
    # и 
    if FILTER_ALGORITHM == fd.f_algorithm_cheby1:

        b, a, lines, title = fd.cheby1(ftype=FILTER_TYPE, fmin=SIGNAL_FREQUENCY_MIN, fmax=SIGNAL_FREQUENCY_MAX, tb=TRANSITION_BAND, sampling=SIGNAL_SAMPLING, rp=Rp, rs=Rs)
        
    elif FILTER_ALGORITHM == fd.f_algorithm_cheby2:

        b, a, lines, title = fd.cheby2(ftype=FILTER_TYPE, fmin=SIGNAL_FREQUENCY_MIN, fmax=SIGNAL_FREQUENCY_MAX, tb=TRANSITION_BAND, sampling=SIGNAL_SAMPLING, rp=Rp, rs=Rs)
        
    elif FILTER_ALGORITHM == fd.f_algorithm_butt:

        b, a, lines, title = fd.butt(ftype=FILTER_TYPE, fmin=SIGNAL_FREQUENCY_MIN, fmax=SIGNAL_FREQUENCY_MAX, tb=TRANSITION_BAND, sampling=SIGNAL_SAMPLING, rp=Rp, rs=Rs)
        
    elif FILTER_ALGORITHM == fd.f_algorithm_ellip:
        
        b, a, lines, title = fd.ellip(ftype=FILTER_TYPE, fmin=SIGNAL_FREQUENCY_MIN, fmax=SIGNAL_FREQUENCY_MAX, tb=TRANSITION_BAND, sampling=SIGNAL_SAMPLING, rp=Rp, rs=Rs)
        
    else:
        sys.exit(1)

##    print("Wp={}, Ws={}, tb={}, type={}".format(Wp, Ws, TRANSITION_BAND, FILTER_TYPE))
##    print("n={}, Wn={}".format(n, Wn))

    # расчет АЧХ
    w, h = signal.freqz(b, a)
    
    plt.subplot(111)
##    plt.semilogx(w / np.pi * ss2, 20 * np.log10(abs(h)))
    plt.plot(w / np.pi * SIGNAL_SAMPLING / 2, 20 * np.log10(abs(h)))
##    plt.axis([0, np.amax(w) / np.pi * ss2, -Rs - 20, Rp])
    plt.xlabel('Frequency')
    plt.ylabel('Amplitude response [dB]')
    plt.grid()
    plt.title(title)
    
    # рисуем линии частоты среза, частоты перехода и уровни Rp и Rs
    if lines[0][0] != None:
        plt.axvline(lines[0][0], color='green', linestyle='dashed') # cutoff frequency 1

    if lines[0][1] != None:
        plt.axvline(lines[0][1], color='green', linestyle='dashed') # cutoff frequency 1

    if lines[1][0] != None:
        plt.axvline(lines[1][0], color='red', linestyle='dashed') # cutoff frequency 1

    if lines[1][1] != None:
        plt.axvline(lines[1][1], color='red', linestyle='dashed') # cutoff frequency 1
        
    plt.axhline(-Rp, color='green') # rp
    plt.axhline(-Rs, color='red') # rs
    
    plt.show()
       

#####################################################################  

if __name__ == "__main__":

    parser = createParser()

    ##############  параметры фильтра  ##############

    if parser == None:

        # параметры для фильтрации
        SIGNAL_FREQUENCY_MIN = 3000
        SIGNAL_FREQUENCY_MAX = 4000
        SIGNAL_SAMPLING = 40000 # должна быть минимум в 2 раза больше макс. частоты
        #SIGNAL_AMP = 255

        # алгоритм фильтрации
        FILTER_ALGORITHM = fd.f_algorithm_ellip
        
        # тип фильтра
        FILTER_TYPE = fd.f_type_bandpass

        # Уровень пульсаций в полосе пропускания
        FILTER_RP = 2   # в dB

        # Уровень ослабления сигнала на частотах задержания
        FILTER_RS = 40.0 # в dB

        TRANSITION_BAND = 280
        
    else:

        # параметры для фильтрации
        SIGNAL_FREQUENCY_MIN = parser.frequency_min
        SIGNAL_FREQUENCY_MAX = parser.frequency_max
        SIGNAL_SAMPLING = parser.sampling

        # алгоритм фильтрации
        FILTER_ALGORITHM = parser.filter_algorithm
        
        # тип фильтра
        FILTER_TYPE = parser.filter_type

        # Уровень пульсаций в полосе пропускания
        FILTER_RP = parser.maximum_ripple

        # Уровень ослабления сигнала на частотах задержания
        FILTER_RS = parser.minimum_attenuation

        TRANSITION_BAND = 200
        if parser.transition_band != None:
            TRANSITION_BAND = parser.transition_band

##        TRANSITION_BAND_H = 200
##        if parser.transition_band_h != None:
##            TRANSITION_BAND_H = parser.transition_band_h
        
    afc(fmin=SIGNAL_FREQUENCY_MIN,
             fmax=SIGNAL_FREQUENCY_MAX,
             s=SIGNAL_SAMPLING,
             falg=FILTER_ALGORITHM,
             ftype=FILTER_TYPE,
             rp=FILTER_RP,
             rs=FILTER_RS,
             tb=TRANSITION_BAND)
