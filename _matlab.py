# -*- coding: utf-8 -*-

import math
import struct
import sys
import os
import array as arr
import numpy as np
from scipy import *
from scipy import signal
import _duty as duty
from _defs import *

from datetime import datetime, date, time
import time

def write_m_file(config, **kwargs):
    print('формируем m файл ... ', end='')

    try:

        m_file_name = get_path(config, 'm')  # путь к файлу в который будет производиться запись

        with open(m_file_name, 'w') as m:
            m.write("function f()\n")
            m.write("\n")
            m.write("%%%% %s\n" % (config[c_signal_name].upper()))
            m.write("%%  частота %i - %i Гц, дискретизация %i Гц\n" % (config[c_freq0], config[c_freq1], config[c_sampling]))
            m.write("%%  сигнал-тишина: %i - %i, повторов %i, пауза %i мсек.\n" % (config[c_duration] - config[c_hush], config[c_hush], config[c_repeat_count], config[c_pause]))
            m.write("%%  koeff = %0.2f\n" % config[c_koeff])
            m.write("%  \n")
            m.write("%  \n")
            m.write("\n")

            m.write("%% ввод данных\n")
            m.write("\t\n")
            m.write("\tfds = %i; %% частота дискретизации исходного сигнала\n" % config[c_sampling])
            m.write("\tfdr = 48828;  % частота дискретизации микрофона\n")
            # m.write("\t\n")
            # m.write("\tday = '%i'; month = '%i'; year = '%i';\n" % (config[c_cur_time][2], config[c_cur_time][1], config[c_cur_time][0])) # https://docs.python.org/2/library/time.html#time.struct_time
            m.write("\t\n")
            m.write("\tpcm = ['%s ' '00' '_' '00' '_' '00' ' 2 6 ' int2str(fdr) '.pcm'];\n" % (time.strftime(c_date_format, config[c_cur_time])))

            # print('path1', get_folder_name(config, 'raw'), '\npath2', get_folder_name(config, 'm'), '\npath3', os.path.relpath(get_folder_name(config, 'raw'), get_folder_name(config, 'm')))

            m.write("\traw = '%s';\n" % get_path(config, 'raw', only_filename=True))
            m.write("\t\n")
            m.write("\tstep = 24000;\n")
            m.write("\tp0 = 1;\n")
            m.write("\tp1 = p0 + step;\n")
            m.write("\tp2 = p1 + step;\n")
            m.write("\t\n")
            m.write("\tttl = '%s, %i - %i Гц'; %% заголовок легенды\n" % (config[c_signal_name], config[c_freq0], config[c_freq1]))
            
            s = ""
            for i in range(config[c_repeat_count]):
                if config[c_hush] == 0: s += "%i - " % config[c_duration]
                else: s += "%i-%i - " % (config[c_duration] - config[c_hush], config[c_hush])

            m.write("\tlgnd = '%s%i мсек., koeff = %0.2f'; %% текст легенды\n" % (s, config[c_pause], config[c_koeff]))
            m.write("\t\n")
            m.write("\tscrsz = get(groot,'ScreenSize');\n")
            m.write("\t\n")
            m.write("%% открываем файлы\n")
            m.write("\t\n")
            
            p = os.path.relpath(get_folder_name(config, 'pcm'), get_folder_name(config, 'm')).replace("\u005c", "/")
            if p[-1] != '/': p += '/'
            m.write("\tf=fopen(['%s' pcm], 'r');\n" % p)
            m.write("\t[RECEIVED_SIGNAL, received_cnt] = fread(f, 'float');\n")
            m.write("\tfclose(f);\n")
            m.write("\t\n")

            p = os.path.relpath(get_folder_name(config, 'raw'), get_folder_name(config, 'm')).replace("\u005c", "/")
            if p[-1] != '/': p += '/'
            m.write("\tf=fopen(['%s' raw]);\n" % p)
            m.write("\t[SOURCE_SIGNAL, source_cnt] = fread(f, 'double');\n")
            m.write("\tfclose(f);\n")
            m.write("\t\n")

            m.write("%% рисуем полученный сигнал и его спектр\n")
            m.write("\tfigure('Name', ['Принятый сигнал ' pcm], 'NumberTitle', 'off', 'Position',[10 scrsz(4)/2 - 35 scrsz(3)/2 - 50 scrsz(4)/2 - 50]);\n")
            m.write("\tplot(RECEIVED_SIGNAL);\n")
            m.write("\t\n")
            m.write("\tlg = legend(lgnd);\n")
            m.write("\ttitle(lg, ttl);\n")
            m.write("\t\n")
            m.write("\tfigure('Name',['Спектр принятого сигнала ' pcm],'NumberTitle','off','Position',[scrsz(3)/2 + 20 scrsz(4)/2 - 35 scrsz(3)/2 - 50 scrsz(4)/2 - 50]);\n")
            m.write("\t\n")
            m.write("\tRECEIVED_SPECTRUM1 = abs(fft(RECEIVED_SIGNAL(p0:p1)));\n")
            m.write("\tRECEIVED_SPECTRUM2 = abs(fft(RECEIVED_SIGNAL(p1:p2)));\n")
            m.write("\t\n")
            m.write("\tslen = (length(RECEIVED_SPECTRUM1) - 1) / 2;\n")
            m.write("\tx = 0:fdr/2/slen:(fdr/2 - fdr/2/slen); % шкала частот\n")
            m.write("\t\n")
            m.write("\tstem(x, RECEIVED_SPECTRUM1(1:slen), 'Marker', 'none');\n")
            m.write("\thold on\n")
            m.write("\tstem(x, RECEIVED_SPECTRUM2(1:slen), 'Marker', 'none');\n")
            m.write("\t\n")
            m.write("\tlg = legend(lgnd);\n")
            m.write("\ttitle(lg, ttl);\n")
            m.write("\t\n")
            m.write("%% рисуем исходный сигнал и его спектр\n")
            m.write("\tfigure('Name',['Исходный сигнал ' raw],'NumberTitle','off','Position',[10 20 scrsz(3)/2 - 50 scrsz(4)/2 - 140]);\n")
            m.write("\tplot(SOURCE_SIGNAL);\n")
            m.write("\t\n")
            m.write("\tlg = legend(lgnd);\n")
            m.write("\ttitle(lg, ttl);\n")
            m.write("\t\n")
            m.write("\tSOURCE_SPECTRUM = abs(fft(SOURCE_SIGNAL));\n")
            m.write("\tfigure('Name',['Спектр исходного сигнала ' raw],'NumberTitle','off','Position',[scrsz(3)/2 + 20 20 scrsz(3)/2 - 50 scrsz(4)/2 - 140]);\n")
            m.write("\t\n")
            m.write("\tslen = (length(SOURCE_SPECTRUM) - 1) / 2;\n")
            m.write("\tx = 0:fds/2/slen:(fds/2 - fds/2/slen); % шкала частот\n")
            m.write("\tstem(x, SOURCE_SPECTRUM(1:slen), 'Marker', 'none');\n")
            m.write("\t\n")
            m.write("\tlg = legend(lgnd);\n")
            m.write("\ttitle(lg, ttl);\n")
            m.write("\t\n")
            m.write("end\n")
            # m.write("\t\n")


        print('ok')

    except Exception as E:
        print('ошибка:\n\t%s' % E, file=sys.stderr)

