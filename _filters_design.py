import math
import sys
import array as arr
import numpy as np
from scipy import *
from scipy import signal


# алгоритм фильтрации
f_algorithm_none   = -1 # не применять фильтр
f_algorithm_cheby1 = 0  # Chebyshev type I filter
f_algorithm_cheby2 = 1  # Chebyshev type II filter
f_algorithm_butt   = 2  # Butterworth filter
f_algorithm_ellip  = 3  # elliptical (Cauer or Zolotarev) filter
f_algorithm_bessel = 4  # bessel

# тип фильтра
f_type_low      = 1 # низкочастотный фильтр
f_type_high     = 2 # высокочастотный фильтр
f_type_bandpass = 3 # полосовой фильтр
f_type_bandstop = 4 # режекторный фильтр


##########################################
def cheby1(**kwargs):

    ftype = kwargs['ftype']
    freq_min = kwargs['fmin']
    freq_max = kwargs['fmax']
    tband = kwargs['tb']
    ss2 = kwargs['sampling'] / 2
    Rp = kwargs['rp']
    Rs = kwargs['rs']
    
    # значения для отрисовки линий частоты среза и частоты перехода
    lines = [[None, None], [None, None]]

    ftype_desc = None

    # полосовой фильтр
    if ftype == f_type_bandpass: 
        Wp = [freq_min / ss2, freq_max / ss2] # диапазон пропускаемых частот (числа в диапазоне 0..1)
        Ws = [(freq_min - tband) / ss2, (freq_max + tband) / ss2] # дипазон частот задержания ( Ws(1) < Wp(1) < Wp(2) < Ws(2) )

        ftype_desc = 'bandpass'
        print('freq_min={}  freq_max={}  ss2={}'.format(freq_min, freq_max, ss2))
        lines[0][0] = freq_min
        lines[0][1] = freq_min - tband
        lines[1][0] = freq_max
        lines[1][1] = freq_max + tband
        
    # низкочастотный фильтр
    elif ftype == f_type_low:  
        Wp = freq_max / ss2 # частота среза (числа в диапазоне 0..1)
        Ws = (freq_max + tband) / ss2 # частота перехода

        ftype_desc = 'lowpass'

        lines[1][0] = freq_max
        lines[1][1] = freq_max + tband

    # высокочастотный фильтр
    elif ftype == f_type_high: 
        
        Wp = freq_min / ss2 # частота среза (числа в диапазоне 0..1)
        Ws = (freq_min - tband) / ss2 # частота перехода

        ftype_desc = 'highpass'

        lines[0][0] = freq_min
        lines[0][1] = freq_min - tband

    # режекторный фильтр     
    else:  
        
        Wp = [freq_min / ss2, freq_max / ss2] # диапазон пропускаемых частот (числа в диапазоне 0..1)
        Ws = [(freq_min + tband) / ss2, (freq_max - tband) / ss2] # дипазон частот задержания ( Ws(1) < Wp(1) < Wp(2) < Ws(2) )
            
        ftype_desc = 'bandstop'
        
        lines[0][0] = freq_min
        lines[0][1] = freq_min + tband
        lines[1][0] = freq_max
        lines[1][1] = freq_max - tband

    # порядок фильтра n, частоты среза фильтра Wn
    n, Wn = signal.cheb1ord(Wp, Ws, Rp, Rs) 
        
    # параметры фильтра b, a
    b, a = signal.cheby1(n, Rp, Wn, btype=ftype_desc)

    title = 'Chebyshev 1 {} {} order filter'.format(ftype_desc, n)
    
    return b, a, lines, title

############################################

