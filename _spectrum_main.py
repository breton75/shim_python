import math
import struct
import sys
import argparse
import matplotlib.pyplot as plt
import array as arr
import numpy as np
from scipy import *
from scipy import signal
import _duty as duty
from scipy.fftpack import fft

from _defs import *

from matplotlib import rc # для отображения русского шрифта
if 'win' in sys.platform: 
    rc('font', family='Verdana')
else:
    rc('font', family='Ubuntu')

from matplotlib.colors import colorConverter
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from matplotlib.artist import Artist
from matplotlib.mlab import dist_point_to_segment
from matplotlib.text import Text

HEADER_STRUCT = '16sIIII' # заголовок, версия, кол-во точек # fmin, fmax
FILE_DESIGNATION = b'SPECTRUM FORM   '
FILE_VER = 0x00000001 # 0.0.0.2
CONTROL_COUNT = 41

class PolygonInteractor(object):
    """
    An polygon editor.

    Key-bindings

      't' toggle vertex markers on and off.  When vertex markers are on,
          you can move them, delete them

      'd' delete the vertex under point

      'i' insert a vertex at point.  You must be within epsilon of the
          line connecting two existing vertices

    """

    showverts = True
    epsilon = 5  # max pixel distance to count as a vertex hit
    x_const = 0

    def __init__(self, ax, poly, file_name, fmin, fmax): #, aspec
        if poly.figure is None:
            raise RuntimeError('You must first add the polygon to a figure or canvas before defining the interactor')
        self.ax = ax
        canvas = poly.figure.canvas
        self.poly = poly

        self.text = Text(x=0, y=0, text='', color='b')
        self.text.set_horizontalalignment('center')
        self.text.set_weight('bold')
        self.text.set_clip_on(False)
        self.text.set_bbox(dict(facecolor='yellow', alpha=0.5))
        self.ax.add_artist(self.text)

        self.file_name = file_name
        self.fmin = fmin
        self.fmax = fmax
        # self.aspec = aspec[fmin:fmax]
        self.maxY = 100 # float(max(self.aspec))
        self.xstep = get_xstep(fmax - fmin, len(poly.xy) - 2)

        x, y = zip(*self.poly.xy)
        
        self.line = Line2D(x, y, marker='s', markerfacecolor='r', markersize=10, animated=True, drawstyle='steps-mid', color='black', lw=0)
        self.ax.add_line(self.line)
        
        #self._update_line(poly)

        cid = self.poly.add_callback(self.poly_changed)
        self._ind = None  # the active vert

        canvas.mpl_connect('draw_event', self.draw_callback)
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('key_press_event', self.key_press_callback)
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas = canvas

    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.ax.draw_artist(self.text)
        self.canvas.blit(self.ax.bbox)

    def poly_changed(self, poly):
        'this method is called whenever the polygon object is called'
        # only copy the artist props to the line (except visibility)
        vis = self.line.get_visible()
        Artist.update_from(self.line, poly)
        self.line.set_visible(vis)  # don't use the poly visibility state

    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'

        # display coords
        xy = np.asarray(self.poly.xy)
        xyt = self.poly.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt - event.x)**2 + (yt - event.y)**2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]

        if d[ind] >= self.epsilon:
            ind = None

        return ind

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if not self.showverts:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        self._ind = self.get_ind_under_point(event)
        self.x_const = self.poly.xy[self._ind][0]

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if not self.showverts:
            return
        if event.button != 1:
            return
        self._ind = None

    def key_press_callback(self, event):
        'whenever a key is pressed'
        # if not event.inaxes:
        #     return

        if event.inaxes:
            if event.key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-']:
                ind = self.get_ind_under_point(event)
                if not (ind is None or ind == 0 or ind == len(self.poly.xy) - 1):
                    if event.key == '-': val = 1
                    else: val = int(event.key) / 10
                    self.poly.xy[ind][1] = self.maxY * val
                    self.line.set_data(zip(*self.poly.xy))

        if event.key == 'ctrl+w':
            print('saving specrtum form... ', end='')

            x, y = zip(*self.poly.xy)

            try:
                f = open(self.file_name, 'wb')

            except (OSError) as msg:
                print(msg, file=sys.stderr)
                return None
            # print('%d  %d' % (max(x), float(max(y))))

            # при сохранении отбрасываем две точки - первую и последнюю, тк они имеют только декоративную функцию
            f.write(struct.pack(HEADER_STRUCT, FILE_DESIGNATION, FILE_VER, len(x) - 2, self.fmin, self.fmax)) 

            for i in range(1, len(x) - 1, 1):
                f.write(struct.pack('d', float(y[i])))

            f.close()
            print('ok')

        if event.key == 'ctrl+r':
            x, y = zip(*self.poly.xy)

            # fpcnt =  # len(self.aspec) # int(self.sampling / 2)
            controls_count = len(x)
            step = get_xstep(self.fmax - self.fmin, controls_count - 2) #  fpcnt / (controls_count - 3)

            # print('fpcnt=%i  controls_count=%i  step=%d' % (fpcnt,controls_count,step))
            self.poly.xy[0][0] = self.fmin #0
            self.poly.xy[-1][0] = self.fmax # fpcnt

            maxY = 100 # max(self.aspec)
            for i in range(1, controls_count - 1):
                self.poly.xy[i][0] = self.fmin + (i - 1) * step
                self.poly.xy[i][1] = maxY
                # print('x=%i  y=%f' % (self.poly.xy[i][0], self.poly.xy[i][1]))
            
            self.line.set_data(zip(*self.poly.xy))


        if event.key in ['ctrl+u', 'ctrl+d']:
            x, y = zip(*self.poly.xy)

            controls_count = len(x)
            step = get_xstep(self.fmax - self.fmin, controls_count - 2) #  fpcnt / (controls_count - 3)

            # print('fpcnt=%i  controls_count=%i  step=%d' % (fpcnt,controls_count,step))
            self.poly.xy[0][0] = self.fmin #0
            self.poly.xy[-1][0] = self.fmax # fpcnt

            maxY = 100 # max(self.aspec)
            stepY = maxY / (controls_count - 3)
            for i in range(1, controls_count - 1):
                self.poly.xy[i][0] = self.fmin + (i - 1) * step
                
                if event.key == 'ctrl+u':
                    self.poly.xy[i][1] = i * stepY
                elif event.key == 'ctrl+d':
                    self.poly.xy[i][1] = maxY - i * stepY
            
            self.line.set_data(zip(*self.poly.xy))


        if event.key == 't':
            self.showverts = not self.showverts
            self.line.set_visible(self.showverts)
            if not self.showverts:
                self._ind = None
        elif event.key == 'd':
            ind = self.get_ind_under_point(event)
            if ind is not None:
                self.poly.xy = [tup for i, tup in enumerate(self.poly.xy) if i != ind]
                self.line.set_data(zip(*self.poly.xy))
        elif event.key == 'i':
            xys = self.poly.get_transform().transform(self.poly.xy)
            p = event.x, event.y  # display coords
            for i in range(len(xys) - 1):
                s0 = xys[i]
                s1 = xys[i + 1]
                d = dist_point_to_segment(p, s0, s1)
                if d <= self.epsilon:
                    self.poly.xy = np.array(
                        list(self.poly.xy[:i]) +
                        [(event.xdata, event.ydata)] +
                        list(self.poly.xy[i:]))
                    self.line.set_data(zip(*self.poly.xy))
                    break

        self.canvas.draw()

    def motion_notify_callback(self, event):
        'on mouse movement'
        if not self.showverts:
            return


        if self._ind is None:
            ind = self.get_ind_under_point(event)
            if not (ind is None or event.ydata is None):
                self.text.set_text('%i Гц' % int(self.poly.xy[ind][0]))
                self.text.set_position([self.poly.xy[ind][0], event.ydata + 1])
                self.update()

            return

        if self._ind == 0 or self._ind == len(self.poly.xy) - 1:
            return
        
        if event.inaxes is None:
            return

            
        if event.button != 1:
            return

        y = event.ydata
        self.poly.xy[self._ind] = self.x_const, y
        
        self.line.set_data(zip(*self.poly.xy))

        self.update()


    def update(self):
        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.ax.draw_artist(self.text)
        self.canvas.blit(self.ax.bbox)
        
