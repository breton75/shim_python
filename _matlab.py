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


def write_m_file(config, **kwargs):
    print('формируем m файл ... ', end='')

    try:

        m_file_name = get_path(config, 'm')  # путь к файлу в который будет производиться запись

        with open(m_file_name, 'w') as m:
            m.write("function f()\n")
            m.write("\n")
            m.write("%%%% %s, частота %i - %i Гц, дискретизация %i Гц\n" % (config[c_signal_name]))
            m.write("%%  частота %i - %i Гц, дискретизация %i Гц\n" % (config[c_freq0], config[c_freq1], config[c_sampling]))
            m.write("%%  сигнал-тишина: %i - %i, повторов %i, пауза %i мсек." % (config[c_duration] - config[c_hush], config[c_hush], config[c_repeat_count], config[c_pause]))
            m.write("%%  koeff = %f" % config[c_koeff])
            m.write("\n")
            m.write("%% ввод данных")
            m.write("\n")
            m.write("\tday = %i'; month = '%i'; year = '%i';" % ())
            m.write("\n")
            m.write("\tlog = '%s';" % get_path(config, ".raw"))
            m.write("\n")
            m.write("h = '00'; m = '00'; s = '00';")
            m.write("\tpcm = [year '_' month '_' day ' ' h '_' m '_' s ' 2 6 48828];")
            m.write("")
            m.write("")
            m.write("")
            m.write("")
            m.write("")
            m.write("")
            m.write("")
            m.write("")
            m.write("")
            m.write("")



            m.write('')



        print('успешно')

    except Exception as E:
        print('ошибка:\n\t%s' % E, file=sys.stderr)