def cheby2(**kwargs):

    ftype = kwargs['ftype']
    freq_min = kwargs['fmin']
    freq_max = kwargs['fmax']
    tband = kwargs['tb']
    ss2 = kwargs['sampling'] / 2
    Rp = kwargs['rp']
    Rs = kwargs['rs']

    # значения для отрисовки линии частоты среза и частоты перехода
    lines = [[None, None], [None, None]]
    ftype_desc = None
    
    if ftype == f_type_bandpass: # полосовой фильтр
        Wp = [freq_min / ss2, freq_max / ss2] # диапазон пропускаемых частот (числа в диапазоне 0..1)
        Ws = [(freq_min - tband) / ss2, (freq_max + tband) / ss2] # дипазон частот задержания ( Ws(1) < Wp(1) < Wp(2) < Ws(2) )

        ftype_desc = 'bandpass'
        
        lines[0][0] = freq_min
        lines[0][1] = freq_min - tband
        lines[1][0] = freq_max
        lines[1][1] = freq_max + tband
        
    # низкочастотный фильтр
    elif ftype == f_type_low:  
        Wp = freq_max / ss2 # частота среза (числа в диапазоне 0..1)
        Ws = (freq_max + tband) / ss2 # частота перехода

        ftype_desc = 'lowpass'

        lines[1][0] = freq_max
        lines[1][1] = freq_max + tband

    # высокочастотный фильтр
    elif ftype == f_type_high: 
        
        Wp = freq_min / ss2 # частота среза (числа в диапазоне 0..1)
        Ws = (freq_min - tband) / ss2 # частота перехода

        ftype_desc = 'highpass'

        lines[0][0] = freq_min
        lines[0][1] = freq_min - tband
        
    # режекторный фильтр     
    else:  
        
        Wp = [freq_min / ss2, freq_max / ss2] # диапазон пропускаемых частот (числа в диапазоне 0..1)
        Ws = [(freq_min + tband) / ss2, (freq_max - tband) / ss2] # дипазон частот задержания ( Ws(1) < Wp(1) < Wp(2) < Ws(2) )
            
        ftype_desc = 'bandstop'

        lines[0][0] = freq_min
        lines[0][1] = freq_min + tband
        lines[1][0] = freq_max
        lines[1][1] = freq_max - tband

    # порядок фильтра n, частоты среза фильтра Wn
    n, Wn = signal.cheb2ord(Wp, Ws, Rp, Rs) 
        
    # параметры фильтра b, a
    b, a = signal.cheby2(n, Rs, Wn, btype=ftype_desc)

    title = 'Chebyshev 2 {} {} order filter'.format(ftype_desc, n)
    return b, a, lines, title

##################################################
        
def butt(**kwargs):

    ftype = kwargs['ftype']
    freq_min = kwargs['fmin']
    freq_max = kwargs['fmax']
    tband = kwargs['tb']
    ss2 = kwargs['sampling'] / 2
    Rp = kwargs['rp']
    Rs = kwargs['rs']
    
    # значения для отрисовки линии частоты среза и частоты перехода
    lines = [[None, None], [None, None]]
    ftype_desc = None
    
    if ftype == f_type_bandpass: # полосовой фильтр
        Wp = [freq_min / ss2, freq_max / ss2] # диапазон пропускаемых частот (числа в диапазоне 0..1)
        Ws = [(freq_min - tband) / ss2, (freq_max + tband) / ss2] # дипазон частот задержания ( Ws(1) < Wp(1) < Wp(2) < Ws(2) )

        ftype_desc = 'bandpass'
        
        lines[0][0] = freq_min
        lines[0][1] = freq_min - tband
        lines[1][0] = freq_max
        lines[1][1] = freq_max + tband
        
    # низкочастотный фильтр
    elif ftype == f_type_low:  
        Wp = freq_max / ss2 # частота среза (числа в диапазоне 0..1)
        Ws = (freq_max + tband) / ss2 # частота перехода

        ftype_desc = 'lowpass'

        lines[1][0] = freq_max
        lines[1][1] = freq_max + tband

    # высокочастотный фильтр
    elif ftype == f_type_high: 
        
        Wp = freq_min / ss2 # частота среза (числа в диапазоне 0..1)
        Ws = (freq_min - tband) / ss2 # частота перехода

        ftype_desc = 'highpass'

        lines[0][0] = freq_min
        lines[0][1] = freq_min - tband
        
    # режекторный фильтр     
    else:  
        
        Wp = [freq_min / ss2, freq_max / ss2] # диапазон пропускаемых частот (числа в диапазоне 0..1)
        Ws = [(freq_min + tband) / ss2, (freq_max - tband) / ss2] # дипазон частот задержания ( Ws(1) < Wp(1) < Wp(2) < Ws(2) )
            
        ftype_desc = 'bandstop'

        lines[0][0] = freq_min
        lines[0][1] = freq_min + tband
        lines[1][0] = freq_max
        lines[1][1] = freq_max - tband

    # порядок фильтра n, частоты среза фильтра Wn
    n, Wn = signal.buttord(Wp, Ws, Rp, Rs) 

    # параметры фильтра b, a
    b, a = signal.butter(n, Wn, btype=ftype_desc)
    print(n, Wn)
    title = 'Butterworth {} {} order filter'.format(ftype_desc, n)
    return b, a, lines, title

