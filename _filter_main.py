import math
import struct
import sys
import argparse
import array as arr
from scipy import *
from scipy import signal
import _filters_design as fd


def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-fmin', '--filter_frequency_min', type=int, required=False)
    parser.add_argument('-fmax', '--filter_frequency_max', type=int, required=False)
    parser.add_argument('-s', '--sampling', type=int, required=False)
    parser.add_argument('-falg', '--filter_algorithm', type=int, required=False)
    parser.add_argument('-ftype', '--filter_type', type=int, required=False)
    parser.add_argument('-rp', '--filter_max_ripple', type=float, required=False)
    parser.add_argument('-rs', '--filter_min_attenuation', type=float, required=False)
    parser.add_argument('-tb', '--filter_transition_band', type=int, required=False)
    parser.add_argument('-ifn', '--in_file_name', type=str, required=False)
    parser.add_argument('-ofn', '--out_file_name', type=str, required=False)

    namespace = parser.parse_args(sys.argv[1:])
    
    if (namespace.filter_frequency_min == None or namespace.filter_frequency_max == None or
        namespace.sampling == None or namespace.filter_type == None or
        namespace.filter_max_ripple == None or namespace.filter_min_attenuation == None or
        namespace.in_file_name == None or namespace.out_file_name == None or
        namespace.filter_transition_band == None):

        return None
    
    else:
        return namespace



def filtrate(fmin, fmax, s, falg, ftype, rp, rs, tb, ifn, ofn, data, **kwargs):

    print('Start signal filtering')

    FILTER_FREQUENCY_MIN = fmin
    FILTER_FREQUENCY_MAX = fmax
    SIGNAL_SAMPLING = s

    FILTER_ALGORITHM = falg
    FILTER_TYPE = ftype
    
    Rp = rp  # максимальные потери в полосе пропускания в dB
    Rs = rs  # Уровень ослабления сигнала на частотах задержания в dB

    TRANSITION_BAND = tb

    IN_FILE_NAME = ifn  # путь к файлу из которого будет считан исходный сигнал
    OUT_FILE_NAME = ofn  # путь к файлу в который будет записан отфильтрованный сигнал

    # если сигнал передан как массив, то используем его
    if 'data' in kwargs:
        araw = data

    else:
        # иначе читаем исходный файл
        try:

            fraw = open(IN_FILE_NAME, 'rb')
            araw = arr.array('d')
            araw.fromstring(fraw.read())
            fraw.close()
        
        except:
            print("Error while opening file", file=sys.stderr)
            return None

##    b = None
##    a = None
    
    # если алгоритм = -1, то возвращаем исходный массив без изменений
    if FILTER_ALGORITHM == fd.f_algorithm_none:
        return araw

    # Получаем параметры фильтра b, a
    elif FILTER_ALGORITHM == fd.f_algorithm_cheby1:

#        ss2 = SIGNAL_SAMPLING / 2
#        Wp = [FILTER_FREQUENCY_MIN / ss2, FILTER_FREQUENCY_MAX / ss2] # диапазон пропускаемых частот (числа в диапазоне 0..1)
#        Ws = [(FILTER_FREQUENCY_MIN - TRANSITION_BAND) / ss2, (FILTER_FREQUENCY_MAX + TRANSITION_BAND) / ss2] # дипазон частот задержания ( Ws(1) < Wp(1) < Wp(2) < Ws(2) )


#        Wp = FILTER_FREQUENCY_MIN / ss2
#        Ws = (FILTER_FREQUENCY_MIN - TRANSITION_BAND) / ss2
#
#        n, Wn = signal.cheb1ord(Wp, Ws, Rp, Rs)
#        print(Wp, Wn, n, Wn)
#
#        # параметры фильтра b, a
#        b, a = signal.cheby1(n, Rp, Wn, btype='lowpass')
#
        b, a, lines, title = fd.cheby1(ftype=FILTER_TYPE, fmin=FILTER_FREQUENCY_MIN, fmax=FILTER_FREQUENCY_MAX, tb=TRANSITION_BAND, sampling=SIGNAL_SAMPLING, rp=Rp, rs=Rs)

