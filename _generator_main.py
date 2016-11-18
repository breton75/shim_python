import math
import struct
import sys
import argparse
import matplotlib.pyplot as plt
import array
import random
import numpy as np

from _defs import *

s_type_noise = 0
s_type_sinus = 1
s_type_meandr = 2
s_type_meandr_random = 3
s_type_sinus_noise = 4
s_type_sinus_sinus_noise = 5
s_type_lfm = 6


def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', type=int, required=False)
    parser.add_argument('-f', '--frequency', type=int, required=False)
    parser.add_argument('-s', '--sampling', type=int, required=False)
    parser.add_argument('-d', '--duration', type=int, required=False)
    parser.add_argument('-h', '--hush', type=int, required=False)
    parser.add_argument('-a', '--amplitude', type=float, required=False)
    parser.add_argument('-fi', '--fade_in', type=int, required=False)
    parser.add_argument('-fo', '--fade_out', type=int, required=False)
    parser.add_argument('-fn', '--file_name', type=str, required=False)

    namespace = parser.parse_args(sys.argv[1:])
    
    if (namespace.type == None or
        namespace.frequency == None or namespace.sampling == None or
        namespace.amplitude == None or namespace.file_name == None):

        return None
    
    else:
        return namespace
    
def generate(config=None, **kwargs):
    try:

        print('generating signal ... ', end='')
        
        if config:
            signal_type = get_cfg_param(config, c_signal_type, 0, 'i') # config[c_signal_type]
            signal_frequency = get_cfg_param(config, c_freq, 0, 'i') # config[c_freq]
            signal_sampling = get_cfg_param(config, c_sampling, 0, 'i') # config[c_sampling]
            signal_duration = get_cfg_param(config, c_duration, 0, 'i') #config[c_duration]
            signal_amplitude = get_cfg_param(config, c_amplitude, 0, 'i') # config[c_amplitude]
            fade_in = get_cfg_param(config, c_fadein, 0, 'i') # config[c_fadein]
            fade_out = get_cfg_param(config, c_fadeout, 0, 'i') # config[c_fadeout]
            file_name = get_path(config, 'raw')
            # hush_duration = config[c_hush]
            hush_duration = get_cfg_param(config, c_hush, 0, 'i')

        elif kwargs:
            signal_type = kwargs['t']
            signal_frequency = kwargs['f']
            signal_sampling = kwargs['s']
            signal_duration = kwargs['d']
            signal_amplitude = kwargs['a']
            fade_in = kwargs['fi']
            fade_out = kwargs['fo']
            file_name = kwargs['fn']
            hush_duration = kwargs['h']
            # meandr_pulse_width = kwargs['mpw']
            # meandr_pulse_interval = kwargs['mpi']

        else:
            raise Exception('Params are not specified')

            
        #общее количество точек, которое будет обсчитано
        point_count = int(signal_sampling * (signal_duration - hush_duration) / 1000)
        hush_count = int(signal_sampling * hush_duration / 1000)
    
        # количество точек на раскачку сигнала
        fade_in_point_count = int(point_count / 100 * fade_in) if fade_in > 0 else 0
        fade_in_step = 1 / fade_in_point_count if fade_in > 0 else 0.0
    
        # количество точек на затухание сигнала    
        fade_out_point_count = int(point_count / 100 * fade_out) if fade_out > 0 else 0
        fade_out_step = 1 / fade_out_point_count if fade_out > 0 else 0.0
        # шаг приращения по оси x
        x_step = signal_frequency / signal_sampling
        
        # формируем сырой сигнал
        if signal_type == s_type_noise:
            y_raw = [random.uniform(-signal_amplitude, signal_amplitude) for _counter in range(point_count)]
            # y_raw = [random.uniform(0, signal_amplitude * 2) for _counter in range(point_count)]
        
        elif signal_type == s_type_sinus:
            # y_raw = [signal_amplitude * math.sin( x_step * _counter * math.pi * 2 + 0.5) for _counter in range(point_count)]
            y_raw = [signal_amplitude * math.sin( x_step * _counter * math.pi * 2) for _counter in range(point_count)]

        elif signal_type == s_type_meandr:
            meandr_pulse_width = get_cfg_param(config, c_meandr_pulse_width, 0, 'i') # config[]
            meandr_pulse_interval = get_cfg_param(config, c_meandr_pulse_interval, 0, 'i') # config[]
            meandr_channel_count = get_cfg_param(config, c_meandr_channel_count, 2, 'i') # config[]

            ms = 0.000001 # 1 микросекунда

            # длительность одного отсчета (сэмпла)
            sample_time = round(1.0 / signal_sampling, 9)

            # длительность одного импульса
            pulse_time = round(ms * meandr_pulse_width, 9)

            # длительность одного интервала
            interval_time = round(ms * meandr_pulse_interval, 9)

            # количество отсчетов (сэмплов) на один импульс
            n_imp = int(meandr_pulse_width * meandr_channel_count * signal_sampling / 1000000)
            if meandr_pulse_width % (1000000 // signal_sampling) != 0:
                raise Exception('При заданной дискретизации длина импульса меандра должна быть кратна %i' % (1000000 // signal_sampling))
                                
            # количество отсчетов (сэмплов) на один интервал
            n_int = int(meandr_pulse_interval * signal_sampling / 1000000)
            if meandr_pulse_interval % (1000000 // signal_sampling) != 0:
                raise Exception('При заданной дискретизации длина интервала между импульсами меандра должна быть кратна %i' % (1000000 // signal_sampling))


            # длина одного периода
            n = n_imp + n_int

            # выводим пердупреждение, если если в заданное количество точек не укладывается ровное количество периодов
            if point_count % n != 0:
                print('Предпреждение: количество периодов меандра не кратно длине сигнала')

            print('sample_time=%f  pulse_time=%f  interval_time=%f  n_imp=%i  n_int=%i  n=%i  meandr_pulse_width=%i  meandr_pulse_interval=%i' % (sample_time, pulse_time, interval_time, n_imp, n_int, n, meandr_pulse_width, meandr_pulse_interval))

            # пустой массив
            y_raw = np.empty(point_count, dtype=float)

            # если два канала, то периодически меняем знак сигнала
            # ik = (-1)**(meandr_channel_count - 1)
            # k = 1

            # расставляем импульсы
            for i in range(point_count):
                # k *= ik
                # period_num = i // n
                o = i % n #- period_num * n

                if meandr_channel_count == 1:
                    y_raw[i] = signal_amplitude * int(o // n_imp == 0)
                    

                else:
                    if o < n_imp/2: k = 1
                    else: k = -1

                    y_raw[i] = signal_amplitude * int(o // n_imp == 0) * k



                # signal_amplitude * val

                print('i=%i  period_num = %i  val=%0.2f' % (i, i//n, y_raw[i]))
                
                # y_raw = [signal_amplitude * math.sin( x_step * _counter * math.pi * 2) for _counter in range(point_count)]            
    
        elif signal_type == s_type_sinus_noise:
            y_raw = [signal_amplitude * math.sin( x_step * _counter * math.pi * 2) * random.random()  for _counter in range(point_count)]
    
        elif signal_type == s_type_sinus_sinus_noise:  #
            k = 0.5
            y_raw = [(signal_amplitude * math.sin( x_step * _counter * math.pi * 2) + (signal_amplitude * k) * math.sin(x_step * k * _counter * math.pi * 2)) * random.random()  for _counter in range(point_count)]
    
        elif signal_type == s_type_lfm:
            f0 = config[c_freq_min] # начальная частота
            f1 = config[c_freq_max] # конечная частота
            fd = signal_sampling   # частота дискретизации
            T = signal_duration/1000 # время в секундах
            d = 1 / fd * T # шаг приращения

            y_raw = [signal_amplitude * math.cos(2 * math.pi * f0 / fd * n + d * math.pi * (f1 - f0) / fd * n**2) for n in range(point_count)]
            #  

        # применяем параметры раскачки и затухания и сохраняем конечный сигнал
        y = []
        y.extend([y_raw[_counter] * (_counter * fade_in_step) for _counter in range(fade_in_point_count)])
        y.extend(y_raw[fade_in_point_count : point_count - fade_out_point_count])
        y.extend([y_raw[point_count - _counter] * (_counter * fade_out_step) for _counter in range(fade_out_point_count, 0, -1)])

        # добавляем тишину в конце, если необходимо
        # print(np.zeros(hush_count))
        y.extend(np.zeros(hush_count))
    
        print('ok')
    

        # пишем в файл
        print('saving signal ...', end='')
        try:
            f = open(file_name, 'wb')
            arr = array.array('d')
            arr.fromlist(y)
            arr.tofile(f)
            f.close()
    
            print('ok')
            
        except Exception as E:
            raise Exception(E)
    

    except Exception as E:
        print('error in function generate(): ', file=sys.stderr, end='')
        print(E, file=sys.stderr)
        return None
    
    return arr


###############################################        

if __name__ == "__main__":

    parser = createParser()

    ########  параметры генератора  #############

    if parser == None:

        # параметры сигнала
        signal_type = s_type_sinus_noise
        signal_frequency = 3000
        signal_sampling = 16000 # должна быть минимум в 2 раза больше макс. частоты
        signal_duration = 100 # в миллисекундах
        signal_amplitude = 512 # величина отклонения от нуля
        HUSH = 0

        # раскачка и затухание сигнала в процентах от общей длины сигнала
        fade_in = 0
        fade_out = 0
        
        # путь к файлу в который будет записан сигнал
        file_name = "d:/c++/AME/Generators/test_random.raw"
        
    else:

        # параметры сигнала
        signal_type = parser.type
        signal_frequency = parser.frequency
        signal_sampling = parser.sampling
        signal_duration = parser.duration # в миллисекундах
        signal_amplitude = parser.amplitude
        HUSH = parser.hash # тишина после сигнала мс.

        # раскачка и затухание сигнала в процентах от общей длины сигнала
        fade_in = parser.fade_in
        fade_out = parser.fade_out

        # путь к файлу в который будет записан сигнал
        file_name = parser.file_name


    generate(t=signal_type,
             s=signal_sampling,
             f=signal_frequency,
             d=signal_duration,
             h=HUSH,
             a=signal_amplitude,
             fi=fade_in,
             fo=fade_out,
             fn=file_name)

    
