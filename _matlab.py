# -*- coding: utf-8 -*-

import math
import struct
import sys
import array as arr
import numpy as np
from scipy import *
from scipy import signal
import _duty as duty
from _defs import *

from datetime import datetime, date, time
from time import struct_time as stm

def write_m_file(config, **kwargs):
    print('формируем m файл ... ', end='')

    try:

        m_file_name = get_path(config, 'm')  # путь к файлу в который будет производиться запись

        with open(m_file_name, 'w') as m:
            m.write("function f()\n")
            m.write("\n")
            m.write("%%%% %s\n" % (config[c_signal_name]))
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
            m.write("\t\n")
            m.write("\tday = '%i'; month = '%i'; year = '%i';\n" % (config[c_cur_time][2], config[c_cur_time][1], config[c_cur_time][0])) # https://docs.python.org/2/library/time.html#time.struct_time
            m.write("\t\n")
            m.write("\tpcm = [year '_' month '_' day ' ' '00' '_' '00' '_' '00' ' 2 6 48828.pcm'];\n")
            # m.write("\tlog = [year '_' month '_' day ' %i_%i_%i.log'];\n" % (config[c_cur_time][3], config[c_cur_time][4], config[c_cur_time][5]))
            m.write("\traw = '%s';\n" % (get_path(config, 'raw', only_filename=True)))
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
            m.write("\tfpcm=fopen(['%s' pcm], 'r');\n" % config[c_workdir])
            m.write("\t[RECEIVED_SIGNAL, received_cnt] = fread(fpcm, 'float');\n")
            m.write("\tfclose(fpcm);\n")
            m.write("\t\n")
            m.write("\tfraw=fopen(['%s' raw]);\n" % config[c_workdir])
            m.write("\t[SOURCE_SIGNAL, source_cnt] = fread(fraw, 'double');\n")
            m.write("\tfclose(fraw);\n")
    


            m.write("")
            m.write("")



            m.write('')



        print('успешно')

    except Exception as E:
        print('ошибка:\n\t%s' % E, file=sys.stderr)

