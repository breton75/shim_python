import math
import struct
import sys
import argparse
import matplotlib.pyplot as plt
import array
import random
import numpy as np

s_type_noise = 0
s_type_sinus = 1
s_type_meandr = 2
s_type_meandr_random = 3
s_type_sinus_noise = 4
s_type_sinus_sinus_noise = 5
# s_type_lfm = 6


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
    
def generate(**kwargs):
    try:

        print('generating signal ... ', end='')
        
        SIGNAL_TYPE = kwargs['t']
        SIGNAL_FREQUENCY = kwargs['f']
        SIGNAL_SAMPLING = kwargs['s']
        SIGNAL_DURATION = kwargs['d']
        SIGNAL_AMPLITUDE = kwargs['a']
        FADE_IN = kwargs['fi']
        FADE_OUT = kwargs['fo']
        FILE_NAME = kwargs['fn']

        hush_duration = kwargs['h']
        meandr_pulse_width = kwargs['mpw']
        meandr_pulse_interval = kwargs['mpi']
            
        #общее количество точек, которое будет обсчитано
        POINT_COUNT = int(SIGNAL_SAMPLING * (SIGNAL_DURATION - hush_duration) / 1000)
        hush_count = int(SIGNAL_SAMPLING * hush_duration / 1000)
    
        # количество точек на раскачку сигнала
        FADE_IN_POINT_COUNT = int(POINT_COUNT / 100 * FADE_IN) if FADE_IN > 0 else 0
        fade_in_step = 1 / FADE_IN_POINT_COUNT if FADE_IN > 0 else 0.0
    
        # количество точек на затухание сигнала    
        FADE_OUT_POINT_COUNT = int(POINT_COUNT / 100 * FADE_OUT) if FADE_OUT > 0 else 0
        fade_out_step = 1 / FADE_OUT_POINT_COUNT if FADE_OUT > 0 else 0.0
    
        # шаг приращения по оси x
        x_step = SIGNAL_FREQUENCY /  SIGNAL_SAMPLING
        
        # формируем сырой сигнал
        if SIGNAL_TYPE == s_type_noise:
            y_raw = [random.uniform(-SIGNAL_AMPLITUDE, SIGNAL_AMPLITUDE) for _counter in range(POINT_COUNT)]
            # y_raw = [random.uniform(0, SIGNAL_AMPLITUDE * 2) for _counter in range(POINT_COUNT)]
        
        elif SIGNAL_TYPE == s_type_sinus:
            # y_raw = [SIGNAL_AMPLITUDE * math.sin( x_step * _counter * math.pi * 2 + 0.5) for _counter in range(POINT_COUNT)]
            y_raw = [SIGNAL_AMPLITUDE * math.sin( x_step * _counter * math.pi * 2) for _counter in range(POINT_COUNT)]

        elif SIGNAL_TYPE == s_type_meandr:
            ms = 0.000001 # 1 микросекунда
            n = ms * float(meandr_pulse_width)

            print(meandr_pulse_width, n)
            mpc = 1 / SIGNAL_SAMPLING / n 

            raise Exception('error')
            # y_raw = [SIGNAL_AMPLITUDE * math.sin( x_step * _counter * math.pi * 2) for _counter in range(POINT_COUNT)]            
    
        elif SIGNAL_TYPE == s_type_sinus_noise:
            y_raw = [SIGNAL_AMPLITUDE * math.sin( x_step * _counter * math.pi * 2) * random.random()  for _counter in range(POINT_COUNT)]
    
        elif SIGNAL_TYPE == s_type_sinus_sinus_noise:  #
            k = 0.5
            y_raw = [(SIGNAL_AMPLITUDE * math.sin( x_step * _counter * math.pi * 2) + (SIGNAL_AMPLITUDE * k) * math.sin(x_step * k * _counter * math.pi * 2)) * random.random()  for _counter in range(POINT_COUNT)]
    
        # применяем параметры раскачки и затухания и сохраняем конечный сигнал
        y = []
        y.extend([y_raw[_counter] * (_counter * fade_in_step) for _counter in range(FADE_IN_POINT_COUNT)])
        y.extend(y_raw[FADE_IN_POINT_COUNT : POINT_COUNT - FADE_OUT_POINT_COUNT])
        y.extend([y_raw[POINT_COUNT - _counter] * (_counter * fade_out_step) for _counter in range(FADE_OUT_POINT_COUNT, 0, -1)])

        # добавляем тишину в конце, если необходимо
        # print(np.zeros(hush_count))
        y.extend(np.zeros(hush_count))
    
        print('ok')
    

        # пишем в файл
        print('saving signal ...', end='')
        try:
            f = open(FILE_NAME, 'wb')
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
        SIGNAL_TYPE = s_type_sinus_noise
        SIGNAL_FREQUENCY = 3000
        SIGNAL_SAMPLING = 16000 # должна быть минимум в 2 раза больше макс. частоты
        SIGNAL_DURATION = 100 # в миллисекундах
        SIGNAL_AMPLITUDE = 512 # величина отклонения от нуля
        HUSH = 0

        # раскачка и затухание сигнала в процентах от общей длины сигнала
        FADE_IN = 0
        FADE_OUT = 0
        
        # путь к файлу в который будет записан сигнал
        FILE_NAME = "d:/c++/AME/Generators/test_random.raw"
        
    else:

        # параметры сигнала
        SIGNAL_TYPE = parser.type
        SIGNAL_FREQUENCY = parser.frequency
        SIGNAL_SAMPLING = parser.sampling
        SIGNAL_DURATION = parser.duration # в миллисекундах
        SIGNAL_AMPLITUDE = parser.amplitude
        HUSH = parser.hash # тишина после сигнала мс.

        # раскачка и затухание сигнала в процентах от общей длины сигнала
        FADE_IN = parser.fade_in
        FADE_OUT = parser.fade_out

        # путь к файлу в который будет записан сигнал
        FILE_NAME = parser.file_name


    generate(t=SIGNAL_TYPE,
             s=SIGNAL_SAMPLING,
             f=SIGNAL_FREQUENCY,
             d=SIGNAL_DURATION,
             h=HUSH,
             a=SIGNAL_AMPLITUDE,
             fi=FADE_IN,
             fo=FADE_OUT,
             fn=FILE_NAME)

    
