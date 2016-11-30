# -*- coding: utf-8 -*-

import math
import struct
import sys
import argparse
import matplotlib.pyplot as plt
import array as arr
import random

from _defs import *

MIN_10NS_PSAW = 5
SAW_FREQ = 100000000

FILE_VER = 0x00000002 # 0.0.0.1
SIGNATURE = b'SHIM    '

HEADER_PACK = '<8sIIIIdddIIIIIII' #iIIIIII'

HEADER_PACK_2 = {'order':'<', 'signature':'8s', 'version':'I',
                 'signal_sampling':'I',
                 'signal_freq':'I',
                 'signal_duration':'I',
                 'signal_amplitude':'d',
                 'shim_R':'d',
                 'shim_r':'d',
                 'shim_zero_smooth':'I',
                 'shim_channel_gap':'I',
                 'shim_channel_count':'I',
                 'saw_freq':'I',
                 'saw_count_per_point':'I',
                 'i10ns_count_per_point':'I',
                 'i10ns_count_per_saw':'I'}
                 # 'filter_algorithm':'i',
                 # 'filter_type':'I',
                 # 'filter_freq_min':'I',
                 # 'filter_freq_max':'I',
                 # 'filter_rp':'I',
                 # 'filter_rs':'I',
                 # 'filter_transition_band':'I'}

# для определения позиции нужного значения
HEADER_PACK_KEYS = ['signature',
                    'version',
                    'signal_sampling',
                    'signal_freq',
                    'signal_duration',
                    'signal_amplitude',
                    'shim_R',
                    'shim_r',
                    'shim_zero_smooth',
                    'shim_channel_gap',
                    'shim_channel_count',
                    'saw_freq',
                    'saw_count_per_point',
                    'i10ns_count_per_point',
                    'i10ns_count_per_saw']
                    # 'filter_algorithm',
                    # 'filter_type',
                    # 'filter_freq_min',
                    # 'filter_freq_max',
                    # 'filter_rp',
                    # 'filter_rs',
                    # 'filter_transition_band']

##struct HEADER_PACK {
##  char    signature[8];	    // (8s) SHIM.... 
##  quint32 version		    // (I) версия файла
##  quint32 signal_sampling;        // (I) дискретизация сигнала (точек на 1 сек.)
##  quint32 signal_freq;            // (I) частота сигнала (Гц)
##  quint32 signal_duration;        // (I) длительность сигнала (мсек.)
##  double  signal_amplitude;       // (d) амплитуда исходного сигнала (отклонение от нуля; в условных единицах)
##  double  shim_R;                 // (d) размах сигнала (max - min) после преобразования в ШИМ (в условных единицах)
##  double  shim_r;                 // (d) амплитуда сигнала (отклонение от нуля) после преобразования в ШИМ (в условных единицах)
##  quint32 shim_zero_smooth;       // (I) размывание нуля. значения сигнала попадающие в заданный диапазон обнуляются
##  quint32 shim_channel_gap;       // (I) разрыв между импульсами каналов a и b. значения сигнала уменьшаются на заданную величину, размах сигнала не изменяется. таким образом увеличивается время между импульсами канала a и b
##  quint32 shim_channel_count;     // (I) количество каналов (1 или 2)
##  quint32 saw_freq;               // (I) частота пилы (SAW_FREQ)
##  quint32 saw_count_per_point;    // (I) количество периодов пилы на одну точку сигнала
##  quint32 i10ns_count_per_point;  // (I) количество 10 нс интервалов, которые приходятся на одну точку сигнала
##  quint32 i10ns_count_per_saw;    // (I) количество 10 нс интервалов, которые приходятся на одну пилу
##
##  /* параметры фильтра */
##  qint32  filter_algorithm; 		// (i) алгоритм фильтрации. при (-1) фильтр не применяется
##  quint32  filter_type;      		// (I) тип фильтра - полосовой, ФНЧ, ФВЧ, режекторный
##  quint32 filter_freq_min;  		// (I) нижняя частота сигнала (Гц)
##  quint32 filter_freq_max;  		// (I) верхняя частота сигнала (Гц)
##  quint32 filter_rp;        		// (I) Rp максимальные потери в полосе пропускания в dB
##  quint32 filter_rs;        		// (I) Rs Уровень ослабления сигнала на частотах задержания в dB
##  quint32 filter_transition_band;     // (I) Ширина полосы перехода (Гц)