##################################################
        
        
def ellip(**kwargs):

    ftype = kwargs['ftype']
    freq_min = kwargs['fmin']
    freq_max = kwargs['fmax']
    tband = kwargs['tb']
    ss2 = kwargs['sampling'] / 2
    Rp = kwargs['rp']
    Rs = kwargs['rs']

    # значения для отрисовки линии частоты среза и частоты перехода
    lines = [[None, None], [None, None]]
    ftype_desc = None
    
    if ftype == f_type_bandpass: # полосовой фильтр
        Wp = [freq_min / ss2, freq_max / ss2] # диапазон пропускаемых частот (числа в диапазоне 0..1)
        Ws = [(freq_min - tband) / ss2, (freq_max + tband) / ss2] # дипазон частот задержания ( Ws(1) < Wp(1) < Wp(2) < Ws(2) )

        ftype_desc = 'bandpass'
        
        lines[0][0] = freq_min
        lines[0][1] = freq_min - tband
        lines[1][0] = freq_max
        lines[1][1] = freq_max + tband
        
    # низкочастотный фильтр
    elif ftype == f_type_low:  
        Wp = freq_max / ss2 # частота среза (числа в диапазоне 0..1)
        Ws = (freq_max + tband) / ss2 # частота перехода

        ftype_desc = 'lowpass'

        lines[1][0] = freq_max
        lines[1][1] = freq_max + tband

    # высокочастотный фильтр
    elif ftype == f_type_high: 
        
        Wp = freq_min / ss2 # частота среза (числа в диапазоне 0..1)
        Ws = (freq_min - tband) / ss2 # частота перехода

        ftype_desc = 'highpass'

        lines[0][0] = freq_min
        lines[0][1] = freq_min - tband
        
    # режекторный фильтр     
    else:  
        
        Wp = [freq_min / ss2, freq_max / ss2] # диапазон пропускаемых частот (числа в диапазоне 0..1)
        Ws = [(freq_min + tband) / ss2, (freq_max - tband) / ss2] # дипазон частот задержания ( Ws(1) < Wp(1) < Wp(2) < Ws(2) )
            
        ftype_desc = 'bandstop'

        lines[0][0] = freq_min
        lines[0][1] = freq_min + tband
        lines[1][0] = freq_max
        lines[1][1] = freq_max - tband

    # порядок фильтра n, частоты среза фильтра Wn
    n, Wn = signal.ellipord(Wp, Ws, Rp, Rs) 

    # параметры фильтра b, a
    b, a = signal.ellip(n, Rp, Rs, Wn, btype=ftype_desc)

    title = 'Elliptic (Cauer) {} {} order filter'.format(ftype_desc, n)
    return b, a, lines, title