def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-raw', '--raw_file_name', type=str, required=False)
    parser.add_argument('-rawf', '--rawf_file_name', type=str, required=False)
    parser.add_argument('-sffn', '--spectrum_form_file_name', type=str, required=False)
    parser.add_argument('-s', '--sampling', type=int, required=False)
    parser.add_argument('-d', '--duration', type=int, required=False)

    namespace = parser.parse_args(sys.argv[1:])

    if namespace.raw_file_name is None or namespace.rawf_file_name is None or \
       namespace.spectrum_form_file_name is None or namespace.sampling is None or \
       namespace.duration is None:
        return None

    else:
        return namespace

def signal2spectrum(config, **kwargs):
    try:
        # print('Start signal to spectrum converting')

        araw = None
        spectrum = None
        aspec = None

        sampling = config[c_sampling]
        duration = config[c_duration]

        point_count = int(sampling * duration / 1000)
        fsdpcnt = int((sampling / 2) * (duration / 1000)) # point_count / 2
        fpcnt = int(sampling / 2)
        
        # print('s=%i  d=%i  pcnt=%i  fsdpcnt=%i' % (sampling, duration, point_count, fsdpcnt))
        # print(kwargs)

        # сигнал должен быть передан как массив
        if 'signal_data' in kwargs:
            araw = kwargs['signal_data']

            # print('araw=%i' % len(araw))

        else: # иначе читаем исходный файл
            try:
                raw = get_path(config, 'raw')

                with open(raw, 'rb') as f:
                        araw = arr.array('d')
                        araw.fromfile(f, point_count)
                
            except Exception as E:
                print(E, sys.stderr)

        if araw is None:
            raise Exception('signal data is not specified')

        # преобразование фурье
        spectrum = fft(araw) # / fsdpcnt * 2

        # формируем массив с уровнями сигнала по частотам
        aspec = np.empty(fpcnt, dtype=float)
        j = 0
        for i in range(fsdpcnt):
            k = int(i / fsdpcnt * fpcnt) + 1
            aspec[j:k] = abs(spectrum[i] / fsdpcnt * 2)
            j = k
            # pp = abs(spectrum[i].real) / fsdpcnt * 2
            # if i < 10: print('i={0}  pp={1}  pp.type={2}  spectrum={3}  type={4}  real={5}  type={6}'.format(i, pp, type(pp), spectrum[i], type(spectrum[i]), spectrum[i].real, type(spectrum[i].real)))

        # aspec = arr.array('d', abs(spectrum[:fpcnt].real)) #abs(spectrum[:fpcnt].real / fpcnt * 2))
        # print('j=%i  k=%i aspec[k]={}'.format(aspec[999:k]) % (j, k))

        # print('Signal to spectrum converting finished successfully')

    except Exception as E:
        print('error in func signal2spectrum(): %s' % E, file=sys.stderr)

    finally:
        # ВНИМАНИЕ.
        # spectrum содержит результат преобразования фурье без изменений, без учета длительности и дискретизации сигнала.
        # aspec содержит уровни частот, пересчитанных с учетом длительности и дискретизации сигнала. для отображения на графике и редактирования формы спектра
        return spectrum, aspec, araw

