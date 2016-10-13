import math
import struct
import sys
import argparse
import matplotlib.pyplot as plt 
import array as arr
import numpy as np
from scipy import *
from scipy import signal
import _shim_main as shim

def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-shim', '--shim_file_name', type=str, required=False)
    parser.add_argument('-p1', '--from_point', type=int, required=False)
    parser.add_argument('-p2', '--to_point', type=int, required=False)

    namespace = parser.parse_args(sys.argv[1:])
    
    if (namespace.shim_file_name == None or
        namespace.from_point == None or namespace.to_point == None):

        return None
    
    else:
        return namespace


def plot_shim(**kwargs):

    print('Start shim plotting')

    SHIM_FILE_NAME = kwargs['shim'] # путь к файлу шим
    P1 = kwargs['p1'] # начальная точка
    P2 = kwargs['p2'] # конечная точка

    SHIM_WIDTH = 10
    SHIM_HEIGHT = 80
    
    # читаем файл c шим
    try:

        fshim = open(SHIM_FILE_NAME, 'rb')

        # читаем заголовок файла
        header = struct.unpack(shim.HEADER_PACK, fshim.read(struct.calcsize(shim.HEADER_PACK)))

        sampling = int(header[shim.HEADER_PACK_KEYS.index('signal_sampling')])
        duration = int(header[shim.HEADER_PACK_KEYS.index('signal_duration')])
        sawpp = int(header[shim.HEADER_PACK_KEYS.index('saw_count_per_point')])
        ch_count = int(header[shim.HEADER_PACK_KEYS.index('shim_channel_count')])
        R = float(header[shim.HEADER_PACK_KEYS.index('shim_R')])
    
        point_count = int(sampling * duration / 1000)
        shim_count = point_count * sawpp * 4
        
        # читаем значения
        ashim = arr.array('H')
        fshim.seek(struct.calcsize(shim.HEADER_PACK))

        ashim.fromfile(fshim, shim_count)

        if shim_count != len(ashim):
            raise ValueError()
            
        fshim.close()
    
    except (OSError) as msg:
        print(msg, file=sys.stderr)
        return False
    
    except (ValueError, EOFError):
        print('Ошибка чтения данных. Ожидалось значений: %i, получено: %i' % (shim_count, len(ashim)), file=sys.stderr)
        fshim.close()
        return False
    
##    shim_len = max(ashim)
    
    print(sampling, duration, sawpp, ch_count, R, r, point_count, shim_count, len(ashim))


    if (P1 == None) or (P1 not in range(len(ashim) // 4)): P1 = 0
    if (P2 == None) or (P2 not in range(P1, len(ashim) // 4)): P2 = len(ashim) // 4

    lefts_a = []
    widths_a = []
    heights_a = []
    bottoms_a = []

    lefts_b = []
    widths_b = []
    heights_b = []
    bottoms_b = []

    step = 4 * sawpp
    for i in range(P1, P2):

        _xa = ashim[i * step]
        x_b = ashim[i * step + 1]
        x_a = ashim[i * step + 2]
        _xb = ashim[i * step + 3]

        # канал a
        k1 = x_a / R
        k2 = 1 - k1

        w = SHIM_WIDTH * k1

        if w: # нулевые значения не добавляем (не отрисовываем)
            lefts_a.append((i - P1) * SHIM_WIDTH + SHIM_WIDTH * k2 / 2)
            widths_a.append(w)

        # если используется два канала, то считаем и для канала b
        if ch_count == 2:
            k1 = x_b / R
            k2 = 1 - k1

            w = SHIM_WIDTH * k1

            if w: # нулевые значения не добавляем (не отрисовываем)
                lefts_b.append((i - P1) * SHIM_WIDTH + SHIM_WIDTH * k2 / 2)
                widths_b.append(w)
        

        
    for i in range(len(lefts_a)):
        heights_a.append(SHIM_HEIGHT)
        bottoms_a.append(0)
      
        
    for i in range(len(lefts_b)):
        heights_b.append(SHIM_HEIGHT)
        bottoms_b.append(-SHIM_HEIGHT)


    plt.subplot(411)
    plt.bar(left=lefts_a, width=widths_a, height=heights_a, bottom=bottoms_a, color='g', edgecolor='g')
    plt.bar(left=lefts_b, width=widths_b, height=heights_b, bottom=bottoms_b, color='r', edgecolor='r')
    plt.ylim(ymin=-100, ymax=100)
    plt.xticks(arange(0, (P2 - P1) * SHIM_WIDTH, SHIM_WIDTH * 50), arange(P1, P2, 50))
    plt.grid()

    plt.show()


    
    # рисуем сигнал
##    plt.subplot(411)
##    plt.plot(araw[POINT_1:POINT_2], label='Raw signal')
##    plt.grid()
##
##    plt.subplot(412)
##    plt.plot(arawf[POINT_1:POINT_2], label='Filtered signal')
##    plt.grid()
##
##    plt.subplot(413)
##    f, Pwelch_spec = signal.welch(araw, SIGNAL_SAMPLING, scaling='spectrum', nperseg=1024)
##    plt.semilogy(f, Pwelch_spec)
##    plt.grid()
##    
##    plt.subplot(414)
##    f, Pwelch_spec = signal.welch(arawf, SIGNAL_SAMPLING, scaling='spectrum', nperseg=1024)
##    plt.semilogy(f, Pwelch_spec)
##    plt.grid()
##    
##    plt.show()

    print('Shim plotting finished')


#####################################################################  

if __name__ == "__main__":

    parser = createParser()

    if parser == None:

        # путь к файлу шим
        SHIM_FILE_NAME = "D:/c++/AME/Generators/test_main.shim"
        POINT_1 = 113 # начальная точка
        POINT_2 = 800 # конечная точка
        
    else:
        SHIM_FILE_NAME = parser.raw_file_name # путь к файлу шим
        POINT_1 = parser.from_point # начальная точка
        POINT_2 = parser.to_point # конечная точка

    plot_shim(shim=SHIM_FILE_NAME,
              p1=POINT_1,
              p2=POINT_2)
    
