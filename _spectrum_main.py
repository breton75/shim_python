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

from matplotlib import rc
rc('font', family='Verdana') # для отображения русского шрифта

from matplotlib.lines import Line2D
from matplotlib.artist import Artist
from matplotlib.mlab import dist_point_to_segment

HEADER_STRUCT = '16sII' # заголовок, версия, кол-во точек
FILE_DESIGNATION = b'SPECTRUM FORM   '
FILE_VER = 0x00000001 # 0.0.0.1
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

    def __init__(self, ax, poly, file_name, aspec, fmin, fmax):
        if poly.figure is None:
            raise RuntimeError('You must first add the polygon to a figure or canvas before defining the interactor')
        self.ax = ax
        canvas = poly.figure.canvas
        self.poly = poly
        self.file_name = file_name
        self.fmin = fmin
        self.fmax = fmax
        self.aspec = aspec[fmin:fmax]
        self.maxY = float(max(self.aspec))
        self.xstep = get_xstep(len(aspec), len(poly.xy) - 2)

        x, y = zip(*self.poly.xy)
        
        self.line = Line2D(x, y, marker='o', markerfacecolor='r', markersize=10, animated=True, drawstyle='steps-mid', color='red', lw=2)
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
                    # val = int(event.key) / 10
                    self.poly.xy[ind][1] = self.maxY * int(event.key) / 10
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

            f.write(struct.pack(HEADER_STRUCT, FILE_DESIGNATION, FILE_VER, len(x) - 2)) 

            for i in range(1, len(x) - 1, 1):
                f.write(struct.pack('d', float(y[i]) / self.maxY))

            
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

            maxY = max(self.aspec)
            for i in range(1, controls_count - 1):
                self.poly.xy[i][0] = self.fmin + (i - 1) * step
                self.poly.xy[i][1] = maxY
                # print('x=%i  y=%f' % (self.poly.xy[i][0], self.poly.xy[i][1]))
            
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
        if self._ind is None or self._ind == 0 or self._ind == len(self.poly.xy) - 1:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        # x, y = event.xdata, event.ydata
        y = event.ydata

        self.poly.xy[self._ind] = self.x_const, y
        
        self.line.set_data(zip(*self.poly.xy))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
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


def signal2spectrum(**kwargs):
    try:
        # print('Start signal to spectrum converting')

        araw = None
        spectrum = None
        aspec = None

        if not ('s' in kwargs and 'd' in kwargs):
            raise Exception('incorrect paramters specified')

        sampling = kwargs['s'] # дискретизация
        duration = kwargs['d']
        point_count = int(sampling * duration / 1000)

        fsdpcnt = int((sampling / 2) * (duration / 1000)) # point_count / 2
        fpcnt = int(sampling / 2)
        
        # print('s=%i  d=%i  pcnt=%i  fsdpcnt=%i' % (sampling, duration, point_count, fsdpcnt))
        # print(kwargs)

        # сигнал должен быть передан как массив
        if 'signal_data' in kwargs:
            araw = kwargs['signal_data']

        elif 'raw' in kwargs: # иначе читаем исходный файл
            try:
    
                f = open(kwargs['raw'], 'rb')
                araw = arr.array('d')
                araw.fromfile(f, point_count)
                f.close()
                
            except Exception as E:
                raise Exception(E)

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
        print('error in func signal2spectrum(): ', file=sys.stderr, end='')
        print(E, file=sys.stderr)


    finally:
        return spectrum, aspec, araw


def read_spectrum_form_file(**kwargs):
    try:
        # print('start read_spectrum_file')

        if not 'sffn' in kwargs:
            raise Exception('spectrum form file name is not specified')

        spectrum_form_file_name = kwargs['sffn']
        ver = None
        controls_count = None
        controls = None   


        header = duty.read_header(spectrum_form_file_name, HEADER_STRUCT)
        
        if header is None:
            raise Exception('wrog spectrum form file header')

        if header[0] != FILE_DESIGNATION:
            raise Exception('wrog spectrum form file header')

        ver = header[1]
        controls_count = header[2]
        # maxX = header[3]
        # maxY = header[4]

        controls = duty.read_file(spectrum_form_file_name, 'd', struct.calcsize(HEADER_STRUCT), controls_count)
        # print(ver, point_count, dataY)

        # print('end read_spectrum_file')

    except Exception as E:
        print('error in function read_spectrum_form_file(): ', file=sys.stderr, end='')
        print(E, file=sys.stderr)
        # return None, No

    
    return ver, controls_count, controls

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


