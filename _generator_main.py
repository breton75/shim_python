import math
import struct
import sys
import argparse
import matplotlib.pyplot as plt
import array
import random
import numpy as np

from scipy.fftpack import fft
from scipy.fftpack import ifft
import scipy

from _defs import *


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
        signal_frequency0 = int(config[c_freq0])
        signal_frequency1 = int(config[c_freq1])
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

            # meandr_pulse_width = kwargs['mpw']
            # meandr_pulse_interval = kwargs['mpi']
            
        #общее количество точек, которое будет обсчитано
        point_count = int(signal_sampling * (signal_duration - hush_duration) / 1000)
        hush_count = int(signal_sampling * hush_duration / 1000)
        pause_count = int(signal_sampling * pause / 1000)
    

        # шаг приращения по оси x
        x_step = signal_frequency0 / signal_sampling
        
        # формируем сырой сигнал
        if signal_type == s_type_noise:
            y_raw = [random.uniform(-signal_amplitude, signal_amplitude) for _counter in range(point_count)]
            y_raw = add_fading(config, y_raw)
            y_raw.extend(np.zeros(hush_count)) # добавляем тишину в конце, если необходимо
        
        elif signal_type == s_type_sinus:
            # y_raw = [signal_amplitude * math.sin( x_step * _counter * math.pi * 2 + 0.5) for _counter in range(point_count)]
            y_raw = [signal_amplitude * math.sin( x_step * _counter * math.pi * 2) for _counter in range(point_count)]
            y_raw = add_fading(config, y_raw)
            y_raw.extend(np.zeros(hush_count)) # добавляем тишину в конце, если необходимо


            print(fft(y_raw))

            # _y = fft(y_raw)
            # from matplotlib import pyplot
            # pyplot.subplot(111)
            # pyplot.plot(_y[:N].real)
            # pyplot.grid()
            # pyplot.show()


        elif signal_type == s_type_meandr:

            y_raw = meandr(config, **kwargs)
            
            if y_raw is None:
                raise Exception('не удалось сформировать сигнал')

            y_raw.extend(np.zeros(hush_count)) # добавляем тишину в конце, если необходимо

        elif signal_type == s_type_meandr_pack:
            interval0 = get_cfg_param(config, c_meandr_interval_width, 0, 'i') # config[]
            interval1 = get_cfg_param(config, c_meandr_random_interval, 0, 'i')
            config[c_meandr_random_interval] = 0
            istep = get_cfg_param(config, c_meandr_pack_step, 100, 'i')

            y_raw = []
            cnt = 0
            while interval0 <= interval1:
                config[c_meandr_interval_width] = interval0
                y_raw.extend(meandr(config, **kwargs))
                y_raw.extend(np.zeros(hush_count)) # добавляем тишину в конце, если необходимо
                cnt += 1
                interval0 += istep

            signal_duration *= cnt
            config[c_meandr_random_interval] = interval1

    
        elif signal_type == s_type_sinus_pack:  #
            y_raw, signal_duration = sinus_pack(config)

            if y_raw is None:
                raise Exception('не удалось сформировать сигнал')


        elif signal_type == s_type_sinus_sinus_noise:
            k = 0.5
            y_raw = [(signal_amplitude * math.sin( x_step * _counter * math.pi * 2) + (signal_amplitude * k) * math.sin(x_step * k * _counter * math.pi * 2)) * random.random()  for _counter in range(point_count)]
            y_raw = add_fading(config, y_raw)
            y_raw.extend(np.zeros(hush_count)) # добавляем тишину в конце, если необходимо
    
        elif signal_type == s_type_lfm:
            f0 = config[c_freq0] # начальная частота
            f1 = config[c_freq1] # конечная частота
            fd = signal_sampling   # частота дискретизации
            T = (signal_duration - hush_duration) / 1000 # время чистого сигнала (без тишины!) в секундах
            d = 1 / (fd * T) # шаг приращения

            y_raw = [signal_amplitude * math.cos(2 * math.pi * f0 / fd * n + d * math.pi * (f1 - f0) / fd * n**2) for n in range(point_count)]
            
            y_raw.extend(np.zeros(hush_count)) # добавляем тишину в конце, если необходимо

        elif signal_type == s_type_spectrum:
            f0 = config[c_freq0] # начальная частота
            f1 = config[c_freq1] # конечная частота
            fd = signal_sampling   # частота дискретизации
            clean_duration = (signal_duration - hush_duration) / 1000 # время чистого сигнала (без тишины!) в секундах

            # определяем количество точек сигнала
            N = int(fd * clean_duration) # 5000

            spectrum = np.empty(N, dtype=complex)
            for i in range(N):
                spectrum[i] = complex(0.0, 0.0)
            
            noise = [random.uniform(-signal_amplitude, signal_amplitude) for _counter in range(N)]
            spec_noise = fft(noise)

            _f0 = int(f0 * clean_duration)
            _f1 = int(f1 * clean_duration)
            
            fade_point_count = int(config[c_fadein])
            fade_step = 1 / fade_point_count if fade_point_count > 0 else 0.0
            
            _snap = [3000, 4000, 6000, 6500]
            snap = [s * clean_duration + c for c in range(10) for s in _snap]

            for i in np.arange(_f0, _f1):
                k = 1
            # >> трапеция
                # if i - _f0 < fade_point_count: k = fade_step * (i - _f0)
                # elif _f1 - i <= fade_point_count: k = fade_step * (_f1 - i)
                # else: k = 1
            # << трапеция

            # >> S-образное окно
                # if i - _f0 < fade_point_count: m = math.sin((-math.pi/2) + math.pi * ((fade_point_count - (fade_point_count - (i - _f0))) / fade_point_count))
                # elif _f1 - i <= fade_point_count: m = math.sin((-math.pi/2) + math.pi * ((fade_point_count - (fade_point_count - (_f1 - i))) / fade_point_count))
                # else: m = 1
                # k = (m + 1)/2
            # << S-образное окно

                # print(k)


                imag = random.uniform(-signal_amplitude * k, signal_amplitude * k) #  spec_noise[i].imag % signal_amplitude            
                ireal = (-1)**int(random.uniform(1,2)) * math.sqrt((signal_amplitude * k)**2 - imag**2)

                # imag = 0.0
                # ireal = signal_amplitude

                # print(ireal)
                if i not in snap:
                    spectrum[i] = complex(ireal, imag)
                    spectrum[-i] = complex(ireal, -imag)

            # for i in range(len(spectrum)):
            #     print(spectrum[i])

            
        # >> синусоида
            # spectrum = np.empty(190, dtype=complex)
            # spectrum[:] = complex(0.0, 0.0)

            # # spectrum[10] = complex(250.0, 0.0)
            # # spectrum[-10] = complex(250.0, 0.0)
            
            # for i in np.arange(10, 11):
            #     spectrum[i] = complex(1, 0)
            #     spectrum[-i] = complex(1, 0)

        # << синусоида

            _y = ifft(spectrum)
            # print('len _y=%i, type: %s of %s' % (len(_y), type(_y), type(_y[0])))

            # from matplotlib import pyplot
            # pyplot.subplot(111)
            # pyplot.plot(_y.real)
            # pyplot.grid()
            # pyplot.show()
            
            y_raw = array.array('d', _y.real) #.tolist()
            
            m1 = 0
            m2 = fade_point_count
            
            for i in np.arange(m1, m2):
                
                # if i < fade_point_count: k = 0.0 #fade_step * i
                # elif (len(y_raw) - i) <= fade_point_count: k = 0.0 #  fade_step * (len(y_raw) - i)
                # else: k = 1

                # print(k)
                m = math.sin((-math.pi/2) + math.pi * ((i - m1) / (m2 - m1)))
                # mm = math.sin((math.pi/2) + math.pi * ((i - m1) / (m2 - m1)))

                k = (m + 1)/2
                # kk = 1 - (mm + 1) / 2
                # print(kk)
                y_raw[i] *= 0.0
                y_raw[-i] *= 0.0

                # y_raw[i] = (-1)**(i%2) * 10 * k
                # y_raw[-i] = (-1)**(i%2) * 10 * k


            # y_raw = add_fading(config, y_raw)

            y_raw.extend(np.zeros(hush_count)) # добавляем тишину в конце, если необходимо
            
        
       
        # повторяем полученный сигнал заданное количество раз
        y = []
        for i in range(repeat_count):
            y.extend(y_raw)

        # добавляем паузу, если необходимо
        y.extend(np.zeros(pause_count))

        config[c_duration] = signal_duration * repeat_count + pause
    
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

        return list(y_raw)

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