def read_spectrum_form_file(config, **kwargs):
    
    ver = None
    controls_count = None
    controls = None
    minX = None
    maxX = None

    try:

        spectrum_form_file_name = get_path(config, 'spectrum')

        header = duty.read_header(spectrum_form_file_name, HEADER_STRUCT)
        
        if header is None:
            raise Exception('wrog spectrum form file header')

        if header[0] != FILE_DESIGNATION:
            raise Exception('wrog spectrum form file header')

        ver = header[1]
        controls_count = header[2]
        minX = header[3]
        maxX = header[4]

        controls = duty.read_file(spectrum_form_file_name, 'd', struct.calcsize(HEADER_STRUCT), controls_count)

    except Exception as E:
        print('error in function read_spectrum_form_file(): ', file=sys.stderr, end='')
        print(E, file=sys.stderr)
        # return None, No

    finally:
        return ver, controls_count, controls, minX, maxX

def get_xstep(spectrum_len, controls_count):

    return spectrum_len / (controls_count - 1)

def get_xs_ys(fmin, fmax, controls_count):
    try:
        xstep = get_xstep(fmax - fmin, controls_count)
        
        xs = None
        ys = None

        # добавляем две точки в начало и конец, для декоративных целей
        xs = np.empty(controls_count + 2, dtype=float)
        xs[0] = fmin
        xs[-1] = fmax
        for i in range(1, controls_count + 1, 1): xs[i] = fmin + (i - 1) * xstep

        ys = np.empty(controls_count + 2, dtype=float)
        ys[0] = 0
        ys[-1] = 0

    except Exception as E:
        print('error in function get_xs_ys(): ', file=sys.stderr, end='')
        print(E, file=sys.stderr)

    return xs, ys