def edit_spectrum(**kwargs):

    try:
        # print('Start spectrum editing')

        if not 'sffn' in kwargs: raise Exception('spectrum form file name is not specified')
        if not 's' in kwargs: raise Exception('sampling is not specified')
        if not 'd' in kwargs: raise Exception('duration is not specified')

        sampling = kwargs['s'] # дискретизация
        duration = kwargs['d']
        point_count = int(sampling * duration / 1000)


        spectrum, aspec, araw = signal2spectrum(**kwargs)
        
        if spectrum is None or aspec is None:
            raise Exception('no spectrum got')


        # задаем границы массива. если нужно применить полосовой фильтр, то отсекаем все, что не входит в [fmin:fmax]
        fmin = 0
        fmax = len(aspec)
        if 'band_pass' in kwargs and kwargs['band_pass'] == True:
            if not ('fmin' in kwargs and 'fmax' in kwargs):
                raise Exception('params for band pass filter are not specified')

            fmin = kwargs['fmin']
            fmax = kwargs['fmax']


        spectrumMax = max(aspec[fmin:fmax])

        spectrum_form_file_name = ''
        if 'sffn' in kwargs:
            spectrum_form_file_name = kwargs['sffn']

    ###############################################
        # print('max(spectrum)=%d  len(aspec)=%i' % (spectrumMax, len(aspec)))

        fig, ax = plt.subplots()
        plt.vlines(range(fmin, fmax, 1), 0, aspec[fmin:fmax], label=' ', color='b')
        # plt.plot(aspec[fmin:fmax], drawstyle='steps', label=' ')
        plt.legend(title='Редактор формы спектра\nctrl + r - сброс\nctrl + w - сохранить и выйти\n0..9 - установить уровень регулятора', loc='upper left', shadow=True, frameon=True, fontsize='small')
        plt.axis([fmin, fmax, 0, spectrumMax * 1.5])

        ver, controls_count, controls = read_spectrum_form_file(**kwargs)
        # print(ver, controls_count)

        # если не удалось прочитать сохраненную форму спектра, то создаем новую
        if controls_count is None or controls is None:
        
            xs, ys = get_xs_ys(fmin, fmax, CONTROL_COUNT)

            ys[1:-1] = spectrumMax
            
            plt.xticks(arange(fmin, fmax, int(get_xstep(fmax - fmin, CONTROL_COUNT)) * 2)) #, arange(0, len(aspec), get_xstep(len(aspec), CONTROL_COUNT)))

        else:

            xs, ys = get_xs_ys(fmin, fmax, controls_count)
            
            for i in range(1, controls_count + 1, 1):
                ys[i] = controls[i - 1] * spectrumMax

            plt.xticks(arange(fmin, fmax, int(get_xstep(fmax - fmin, controls_count)) * 2)) #, arange(0, len(aspec), get_xstep(len(aspec), controls_count) * 4))


        from matplotlib.colors import colorConverter
        from matplotlib.patches import Polygon
        poly = Polygon(list(zip(xs, ys)), animated=True, closed=False, color=colorConverter.to_rgba('r', 0.500), visible=True)
        ax.add_patch(poly)
        p = PolygonInteractor(ax, poly, spectrum_form_file_name, aspec, fmin, fmax)
        
        plt.autumn()
        plt.grid()
        plt.show()

        # print('Spectrum editing finished')

    except Exception as E:
        print('error in function edit_spectrum(): ', file=sys.stderr, end='')
        print(E, file=sys.stderr)