def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--frequency', type=int, required=False)
    parser.add_argument('-s', '--sampling', type=int, required=False)
    parser.add_argument('-d', '--duration', type=int, required=False)
    parser.add_argument('-a', '--amplitude', type=float, required=False)
    parser.add_argument('-rawfn', '--raw_file_name', type=str, required=False)
    parser.add_argument('-shimfn', '--shim_file_name', type=str, required=False)
    parser.add_argument('-zero', '--zero_smooth', type=int, required=False)
    parser.add_argument('-chgap', '--channel_gap', type=int, required=False)
    parser.add_argument('-chcnt', '--channel_count', type=int, required=False)
    parser.add_argument('-sawpp', '--saw_count_per_point', type=int, required=False)

    # parser.add_argument('-fmin', '--filter_frequency_min', type=int, required=False)
    # parser.add_argument('-fmax', '--filter_frequency_max', type=int, required=False)
    # parser.add_argument('-falg', '--filter_algorithm', type=int, required=False)
    # parser.add_argument('-ftype', '--filter_type', type=int, required=False)
    # parser.add_argument('-rp', '--filter_max_ripple', type=float, required=False)
    # parser.add_argument('-rs', '--filter_min_attenuation', type=float, required=False)
    # parser.add_argument('-tb', '--filter_transition_band', type=int, required=False)

    
    namespace = parser.parse_args(sys.argv[1:])
    
    if (namespace.frequency is None or namespace.sampling is None or
        namespace.duration is None or namespace.amplitude is None or
        namespace.raw_file_name is None or shim_file_name is None or
        namespace.zero_smooth is None or namespace.channel_gap is None or
        namespace.channel_count is None or namespace.saw_count_per_point is None):

        # namespace.filter_frequency_min is None or namespace.filter_frequency_max is None or
        # namespace.filter_algorithm is None or namespace.filter_type is None or        
        # namespace.filter_max_ripple is None or namespace.filter_min_attenuation is None or        
        # namespace.filter_transition_band is None):

        return None
    
    else:
        return namespace
    