def sinus_pack(config):
    try:
        # print('generator1: duration=%i' % config[c_duration])
    
        f0 = int(config[c_freq0])
        f1 = int(config[c_freq1])
        f_step = int(config[c_sinus_pack_step])
        sampling = int(config[c_sampling])
        signal_duration = int(config[c_duration])
        amplitude = int(config[c_amplitude])
        
        # fade_in = int(config[c_fadein])
        # fade_out = int(config[c_fadeout])
        # file_name = get_path(config, 'raw')
        
        hush_duration = int(config[c_hush])
        
        point_count = int(sampling * signal_duration / 1000)
        signal_count = int(sampling * (signal_duration - hush_duration) / 1000)
        hush_count = int(sampling * hush_duration / 1000)
    
        y_raw = []
        cnt = 0
        while f0 <= f1:
            x_step = f0 / sampling
            _y = [amplitude * math.sin( x_step * _counter * math.pi * 2) for _counter in range(signal_count)]
            _y = add_fading(config, _y)
            
            y_raw.extend(_y)
            y_raw.extend(np.zeros(hush_count))
            f0 += f_step
            cnt += 1
    
    
        signal_duration *= cnt
        # point_count *= cnt

        return y_raw, signal_duration

    except Exception as E:
        print('error in func _generator_main.sinus_pack(): %s' % E, file=sys.stderr)
        return None, None

def add_fading(config, y_raw):
    # применяем параметры раскачки и затухания
    signal_sampling = int(config[c_sampling])
    signal_duration = int(config[c_duration])
    fade_in = int(config[c_fadein])
    fade_out = int(config[c_fadeout])
    hush_duration = int(config[c_hush])

    if fade_in == 0 and fade_out == 0:
        return y_raw

    point_count = int(signal_sampling * (signal_duration - hush_duration) / 1000)
    # print('generator: duration=%i' % signal_duration)

    # количество точек на раскачку сигнала
    fade_in_point_count = int(point_count / 100 * fade_in) if fade_in > 0 else 0
    fade_in_step = 1 / fade_in_point_count if fade_in > 0 else 0.0
    
    # количество точек на затухание сигнала    
    fade_out_point_count = int(point_count / 100 * fade_out) if fade_out > 0 else 0
    fade_out_step = 1 / fade_out_point_count if fade_out > 0 else 0.0
    print('gen: point_count=%i  fade_in_point_count=%i  fade_out_point_count=%i' % (point_count, fade_in_point_count, fade_out_point_count))

    _y = []
    _y.extend([y_raw[_counter] * (_counter * fade_in_step) for _counter in range(fade_in_point_count)])
    _y.extend(y_raw[fade_in_point_count : point_count - fade_out_point_count])
    _y.extend([y_raw[point_count - _counter] * (_counter * fade_out_step) for _counter in range(fade_out_point_count, 0, -1)])
    
    return _y


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

    