##        b,a = signal.iirdesign(Wp, Ws, Rp, Rs, ftype='cheby1')
        
    elif FILTER_ALGORITHM == fd.f_algorithm_cheby2:

        b, a, lines, title = fd.cheby2(ftype=FILTER_TYPE, fmin=FILTER_FREQUENCY_MIN, fmax=FILTER_FREQUENCY_MAX, tb=TRANSITION_BAND, sampling=SIGNAL_SAMPLING, rp=Rp, rs=Rs)
        
    elif FILTER_ALGORITHM == fd.f_algorithm_butt:
        
        b, a, lines, title = fd.butt(ftype=FILTER_TYPE, fmin=FILTER_FREQUENCY_MIN, fmax=FILTER_FREQUENCY_MAX, tb=TRANSITION_BAND, sampling=SIGNAL_SAMPLING, rp=Rp, rs=Rs)
        
    elif FILTER_ALGORITHM == fd.f_algorithm_ellip:
        
        b, a, lines, title = fd.ellip(ftype=FILTER_TYPE, fmin=FILTER_FREQUENCY_MIN, fmax=FILTER_FREQUENCY_MAX, tb=TRANSITION_BAND, sampling=SIGNAL_SAMPLING, rp=Rp, rs=Rs)
        
    else:
        print("Unknown filter algorithm parameter", file=sys.stderr)
        return None


    # фильтрация
    # aflt = arr.array('d', signal.lfilter(b, a, araw))
    aflt = arr.array('d', signal.filtfilt(b, a, araw))

    # сохраняем отфильтрованный сигнал в файл
    try:
        
        fflt = open(OUT_FILE_NAME, 'wb')
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

        # алгоритм фильтрации
        FILTER_ALGORITHM = fd.f_algorithm_cheby1
        
        # тип фильтра
        FILTER_TYPE = fd.f_type_bandpass

        # Уровень пульсаций в полосе пропускания
        FILTER_RP = 2   # в dB

        # Уровень ослабления сигнала на частотах задержания
        FILTER_RS = 80 # в dB
        
        # путь к файлу из которого будет считан исходный сигнал
        IN_FILE_NAME = "d:/c++/AME/Generators/test_main.raw"
        
        # путь к файлу в который будет записан отфильтрованный сигнал
        OUT_FILE_NAME = "d:/c++/AME/Generators/test_main.rawf"

        # полоса перехода
        TRANSITION_BAND = 200
        
    else:

        # параметры для фильтрации
        FILTER_FREQUENCY_MIN = parser.filter_frequency_min
        FILTER_FREQUENCY_MAX = parser.filter_frequency_max
        SIGNAL_SAMPLING = parser.sampling

        # алгоритм фильтрации
        FILTER_ALGORITHM = parser.filter_algorithm
        
        # тип фильтра
        FILTER_TYPE = parser.filter_type

        # Уровень пульсаций в полосе пропускания
        FILTER_RP = parser.filter_max_ripple

        # Уровень ослабления сигнала на частотах задержания
        FILTER_RS = parser.filter_min_attenuation

        # путь к файлу из которого будет считан исходный сигнал
        IN_FILE_NAME = parser.in_file_name
        
        # путь к файлу в который будет записан отфильтрованный сигнал
        OUT_FILE_NAME = parser.out_file_name

        # полоса перехода
        TRANSITION_BAND = parser.filter_transition_band

 
    filtrate(fmin=FILTER_FREQUENCY_MIN,
             fmax=FILTER_FREQUENCY_MAX,
             s=SIGNAL_SAMPLING,
             falg=FILTER_ALGORITHM,
             ftype=FILTER_TYPE,
             rp=FILTER_RP,
             rs=FILTER_RS,
             tb=TRANSITION_BAND,
             ifn=IN_FILE_NAME,
             ofn=OUT_FILE_NAME)