def shim(config, **kwargs):
    
    
    try:
        print('shim conversion ... ', end='')

        SIGNAL_FREQUENCY = int(config[c_freq0])
        SIGNAL_SAMPLING = int(config[c_sampling])
        SIGNAL_DURATION = int(config[c_duration])
        SIGNAL_AMPLITUDE = int(config[c_amplitude])
        SHIM_FILE_NAME = get_path(config, 'shim')
        SHIM_ZERO_SMOOTH = int(config[c_zero_smooth])
        SHIM_CHANNEL_GAP = int(config[c_channel_gap])
        SHIM_CHANNEL_COUNT = int(config[c_channel_count])
        SAW_COUNT_PER_POINT = int(config[c_saw_count_per_point])
    
        # эти параметры не учавствуют в вычисленияях, они только записываются в заголовок файла
        # FILTER_FREQUENCY_MIN = kwargs['fmin']
        # FILTER_FREQUENCY_MAX = kwargs['fmax']
        # FILTER_ALGORITHM = kwargs['falg']
        # FILTER_TYPE = kwargs['ftype']
        # Rp = kwargs['rp']
        # Rs = kwargs['rs']
        # TRANSITION_BAND = kwargs['tb']
    
        
        signal_len = int(SIGNAL_SAMPLING * SIGNAL_DURATION / 1000)  
    
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

        
        # вычисляем количество 10 нс интервалов по оси Х, которые приходятся на одну точку сигнала 
        N = int(SAW_FREQ / SIGNAL_SAMPLING)
      
        # подбираем количество пил, таким образом, чтобы на одну точку сигнала 
        # укладывалось ровное количество пил, при заданном количестве 10 нс интервалов.
        # параметр MIN_10NS_PSAW - минимальное количество 10 нс интервалов на одну пилу
        
        ok = False
        while N / SAW_COUNT_PER_POINT > MIN_10NS_PSAW:
            if N % SAW_COUNT_PER_POINT == 0:
                ok = True
                break
    
            SAW_COUNT_PER_POINT += 1
    
      
        if ok == False:
            print("Не найдено подходящее количество пил на точку")
            return False
    
      
        # количество 10 нс интервалов на одну пилу 
        saw_N = int(N / SAW_COUNT_PER_POINT)
    
        # вычисляем новый размах сигнала, который равен количеству 10нс отсчетов на половину пилы 
        R = float(saw_N) / 2.0
      
        # новая амплитуда (половина размаха)
        r = R / 2.0
    
        # вычисляем коэффициент для пересчета уровней сигнала
        k = r / SIGNAL_AMPLITUDE
    
    ##    print('amp=%0.4f  saw_N=%d  R=%0.4f  r=%0.4f  k=%0.8f' % (SIGNAL_AMPLITUDE, saw_N, R, r, k))
    
        # открываем файл для записи преобразованного файла и шим
        try:
    
            fshim = open(SHIM_FILE_NAME, 'wb')
            
        except:
            print("Error while opening shim file", file=sys.stderr)
            return False
    
        # записываем заголовок
        fshim.write(struct.pack(HEADER_PACK,
                                SIGNATURE,
                                FILE_VER,
                                SIGNAL_SAMPLING,
                                SIGNAL_FREQUENCY,
                                SIGNAL_DURATION,
                                SIGNAL_AMPLITUDE,
                                R,
                                r,
                                SHIM_ZERO_SMOOTH,
                                SHIM_CHANNEL_GAP,
                                SHIM_CHANNEL_COUNT,
                                SAW_FREQ,
                                SAW_COUNT_PER_POINT,
                                N,
                                saw_N))
                                # FILTER_ALGORITHM,
                                # FILTER_TYPE,
                                # FILTER_FREQUENCY_MIN,
                                # FILTER_FREQUENCY_MAX,
                                # Rp,
                                # Rs,
                                # TRANSITION_BAND))
        
    ##
    ##  file_signal.write("SIGNAL  \0");
    ##  file_signal.write((char*)&hpack, sizeof(HEADER_PACK));
    ##  file_signal.write((char*)signal, signal_len * sizeof(double));
    ##  file_signal.close();
      
        # вычисляем значения шим сигнала и записываем их в файл
        for i in range(len(araw)):
    
            # читаем уровень сигнала и преобразуем его под новую амплитуду
            y = araw[i] * k
    
            # преобразуем значение для изменения разрыва между импульсами разных каналов
            y *= (1 - SHIM_CHANNEL_GAP / 100.0)
        
            # диапазон размытия уровня нуля
            zs = r * SHIM_ZERO_SMOOTH / 100.0
    
    
            # выставляем нулевые значения шим
    	# время до перехода в 1, канал b 
            _xb = int(R + 1)  # никогда не перейдет в 1
    		
    	# время до перехода в 1, канал a
            _xa = int(R + 1)  # никогда не перейдет в 1
    		
    	# время до перехода в 0, канал a
            x_a = 0      # сразу переход в 0
    		
    	# время до перехода в 0, канал b
            x_b = 0      # сразу переход в 0
    		
    		
    	# вычисляем значения шим. в зависимости от значения y считаем по разному
    	# описание в файле 'определение положения точек.vsd'
    
    	# если нужен только один канал, то независимо от уровня сигнала все значения вычисляем для канала а
            if SHIM_CHANNEL_COUNT == 1:
    		
                # канал a
                _xa = int(r - y)
                x_a = int(R - _xa)
    
                # канал b всегда в нуле
    
    		
            # иначе, если нужны два канала, то вычисляем значения в зависимости от уровня сигнала
            # если уровень сигнала попадает в диапазон размытия нуля (-zs:zs), то значения не меняются
            elif y > zs:
    	
                # канал a
                x_a = int(y)
                _xa = int(R - x_a)
                
                # значения канала b не изменяются
    
    
            elif y < -zs:
    
                # значения канала a не изменяются
                
                # канал b
                x_b = int(-y)
    
                # самую первую точку канала b необходимо обнулить !*/
                if i == 0:      _xb = 0
                else:           _xb = int(R - x_b)
    
          
    
            for saw_num in range(SAW_COUNT_PER_POINT):
                fshim.write(struct.pack('<H', (_xa))) # время до перехода в 1, канал a
                fshim.write(struct.pack('<H', (x_b))) # время до перехода в 0, канал b
                fshim.write(struct.pack('<H', (x_a))) # время до перехода в 0, канал
                fshim.write(struct.pack('<H', (_xb))) # время до перехода в 1, канал b
    
    	
        # в последнее значение для канала b заменяем на R + 1, чтобы канал b всегда выключался
        _xb = int(R + 1)
        for saw_num in range(SAW_COUNT_PER_POINT):
            fshim.seek(-1 * (saw_num * struct.calcsize('H') * 4 + 1), 2)
            fshim.write(struct.pack('<H', (_xb)))
    
    
        fshim.close()

    except Exception as E:
        print('error in function _shim_main.shim(): %s' % E, file=sys.stderr)
        return False
    
    
    print('ok')
    return True