def edit_spectrum(config, **kwargs):

    try:
        sampling = config[c_sampling] # дискретизация
        duration = config[c_duration]

        # задаем границы массива диапазон частот [fmin:fmax]
        fmin = 1
        fmax = int(sampling / 2)
        if c_filter_freq_min in config and config[c_filter_freq_min] in range(fmin, fmax): fmin = config[c_filter_freq_min]
        if c_filter_freq_max in config and config[c_filter_freq_max] in range(fmin, fmax): fmax = config[c_filter_freq_max]

        spectrumMax = 100 # в процентах %

        spectrum_form_file_name = get_path(config, 'spectrum')

    ###############################################

        ver, controls_count, controls, minX, maxX = read_spectrum_form_file(config, **kwargs)

        # если не удалось прочитать сохраненную форму спектра, то создаем новую
        if controls_count is None:
            controls_count = CONTROL_COUNT
            minX = fmin
            maxX = fmax
        
        # получаем два массива с координатами регуляторов
        xs, ys = get_xs_ys(minX, maxX, controls_count)
            
        # если создаем новую форму спектра, то значения у всех регуляторов равно 100%
        if controls is None:
            ys[1:-1] = spectrumMax

        else:
            for i in range(1, controls_count + 1, 1):
                ys[i] = controls[i - 1]


        # создаем графические элементы
        fig, ax = plt.subplots()
        plt.vlines(xs, 0, ys, label=' ', color='b', lw=3)
        plt.legend(title='Редактор формы спектра\nctrl + r - сброс\nctrl + w - сохранить и выйти\n0..9 - установить уровень регулятора', loc='upper left', shadow=True, frameon=True, fontsize='small')
        plt.axis([fmin, fmax, 0, spectrumMax * 1.5])
        plt.xticks(arange(fmin, fmax, int(get_xstep(fmax - fmin, controls_count)) * 2)) #, arange(0, len(aspec), get_xstep(len(aspec), controls_count) * 4))
        
        poly = Polygon(list(zip(xs, ys)), animated=True, closed=False, color=colorConverter.to_rgba('b', 0.250), visible=True)
        ax.add_patch(poly)
        p = PolygonInteractor(ax, poly, spectrum_form_file_name, minX, maxX) # , aspec
        
        plt.autumn()
        plt.grid()
        plt.show()
        
        return True

    except Exception as E:
        print('error in function edit_spectrum(): ', file=sys.stderr, end='')
        print(E, file=sys.stderr)
        return None