def apply_spectrum(**kwargs):
    try:
        # print('Start spectrum appling')

        aflt = None

        if not 'sffn' in kwargs: raise Exception('Не указано имя файла с формой спектра')
        if not 'rawf' in kwargs: raise Exception('Не указано имя файла для сохранения')
        
        # if not 's' in kwargs: raise Exception('Не указана дискретизация')
        # if not 'd' in kwargs: raise Exception('Не указана длительность сигнала')

        spectrum_form_file_name = kwargs['sffn']
        rawf = kwargs['rawf']      # путь к файлу в который будет записан отфильтрованный сигнал

        sampling = kwargs['s'] # дискретизация
        duration = kwargs['d']
        point_count = int(sampling * duration / 1000)
        fsdpcnt = int((sampling / 2) * (duration / 1000))
        fpcnt = int(sampling / 2)

        spectrum, aspec, araw = signal2spectrum(**kwargs)

        if spectrum is None or araw is None:
            raise Exception('converting to spectrum error')

        # задаем границы массива. если нужно применить полосовой фильтр, то отсекаем все, что не входит в [fmin:fmax]
        fmin = 0
        fmax = len(aspec)
        if 'band_pass' in kwargs and kwargs['band_pass'] == True:
            if not ('fmin' in kwargs and 'fmax' in kwargs):
                raise Exception('params for band pass filter are not specified')

            fmin = kwargs['fmin']
            fmax = kwargs['fmax']


        spectrumMax = max(aspec[fmin:fmax])


        ver, controls_count, controls = read_spectrum_form_file(**kwargs)
    
        # если не удалось прочитать сохраненную форму спектра, то выходим с ошибкой
        if controls_count is None or controls is None:
            raise Exception('error on reading spectrum form')

        fmin_n = int(fmin * fsdpcnt / fpcnt)
        fmax_n = int(fmax * fsdpcnt / fpcnt)

        xstep = get_xstep(fmax_n - fmin_n, controls_count)
        x = fmin_n
        x1 = fmin_n
        y1 = controls[0]
        
        for i in range(1, controls_count, 1):
            x2 = fmin_n + i * xstep
            y2 = controls[i]


            # print('i=%d' % i)
            while x < x2:
    
                # находим значение (у) точки пересечения прямой x = j и прямой (x1,y1)-(x2,y2)
                # уравнение прямой (х1,у1)-(х2,у2):  (x - x1)/(x2 - x1) = (y - y1)/(y2 - y1), отсюда
                # y = (x - x1)/(x2 - x1) * (y2 - y1) + y1. так как x = j, получим:

                y = (x - x1) / (x2 - x1) * (y2 - y1) + y1
                # print('i=%i  x1=%d y1=%0.2f  x2=%d y2=%0.2f  x=%i  y=%0.2f  araw[x]=%0.2f' % (i, x1, y1, x2, y2, x, y, araw[x]) )
                # print('y={}'.format(y))
                if abs(spectrum[x]) > y * spectrumMax:
                    # print('complex={}'.format(complex(y * spectrumMax, spectrum[x].imag)))
                    spectrum[x] =  complex(y * spectrum[x].real, spectrum[x].imag)
                    spectrum[-x] =  complex(y * spectrum[x].real, spectrum[x].imag)
    
                x+=1
    
            x1 = x2
            y1 = y2

        # обнуляем все значения, которые не входят в диапазон частот
        spectrum[:fmin_n] = 0.0   # в основной части спектра
        spectrum[-fmin_n:] = 0.0  # в зеркальной части спектра
    
        spectrum[fmax_n:fsdpcnt] = 0.0   # в основной части спектра
        spectrum[fsdpcnt:-fmax_n] = 0.0  # в зеркальной части спектра

        # фильтрация
        yf = ifft(spectrum)
        aflt = arr.array('d', yf.real)

        # сохраняем отфильтрованный сигнал в файл
        try:
            f = open(rawf, 'wb')
            aflt.tofile(f)
            f.close()

        except Exception as E:
            raise Exception(E)
        
        print('filtered signal saved successfully')
                        

    except Exception as E:
        print('error in function apply_spectrum(): ', file=sys.stderr, end='')
        print(E, file=sys.stderr)
        return None
        
    # print('Spectrum applyed successfully')

    return aflt



#####################################################################  

if __name__ == "__main__":

    parser = createParser()

    if parser is None:

        # путь к файлу c исходным сигналом
        RAW_FILE_NAME = "D:/c++/AME/Generators/test_main.raw"

        # путь к файлу с отфильтрованным сигналом
        RAWF_FILE_NAME = "D:/c++/AME/Generators/test_main.rawf"

        # путь к файлу с формой спектра        
        SPECTRUM_FORM_FILE_NAME = "D:/c++/AME/Generators/test_main.spectrum"

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
                  fmin=1500,
                  fmax=3000)