###############################################        

if __name__ == "__main__":

    parser = createParser()

    ########  параметры преобразователя шим  #############

    if parser == None:

        ## ЭТИ ПАРАМЕТРЫ ТОЛЬКО ДЛЯ ОТЛАДКИ ! ##

        SIGNAL_SAMPLING = 16000 # должна быть минимум в 2 раза больше макс. частоты
        SIGNAL_DURATION = 500 # в миллисекундах
        SIGNAL_AMPLITUDE = 512 # величина отклонения от нуля
        
        # путь к файлу исходного сигнала
        RAW_FILE_NAME = "d:/c++/AME/Generators/test_main.raw"

        # путь к файлу шим
        SHIM_FILE_NAME = "d:/c++/AME/Generators/test_main.shim"

        SAW_COUNT_PER_POINT = 1
        SHIM_CHANNEL_GAP = 0
        SHIM_ZERO_SMOOTH = 0
        SHIM_CHANNEL_COUNT = 1

    else:

        # параметры сигнала
        SIGNAL_FREQUENCY = parser.frequency # для сигнала с постоянной частотой
        SIGNAL_SAMPLING = parser.sampling
        SIGNAL_DURATION = parser.duration # в миллисекундах
        SIGNAL_AMPLITUDE = parser.amplitude

        RAW_FILE_NAME = parser.raw_file_name # путь к файлу исходного сигнала
        SHIM_FILE_NAME = parser.shim_file_name # путь к файлу шим

        SHIM_ZERO_SMOOTH = parser.zero_smooth
        SHIM_CHANNEL_GAP = parser.channel_gap
        SHIM_CHANNEL_COUNT = parser.channel_count
        SAW_COUNT_PER_POINT = parser.saw_count_per_point
        
    shim(f=SIGNAL_FREQUENCY,
         s=SIGNAL_SAMPLING,
         d=SIGNAL_DURATION,
         a=SIGNAL_AMPLITUDE,
         rawfn=RAW_FILE_NAME,
         shimfn=SHIM_FILE_NAME,
         zero=SHIM_ZERO_SMOOTH,
         chgap=SHIM_CHANNEL_GAP,
         chcnt=SHIM_CHANNEL_COUNT,
         sawpp=SAW_COUNT_PER_POINT)
         # fmin=FILTER_FREQUENCY_MIN,
         # fmax=FILTER_FREQUENCY_MAX,
         # falg=FILTER_ALGORITHM,
         # ftype=FILTER_TYPE,
         # rp=Rp,
         # rs=Rs,
         # tb=TRANSITION_BAND)