def apply_spectrum(config, **kwargs):
    
    aflt = None
    
    try:
        
        sampling = config[c_sampling] # дискретизация
        duration = config[c_duration] # длительность сигнала
        print(sampling, duration)
        # преобразуем заданный сигнал в спектр
        spectrum, aspec, araw = signal2spectrum(config, **kwargs)

        if spectrum is None or araw is None:
            raise Exception('converting to spectrum error')

        # границы частот спектра определяют диапазон наложения формы спектра
        # для применения полосового фильтра, отсекаем все, что не входит в [fmin:fmax]
        fmin = 1
        fmax = len(aspec)
        if c_filter_freq_min in config and config[c_filter_freq_min] in range(fmin, fmax): fmin = config[c_filter_freq_min]
        if c_filter_freq_max in config and config[c_filter_freq_max] in range(fmin, fmax): fmax = config[c_filter_freq_max]

        # значения для вычислений
        # point_count = int(sampling * duration / 1000)
        fsdpcnt = int((sampling / 2) * (duration / 1000)) # количество точек спектра исходя из длительности и дискретизации
        fpcnt = int(sampling / 2) # реальное количество точек спектра
        fmin_n = int(fmin * fsdpcnt / fpcnt) # реальные границы диапазона частот 
        fmax_n = int(fmax * fsdpcnt / fpcnt)


        # максимальное значение спектра в заданной области частот
        spectrumMax = max(aspec[fmin:fmax])

        # ЕСЛИ ЗАДАНА ФОРМА СПЕКТРА, ТО НАКЛАДЫВАЕМ ЕЕ НА СПЕКТР
        # * начало 1 *
        if c_apply_spectrum_form in config and config[c_apply_spectrum_form] == True: 
            
            print('appling spectrum form ...', end='')

            spectrum_form_file_name = get_path(config, 'spectrum')

            # читаем файл с сохраненной формой спектра
            ver, controls_count, controls, minX, maxX = read_spectrum_form_file(config, **kwargs)

            # если диапазон частот форма спектра не соответствует заданным параметрам fmin и fmax, то выходим с ошибкой
            # if not (fmin == minX and fmax == maxX):
            #     raise Exception('полоса частот формы спектра (%i - %i) не соответствует заданным параметрам (%i - %i)' % (minX, maxX, fmin, fmax))
                # raise Exception('frequency band of spectrum form (%i - %i) does not match to given params (%i - %i)' % (minX, maxX, fmin, fmax))
    
            # если не удалось прочитать сохраненную форму спектра, то выходим с ошибкой
            if controls_count is None or controls is None:
                raise Exception('error on reading spectrum form')

            minX_n = int(minX * fsdpcnt / fpcnt) # реальные границы формы спектра 
            maxX_n = int(maxX * fsdpcnt / fpcnt)
            # print('minX_n={}  maxX_n={}'.format(minX_n,maxX_n))

            xstep = get_xstep(maxX_n - minX_n, controls_count)
            x = minX_n
            x1 = minX_n
            y1 = controls[0]
            
            maxY_pos = max(spectrum[minX_n:maxX_n].real) # макс. положительное значение спектра в заданной полосе
            minY_neg = min(spectrum[minX_n:maxX_n].real) # мин.  отрицательное значение спектра в заданной полосе
            
            if maxY_pos > abs(minY_neg): maxYreal = maxY_pos
            else: maxYreal = abs(minY_neg)
            # print('maxY_pos = {}  maxY_neg={}'.format(maxY_pos, minY_neg))

            for i in range(1, controls_count, 1):
                x2 = minX_n + i * xstep
                y2 = controls[i]
    
                # проходим по всем точкам между x1 и x2
                while x < x2:
        
                    # находим значение (у) точки пересечения вертикальной прямой в точке x и прямой (x1,y1)-(x2,y2)
                    # уравнение прямой (х1,у1)-(х2,у2):  (x - x1)/(x2 - x1) = (y - y1)/(y2 - y1), отсюда
                    # y = (x - x1)/(x2 - x1) * (y2 - y1) + y1. получим:
    
                    y = ((x - x1) / (x2 - x1) * (y2 - y1) + y1) / 100.0

                    # если необходимо привести спектр, точно к заданной форме, то
                    # в зависимости от уровня сигнала >0 или <0, задаем уровень спектра в данной точке равным y * макс. или мин. значение
                    if c_apply_accurately_to_form in config and config[c_apply_accurately_to_form] == True:
                        if spectrum[x].real > 0: newYreal =  y * maxYreal
                        else:                    newYreal =  -y * maxYreal
                        # newYreal =  y * maxYreal
                    # иначе, изменяем уровень спектра в данной точке пропорционально y
                    else: # abs(spectrum[x]) > y * spectrumMax:
                        newYreal = y * spectrum[x].real        
                    
                    spectrum[x]  = complex(newYreal, spectrum[x].imag)  
                    spectrum[-x] = complex(newYreal, spectrum[x].imag) # в зеркальной части спектра такое же значение

                    x+=1
    
                x1 = x2
                y1 = y2

            print('ok')

        # * конец 1 *

        # >> ПРИМЕНЯЕМ ПОЛОСОВОЙ ФИЛЬТР
        if c_filtrate in config and config[c_filtrate] == True:
            # обнуляем все значения, которые не входят в диапазон частот
            spectrum[:fmin_n] = 0.0   # в основной части спектра
            spectrum[-fmin_n:] = 0.0  # в зеркальной части спектра
    
            spectrum[fmax_n:fsdpcnt] = 0.0   # в основной части спектра
            spectrum[fsdpcnt:-fmax_n] = 0.0  # в зеркальной части спектра

        # << #####


        # преобразуем спектр обратно в сигнал
        yf = ifft(spectrum)
        aflt = arr.array('d', yf.real)

        # сохраняем отфильтрованный сигнал в файл
        print('сохраняю отфильтрованный сигнал ... ', end='')
        try:
            rawf = get_path(config, 'rawf')  # путь к файлу в который будет записан отфильтрованный сигнал
            
            with open(rawf, 'wb') as f:
                aflt.tofile(f)

            print('ok')

        except Exception as E:
            print(E, file=sys.stderr)
                                

    except Exception as E:
        print('error in function apply_spectrum(): %s' % E, file=sys.stderr)
        return None
        
    return aflt



