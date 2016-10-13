##from _generator_main import *
import sys
import _generator_main as gen
import _filter_main as flt
import _filter_fourier as fourier
import _filters_design as fld
import _plot_main as plot
import _shim_main as shim
import _socket_main as sock
import _AFC_main as afc
import _plot_shim as plotshim
import _read_wav as wav
import _spectrum_main as spectrum

# генератор  s_type_noise | s_type_sinus | s_type_sinus_noise | s_type_sinus_sinus_noise

signal_type = gen.s_type_sinus
freq = 200
sampling = 100000
duration = 1000
amplitude = 256
fadein = 0
fadeout = 0
filename_template = "d:/c++/AME/Generators/test_main" # добавляем разные расширения

# фильтр
freq_min = 500
freq_max = 3000

filter_algorithm = fld.f_algorithm_cheby1
filter_type = fld.f_type_bandpass
filter_rp = 2    # Уровень пульсаций в полосе пропускания в dB
filter_rs = 45   # Уровень ослабления сигнала на частотах задержания в dB
transition_band = 1500

# преобразование ШИМ
channel_count = 2
saw_count_per_point = 1
zero_smooth = 0
channel_gap = 0

# имена файлов
filename_raw = filename_template + '.raw'
filename_flt = filename_template + '.rawf'
filename_flt2 = filename_template + '.rawf2'
filename_shim = filename_template + '.shim'

# загрузка по сети
host = '172.16.4.55'
port = 35580
mode = sock.e_mode_loop

# отрисовка
point1=0
point2=1000

#####################################################
#####################################################

SEND_STOP = 0
AFC_ONLY = 0

EDIT_SPECTRUM = bool(0) and (signal_type != gen.s_type_sinus)
filename_spectrum = filename_template + '.spectrum'
APPLY_SPECTRUM = bool(0) | EDIT_SPECTRUM

FILTRATE = bool(1) and (signal_type != gen.s_type_sinus)

MAKE_SHIM = bool(1)

PLOT_SIGNAL = 1
PLOT_FILTERED = 1 & (int(FILTRATE) | int(APPLY_SPECTRUM))
PLOT_SIGNAL_SPECTRUM = 1
PLOT_FILTERED_SPECTRUM = 1 & (int(FILTRATE) | int(APPLY_SPECTRUM))
PLOT_SHIM = bool(0) and MAKE_SHIM
FLAGS = PLOT_SIGNAL | (PLOT_FILTERED << 1) | (PLOT_SIGNAL_SPECTRUM << 2) | (PLOT_FILTERED_SPECTRUM << 3) | (PLOT_SHIM << 4)


READ_WAV = 0
SEND = 0
PLOT = bool(1) and bool(FLAGS)

#####################################################
#####################################################

if SEND_STOP:
  sock.sendSTOP(host, port)
  sys.exit(0)

if AFC_ONLY:
    afc.afc(fmin=freq_min,
            fmax=freq_max,
            s=sampling,
            falg=filter_algorithm,
            ftype=filter_type,
            rp=filter_rp,
            rs=filter_rs,
            tb=transition_band)

    sys.exit(0)

if READ_WAV:
  araw = wav.wav(file_name="D:/c++/AME/imperia march r.wav",
                 to_file=filename_raw)
else:
  araw = gen.generate(t=signal_type,
             f=freq,
             s=sampling,
             d=duration,
             a=amplitude,
             fi=fadein,
             fo=fadeout,
             fn=filename_raw)

if araw is None:
  print('araw is None')
  sys.exit(1)


if EDIT_SPECTRUM:
  spectrum.edit_spectrum(s=sampling,
                   d=duration,
                   signal_data=araw,
                   sffn=filename_spectrum)

if APPLY_SPECTRUM:
  araw = spectrum.apply_spectrum(s=sampling,
                   d=duration,
                   signal_data=araw,
                   sffn=filename_spectrum,
                   rawf=filename_flt)


if araw is None:
  sys.exit(1)

if FILTRATE:
    # arawf = flt.filtrate(fmin=freq_min,
    #                      fmax=freq_max,
    #                      s=sampling,
    #                      falg=filter_algorithm,
    #                      ftype=filter_type,
    #                      rp=filter_rp,
    #                      rs=filter_rs,
    #                      tb=transition_band,
    #                      ifn=filename_raw,
    #                      ofn=filename_flt,
    #                      data=araw)

    arawf = fourier.filtrate(fmin=freq_min, fmax=freq_max,
                             s=sampling,
                             d=duration,
                             raw=filename_raw,
                             rawf=filename_flt,
                             signal_data=araw)

else:
    arawf = araw

if arawf is None:
    sys.exit(1)

if MAKE_SHIM:
  if not shim.shim(f=freq,
                   s=sampling,
                   d=duration,
                   a=amplitude,
                   rawfn=filename_raw,
                   shimfn=filename_shim,
                   zero=zero_smooth,
                   chgap=channel_gap,
                   chcnt=channel_count,
                   sawpp=saw_count_per_point,
                   fmin=freq_min,
                   fmax=freq_max,
                   falg=filter_algorithm,
                   ftype=filter_type,
                   rp=filter_rp,
                   rs=filter_rs,
                   tb=transition_band,
                   data=arawf):
    sys.exit(1)

if SEND:
    sock.send(host=host,
              port=port,
              mode=mode,
              fn=filename_shim)

if PLOT:
  plot.plot(raw=filename_raw,
              rawf=filename_flt,
              shim=filename_shim,
              s=sampling,
              d=duration,
              p1=point1,
              p2=point2,
              flags=FLAGS)


##plotshim.plot_shim(shim=filename_shim,
##                   p1=point1,
##                   p2=point2)
