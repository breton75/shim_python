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
        

        signal_type = int(config[c_signal_type])
        signal_frequency = int(config[c_freq])
        signal_sampling = int(config[c_sampling])
        signal_duration = int(config[c_duration])
        signal_amplitude = int(config[c_amplitude])
        fade_in = int(config[c_fadein])
        fade_out = int(config[c_fadeout])
        file_name = get_path(config, 'raw')
        hush_duration = int(config[c_hush])
        repeat_count = int(config[c_repeat_count])
        if repeat_count < 1: repeat_count = 1
        pause = int(config[c_pause])

        config[c_duration] = signal_duration * repeat_count + pause

            # meandr_pulse_width = kwargs['mpw']
            # meandr_pulse_interval = kwargs['mpi']
            
        #общее количество точек, которое будет обсчитано
        point_count = int(signal_sampling * (signal_duration - hush_duration) / 1000)
        hush_count = int(signal_sampling * hush_duration / 1000)
        pause_count = int(signal_sampling * pause / 1000)
    
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

            y_raw = meandr(config, **kwargs)
            
            if y_raw is None:
                raise Exception('не удалось сформировать сигнал')

    
        elif signal_type == s_type_sinus_noise:
            y_raw = [signal_amplitude * math.sin( x_step * _counter * math.pi * 2) * random.random()  for _counter in range(point_count)]
    
        elif signal_type == s_type_sinus_sinus_noise:  #
            k = 0.5
            y_raw = [(signal_amplitude * math.sin( x_step * _counter * math.pi * 2) + (signal_amplitude * k) * math.sin(x_step * k * _counter * math.pi * 2)) * random.random()  for _counter in range(point_count)]
    
        elif signal_type == s_type_lfm:
            f0 = config[c_freq_min] # начальная частота
            f1 = config[c_freq_max] # конечная частота
            fd = signal_sampling   # частота дискретизации
            T = (signal_duration - hush_duration) / 1000 # время чистого сигнала (без тишины!) в секундах
            d = 1 / (fd * T) # шаг приращения

            y_raw = [signal_amplitude * math.cos(2 * math.pi * f0 / fd * n + d * math.pi * (f1 - f0) / fd * n**2) for n in range(point_count)]
            #  

        # применяем параметры раскачки и затухания и сохраняем конечный сигнал
        _y = []
        _y.extend([y_raw[_counter] * (_counter * fade_in_step) for _counter in range(fade_in_point_count)])
        _y.extend(y_raw[fade_in_point_count : point_count - fade_out_point_count])
        _y.extend([y_raw[point_count - _counter] * (_counter * fade_out_step) for _counter in range(fade_out_point_count, 0, -1)])

        # добавляем тишину в конце, если необходимо
        _y.extend(np.zeros(hush_count))

        # повторяем полученный сигнал заданное количество раз
        y = []
        for i in range(repeat_count):
            y.extend(_y)

        # добавляем паузу, если необходимо
        y.extend(np.zeros(pause_count))
    
        print('ok')
    

        # пишем в файл
        print('saving signal ...', end='')
        try:
            with open(file_name, 'wb') as f:
                arr = array.array('d')
                arr.fromlist(y)
                arr.tofile(f)
    
            print('ok')
            
        except Exception as E:
            raise Exception(E)
    

    except Exception as E:
        print('error in function generate(): %s' % E, file=sys.stderr)
        return None
    
    return arr