#####################################################################  

if __name__ == "__main__":

    parser = createParser()

    if parser is None:

        # путь к файлу c исходным сигналом
        RAW_FILE_NAME = "D:/c++/AME/Generators/test_main.raw"

        # путь к файлу с отфильтрованным сигналом
        RAWF_FILE_NAME = "D:/c++/AME/Generators/www.rawf"

        # путь к файлу с формой спектра        
        SPECTRUM_FORM_FILE_NAME = "D:/c++/AME/Generators/www.spectrum"

        SIGNAL_SAMPLING = 100000 # дискретизация
        SIGNAL_DURATION = 1000

    else:
        RAW_FILE_NAME = parser.raw_file_name # путь к файлу c исходным сигналом
        RAWF_FILE_NAME = parser.rawf_file_name  # путь к файлу с отфильтрованным сигналом
        SPECTRUM_FORM_FILE_NAME = parser.spectrum_form_file_name # путь к файлу формой фильтра
        SIGNAL_SAMPLING = parser.sampling # дискретизация
        SIGNAL_DURATION = parser.duration

    _apply = bool(0)

    if _apply:
        apply_spectrum(raw=RAW_FILE_NAME,
                  rawf=RAWF_FILE_NAME,
                  sffn=SPECTRUM_FORM_FILE_NAME,
                  s=SIGNAL_SAMPLING,
                  d=SIGNAL_DURATION)
    else:
        edit_spectrum(raw=RAW_FILE_NAME,
                  sffn=SPECTRUM_FORM_FILE_NAME,
                  s=SIGNAL_SAMPLING,
                  d=SIGNAL_DURATION,
                  band_pass=True,
                  fmin=2000,
                  fmax=4000)