def meandr(config, **kwargs):
    try:
        signal_sampling = int(config[c_sampling])
        signal_duration = int(config[c_duration])
        signal_amplitude = int(config[c_amplitude])
        hush_duration = int(config[c_hush])
            
        #общее количество точек, которое будет обсчитано
        point_count = int(signal_sampling * (signal_duration - hush_duration) / 1000)

        meandr_pulse_width = get_cfg_param(config, c_meandr_pulse_width, 250, 'i') # config[]
        meandr_interval_width = get_cfg_param(config, c_meandr_interval_width, 0, 'i') # config[]
        meandr_type = get_cfg_param(config, c_meandr_type, m_one_channel, 'i') # config[]
        meandr_random_interval = get_cfg_param(config, c_meandr_random_interval, 0, 'i')

        ms = 0.000001 # 1 микросекунда

        # количество отсчетов (сэмплов) на один импульс
        # if meandr_type == m_one_channel or meandr_type == m_channels_iterleaved:
        #     n_imp = int(meandr_pulse_width * signal_sampling / 1000000)

        # else:
        #     n_imp = int(meandr_pulse_width * signal_sampling / 1000000) * 2

        n_imp = int(meandr_pulse_width * signal_sampling / 1000000)

        if meandr_pulse_width % (1000000 // signal_sampling) != 0:
            raise Exception('При заданной дискретизации длина импульса меандра должна быть кратна %i' % (1000000 // signal_sampling))



        # >> 1. случай, когда все интервалы равны
        if meandr_random_interval <= meandr_interval_width:

                                 
            # количество отсчетов (сэмплов) на один интервал
            n_int = int(meandr_interval_width * signal_sampling / 1000000)
            if meandr_interval_width % (1000000 // signal_sampling) != 0:
                raise Exception('При заданной дискретизации длина интервала между импульсами меандра должна быть кратна %i' % (1000000 // signal_sampling))

            # длина одного периода
            n = n_imp + n_int

            # выводим пердупреждение, если если в заданное количество точек не укладывается ровное количество периодов
            if point_count % n != 0:
                print('Предпреждение: количество периодов меандра не кратно длине сигнала')

            # print('sample_time=%f  pulse_time=%f  interval_time=%f  n_imp=%i  n_int=%i  n=%i  meandr_pulse_width=%i  meandr_interval_width=%i' % (sample_time, pulse_time, interval_time, n_imp, n_int, n, meandr_pulse_width, meandr_interval_width))

            # пустой массив
            y_raw = np.empty(point_count, dtype=float)


            # расставляем импульсы
            if meandr_type == m_one_channel:
                i = 0
                while i < point_count:
                    i = fill_meandr(y_raw, n_imp, i, point_count, signal_amplitude)
                    i = fill_meandr(y_raw, n_int, i, point_count, 0)
                      
    
            elif meandr_type == m_channels_alternate:
                i = 0
                while i < point_count:

                    i = fill_meandr(y_raw, n_imp, i, point_count, signal_amplitude)
                    i = fill_meandr(y_raw, n_imp, i, point_count, -signal_amplitude)
                    i = fill_meandr(y_raw, n_int, i, point_count, 0)

            else:
                i = 0
                while i < point_count:
                    i = fill_meandr(y_raw, n_imp, i, point_count, signal_amplitude)
                    i = fill_meandr(y_raw, n_int, i, point_count, 0)
                    i = fill_meandr(y_raw, n_imp, i, point_count, -signal_amplitude)
                    i = fill_meandr(y_raw, n_int, i, point_count, 0)

        # << 1

        # >> 2. иначе если необходимо расставить интервалы произвольной длины
        else:

            # длительность одного отсчета (сэмпла)
            sample_time = round(1.0 / signal_sampling, 9)

            # длительность одного импульса
            pulse_time = round(ms * meandr_pulse_width, 9)
            
            # длительность одного интервала
            interval_time = round(ms * meandr_interval_width, 9)

            # определяем минимальное и максимальное количество отсчетов (сэмплов) на один интервал
            n_int_min = int(meandr_interval_width * signal_sampling / 1000000)
            n_int_max = int(meandr_random_interval * signal_sampling / 1000000)
            
            # if meandr_interval_width % (1000000 // signal_sampling) != 0:
                # raise Exception('При заданной дискретизации длина интервала между импульсами меандра должна быть кратна %i' % (1000000 // signal_sampling))

            # пустой массив
            y_raw = np.empty(point_count, dtype=float)


            # расставляем импульсы
            if meandr_type == m_one_channel:
                i = 0
                while i < point_count:

                    i = fill_meandr(y_raw, n_imp, i, point_count, signal_amplitude)

                    # n_int_random = random.gammavariate(n_int_min) randrange(n_int_min, n_int_max)
                    # n_int_random = -1
                    # while n_int_random not in range(n_int_min, n_int_max):
                    #     rnd = random.expovariate(2)
                    #     n_int_random = n_int_min + int((n_int_max - n_int_min) * rnd)

                        # print('n_int_min=%i  rnd=%f  n/2=%f  n_int_random=%i' % (n_int_min, rnd, (n_int_max - n_int_min)/2, n_int_random))
                    

                    # n_int_random = random.randrange(n_int_min, n_int_max)
                    n_int_random = random.triangular(n_int_min, n_int_max, n_int_min)
                    i = fill_meandr(y_raw, n_int_random, i, point_count, 0)

                # print(y)
                        
    
            elif meandr_type == m_channels_alternate:
                i = 0
                while i < point_count:

                    i = fill_meandr(y_raw, n_imp, i, point_count, signal_amplitude)
                    i = fill_meandr(y_raw, n_imp, i, point_count, -signal_amplitude)

                    # n_int_random = random.randrange(n_int_min, n_int_max)
                    n_int_random = random.triangular(n_int_min, n_int_max, n_int_min)
                    i = fill_meandr(y_raw, n_int_random, i, point_count, 0)


            else:
                i = 0
                while i < point_count:

                    i = fill_meandr(y_raw, n_imp, i, point_count, signal_amplitude)
                    
                    # n_int_random = random.randrange(n_int_min, n_int_max)
                    # n_int_random = get_rnd(n_int_min, n_int_max)
                    n_int_random = random.triangular(n_int_min, n_int_max, n_int_min)
                    i = fill_meandr(y_raw, n_int_random, i, point_count, 0)
                    
                    i = fill_meandr(y_raw, n_imp, i, point_count, -signal_amplitude)

                    # n_int_random = random.randrange(n_int_min, n_int_max)
                    # n_int_random = get_rnd(n_int_min, n_int_max)
                    n_int_random = random.triangular(n_int_min, n_int_max, n_int_min)
                    i = fill_meandr(y_raw, n_int_random, i, point_count, 0)

        # << 2

        return y_raw

    except Exception as E:
        print('error in func _generator_main.meandr(): %s' % E, file=sys.stderr)
        return None
                

def fill_meandr(signal, interval_len, current_pos, point_count, val):
    j = 0
    while j < interval_len and current_pos < point_count:
        signal[current_pos] = val
        j += 1
        current_pos += 1

    return current_pos

def get_rnd(min_val, max_val):
    random_val = -1
    while random_val not in range(min_val, max_val):
        rnd = random.expovariate(4)
        random_val = min_val + int((max_val - min_val) * rnd)
    
    return random_val



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

    
