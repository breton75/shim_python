import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *

import _generator_main as gen
import _plot_main as plot
import _shim_main as shim
import _socket_main as sock
import _read_wav as wav
import _spectrum_main as spectrum
# from _exec_main import execute
# from _exec_main import get_cfg_param

import matplotlib.pyplot as plt


class mainFrame(Frame):
	def __init__(self, master):
		super(mainFrame, self).__init__(master)
		self.grid() #row=0, column=0, sticky=tk.W)
		
		self.config = {}

		self.showFrame()



	def showFrame(self):
 
		# читаем файл _main.config
		try:

			with open('_main.config', 'r') as configfile:
				lines = configfile.readlines()

				# разбираем параметры записанные в файле _main.config
				lst=[]
				for line in lines: # если строка начинается не с буквы, то эту строку пропускаем
					if line[0] in ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']:
						lst.append(line.split('='))
	  
				for i in range(len(lst)):
					for j in range(len(lst[i])):
						lst[i][j] = lst[i][j].strip()

				self.config = dict(lst)

		except Exception as E:
			print('error on reading self.config file: ', file=sys.stderr, end='')
			print(E, file=sys.stderr)  
			self.config = {}


	### -> параметры генерации исходного сигнала ###
	
		self.frameSignal = tk.LabelFrame(self, text='Генератор')
		self.frameSignal.grid(row=0, column=0, sticky=tk.W)

		# тип сигнала
		self.lblSignalType = tk.Label(self.frameSignal, text='Тип сигнала', width=25)
		self.lblSignalType.grid(row=0, column=0, sticky=tk.E)
	
		self.cbSignalType = ttk.Combobox(self.frameSignal, width=13, values=['Шум', 'Синус', 'Синус+Шум', 'Синус+Синус+Шум'])
		self.cbSignalType.grid(row=0, column=1, sticky=tk.W)
		self.cbSignalType.current(newindex=get_cfg_param(self.config, 'signal_type', 0, 'i'))
	
		# частота
		self.lblFrequency = tk.Label(self.frameSignal, text='Частота', width=25)
		self.lblFrequency.grid(row=1, column=0, sticky=tk.E)

		self.editFrequency = tk.Entry(self.frameSignal, width=16)
		self.editFrequency.grid(row=1, column=1, sticky=tk.W)
		self.editFrequency.insert(0, get_cfg_param(self.config, 'freq', '8000'))


		# дискретизация
		self.lblSampling = tk.Label(self.frameSignal, text='Дискретизация', width=25)
		self.lblSampling.grid(row=2, column=0, sticky=tk.E)
		self.editSampling = tk.Entry(self.frameSignal, width=16)
		self.editSampling.grid(row=2, column=1, sticky=tk.W)
		self.editSampling.insert(0, get_cfg_param(self.config, 'sampling', '100000'))


		# длительность (мс.)
		self.lblDuration = tk.Label(self.frameSignal, text='Длительность (мс)', width=25)
		self.lblDuration.grid(row=3, column=0, sticky=tk.E)
		self.editDuration = tk.Entry(self.frameSignal, width=16)
		self.editDuration.grid(row=3, column=1, sticky=tk.W)
		self.editDuration.insert(0, get_cfg_param(self.config, 'duration', '1000'))

		# амплитуда
		self.lblAmplitude = tk.Label(self.frameSignal, text='Амплитуда', width=25)
		self.lblAmplitude.grid(row=4, column=0, sticky=tk.E)

		self.editAmplitude = tk.Entry(self.frameSignal, width=16)
		self.editAmplitude.grid(row=4, column=1, sticky=tk.W)
		self.editAmplitude.insert(0, get_cfg_param(self.config, 'amplitude', '1024'))

		# раскачка сигнала
		self.lblFadeIn = tk.Label(self.frameSignal, text='Раскачка (%)', width=25)
		self.lblFadeIn.grid(row=5, column=0, sticky=tk.E)

		self.editFadeIn = tk.Entry(self.frameSignal, width=16)
		self.editFadeIn.grid(row=5, column=1, sticky=tk.W)
		self.editFadeIn.insert(0, get_cfg_param(self.config, 'fadein', '0'))

		# затухание сигнала
		lblFadeOut = tk.Label(self.frameSignal, text='Затухание (%)', width=25).grid(row=6, column=0, sticky=tk.E)
		self.editFadeOut = tk.Entry(self.frameSignal, width=16)
		self.editFadeOut.grid(row=6, column=1, sticky=tk.W)
		self.editFadeOut.insert(0, get_cfg_param(self.config, 'fadeout', '0'))
	
	### <- параметры сигнала ###	

	## -> фильтрация ##

		self.frameFilter = tk.LabelFrame(self, text='Фильтрация')
		self.frameFilter.grid(row=1, column=0, sticky=tk.W)

		self.filtrate = BooleanVar()
		self.checkFilter = tk.Checkbutton(self.frameFilter, text='Применить полосовой фильтр', variable=self.filtrate)
		self.checkFilter.grid(row=0, column=0, sticky=tk.W, columnspan=2)
		self.filtrate.set(get_cfg_param(self.config, 'filtrate', True, 'b'))
		# else: self.filtrate.set(False)

		# минимальная частота
		self.lblFreqMin = tk.Label(self.frameFilter, text='Мин. частота', width=25)
		self.lblFreqMin.grid(row=1, column=0, sticky=tk.E)
		self.editFreqMin = tk.Entry(self.frameFilter, width=16)
		self.editFreqMin.grid(row=1, column=1, sticky=tk.W)
		self.editFreqMin.insert(0, get_cfg_param(self.config, 'freq_min', '1000'))

		# максимальная частота
		self.lblFreqMax = tk.Label(self.frameFilter, text='Макс. частота', width=25)
		self.lblFreqMax.grid(row=2, column=0, sticky=tk.E)
		self.editFreqMax = tk.Entry(self.frameFilter, width=16)
		self.editFreqMax.grid(row=2, column=1, sticky=tk.W)
		self.editFreqMax.insert(0, get_cfg_param(self.config, 'freq_max', '4000'))
		
		# редактировать форму спектра
		# self.edit_spectrum_form = BooleanVar()
		# self.checkEditSpectrumForm = tk.Checkbutton(self.frameFilter, text='Редактировать форму спектра', variable=self.edit_spectrum_form)
		# self.checkEditSpectrumForm.grid(row=3, column=0, sticky=tk.W, columnspan=2)
		# self.edit_spectrum_form.set(get_cfg_param(self.config, 'edit_spectrum_form', False, 'b'))


		# # применить форму спектра
		self.apply_spectrum_form = BooleanVar()
		self.checkApplySpectrumForm = tk.Checkbutton(self.frameFilter, text='Применить заданную форму спектра', variable=self.apply_spectrum_form)
		self.checkApplySpectrumForm.grid(row=4, column=0, sticky=tk.W, columnspan=2)
		self.apply_spectrum_form.set(get_cfg_param(self.config, 'apply_spectrum_form', False, 'b'))

		# новая форма спектра
		self.bnCreateSpectrumForm = tk.Button(self.frameFilter, text='Новая форма спектра', command=self.create_spectrum)
		self.bnCreateSpectrumForm.grid(row=6, column=0, sticky=tk.W, columnspan=2)

		# редактор
		self.bnEditSpectrumForm = tk.Button(self.frameFilter, text='Редактор формы спектра', command=self.edit_spectrum)
		self.bnEditSpectrumForm.grid(row=7, column=0, sticky=tk.W, columnspan=2)

	## <- фильтрация ##

	## -> преобразование шим ##

		self.frameShim = tk.LabelFrame(self, text='Преобразование ШИМ')
		self.frameShim.grid(row=0, column=1, sticky=tk.N, rowspan=1)

		# кол-во каналов
		lblChannelCount = tk.Label(self.frameShim, text='Кол-во каналов', width=25).grid(row=0, column=0, sticky=tk.E)
		self.editChannelCount = tk.Entry(self.frameShim, width=16)
		self.editChannelCount.grid(row=0, column=1, sticky=tk.W)
		self.editChannelCount.insert(0, get_cfg_param(self.config, 'channel_count', '2'))
		
		# пил на точку
		lblSawpp = tk.Label(self.frameShim, text='Пил на точку', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editSawpp = tk.Entry(self.frameShim, width=16)
		self.editSawpp.grid(row=1, column=1, sticky=tk.W)
		self.editSawpp.insert(0, get_cfg_param(self.config, 'saw_count_per_point', '1'))
		
		# размытие нуля
		lblZeroSmooth = tk.Label(self.frameShim, text='Размытие нуля (%)', width=25).grid(row=2, column=0, sticky=tk.E)
		self.editZeroSmooth = tk.Entry(self.frameShim, width=16)
		self.editZeroSmooth.grid(row=2, column=1, sticky=tk.W)
		self.editZeroSmooth.insert(0, get_cfg_param(self.config, 'zero_smooth', '0'))

		# разрыв между каналами
		lblChannelGap = tk.Label(self.frameShim, text='Разрыв между каналами (%)', width=25).grid(row=3, column=0, sticky=tk.E)
		self.editChannelGap = tk.Entry(self.frameShim, width=16)
		self.editChannelGap.grid(row=3, column=1, sticky=tk.W)
		self.editChannelGap.insert(0, get_cfg_param(self.config, 'channel_gap', '0'))

	## <- преобразование шим ##

	## -> выгрузка на устройство ##

		self.frameSend = tk.LabelFrame(self, text='Выгрузка')
		self.frameSend.grid(row=1, column=1, sticky=tk.N)

		self.send = BooleanVar()
		self.checkSend = tk.Checkbutton(self.frameSend, text='Выгрузить сигнал на устройство', variable=self.send)
		self.checkSend.grid(row=0, column=0, sticky=tk.E, columnspan=2)
		# print(self.config['send'])
		self.send.set(get_cfg_param(self.config, 'send', True, 'b'))

		# host
		lblHost = tk.Label(self.frameSend, text='IP', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editHost = tk.Entry(self.frameSend, width=16)
		self.editHost.grid(row=1, column=1, sticky=tk.W)
		self.editHost.insert(0, get_cfg_param(self.config, 'host', '172.16.4.55'))
		
		# port
		lblPort = tk.Label(self.frameSend, text='Порт', width=25).grid(row=2, column=0, sticky=tk.E)
		self.editPort = tk.Entry(self.frameSend, width=16)
		self.editPort.grid(row=2, column=1, sticky=tk.W)
		self.editPort.insert(0, get_cfg_param(self.config, 'port', '35580'))
		
		# режим работы: ONE или LOOP
		self.lblMode = tk.Label(self.frameSend, text='Режим работы', width=25)
		self.lblMode.grid(row=3, column=0, sticky=tk.E)
	
		self.cbMode = ttk.Combobox(self.frameSend, width=13, values=['ONE', 'LOOP'])
		self.cbMode.grid(row=3, column=1, sticky=tk.W)
		self.cbMode.current(newindex=get_cfg_param(self.config, 'mode', 1))

		# send STOP
		self.bnSendStop = tk.Button(self.frameSend, text='Отправить STOP', command=self.send_stop)
		self.bnSendStop.grid(row=4, column=0, sticky=tk.E, columnspan=2)

	## <- выгрузка на устройство ##


	## -> отрисовка ##

		self.framePlot = tk.LabelFrame(self, text='Отрисовка')
		self.framePlot.grid(row=3, column=0, sticky=tk.W, columnspan=3)

		# отобразить сигнал
		self.plot_signal = BooleanVar()
		self.checkPlotSignal = tk.Checkbutton(self.framePlot, text='Сигнал', variable=self.plot_signal)
		self.checkPlotSignal.grid(row=0, column=0, sticky=tk.W, columnspan=4)
		self.plot_signal.set(get_cfg_param(self.config, 'plot_signal', True, 'b'))

		# отобразить спектр сигнала
		self.plot_signal_spectrum = BooleanVar()
		self.checkSignalSpectrum = tk.Checkbutton(self.framePlot, text='Спектр сигнала', variable=self.plot_signal_spectrum)
		self.checkSignalSpectrum.grid(row=0, column=1, sticky=tk.W, columnspan=4)
		self.plot_signal_spectrum.set(get_cfg_param(self.config, 'plot_signal_spectrum', True, 'b'))
		
		# отобразить отфильтрованный сигнал
		self.plot_filtered_signal = BooleanVar()
		self.checkPlotFiltered = tk.Checkbutton(self.framePlot, text='Отфильтрованный сигнал', variable=self.plot_filtered_signal)
		self.checkPlotFiltered.grid(row=1, column=0, sticky=tk.W, columnspan=4)
		self.plot_filtered_signal.set(get_cfg_param(self.config, 'plot_filtered_signal', True, 'b'))
	
		# отобразить спектр отфильтрованного сигнала
		self.plot_filtered_spectrum = BooleanVar()
		self.checkPlotFilteredSignalSpectrum = tk.Checkbutton(self.framePlot, text='Спектр отфильтрованного сигнала', variable=self.plot_filtered_spectrum)
		self.checkPlotFilteredSignalSpectrum.grid(row=1, column=1, sticky=tk.W, columnspan=4)
		self.plot_filtered_spectrum.set(get_cfg_param(self.config, 'plot_filtered_spectrum', True, 'b'))

		# отобразить ШИМ
		self.plot_shim = BooleanVar()
		self.checkPlotShim = tk.Checkbutton(self.framePlot, text='ШИМ', variable=self.plot_shim)
		self.checkPlotShim.grid(row=2, column=0, sticky=tk.W, columnspan=4)
		self.plot_shim.set(get_cfg_param(self.config, 'plot_shim', True, 'b'))
		
		# отобразить сигнал + пила
		self.plot_signal_saw = BooleanVar()
		self.checkSignalSaw = tk.Checkbutton(self.framePlot, text='Сигнал + Пила', variable=self.plot_signal_saw)
		self.checkSignalSaw.grid(row=2, column=1, sticky=tk.W, columnspan=4)
		self.plot_signal_saw.set(get_cfg_param(self.config, 'plot_signal_saw', False, 'b'))

		# сигнал с точки .. по ..
		lblPlotFromPoint = tk.Label(self.framePlot, text='Показать точки с', width=25).grid(row=3, column=0, sticky=tk.E)
		self.editPlotFromPoint = tk.Entry(self.framePlot, width=5)
		self.editPlotFromPoint.grid(row=3, column=1, sticky=tk.W)
		self.editPlotFromPoint.insert(0, get_cfg_param(self.config, 'plot_from_point', '1'))
		
		lblPlotToPoint = tk.Label(self.framePlot, text=' по ', width=4).grid(row=3, column=2, sticky=tk.E)
		self.editPlotToPoint = tk.Entry(self.framePlot, width=53)
		self.editPlotToPoint.grid(row=3, column=3, sticky=tk.W)
		self.editPlotToPoint.insert(0, get_cfg_param(self.config, 'plot_to_point', '1000'))

	## <- отрисовка ##

	## -> общее ##
	
		self.frameGen = tk.LabelFrame(self, text='Общее')
		self.frameGen.grid(row=5, column=0, sticky=tk.W, columnspan=2)

		# рабочий каталог
		lblWorkDir = tk.Label(self.frameGen, text='Рабочий каталог', width=25).grid(row=0, column=0, sticky=tk.E)
		self.editWorkDir = tk.Entry(self.frameGen, width=65)
		self.editWorkDir.grid(row=0, column=1, sticky=tk.W)
		self.editWorkDir.insert(0, get_cfg_param(self.config, 'workdir', ''))
		
		# шаблон имен файлов
		lblFilenameTemplate = tk.Label(self.frameGen, text='Шаблон имен файлов', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editFilenameTemplate = tk.Entry(self.frameGen, width=65)
		self.editFilenameTemplate.grid(row=1, column=1, sticky=tk.W)
		self.editFilenameTemplate.insert(0, get_cfg_param(self.config, 'filename_template', ''))
		
	## <- общее ##

	## -> кнопки ##

		self.frameButtons = tk.Frame(self)
		self.frameButtons.grid(row=6, column=0, sticky=tk.W, columnspan=2)

		# ПУСК
		self.bnStart = tk.Button(self.frameButtons, text='Старт', width=80, command = self.start)
		self.bnStart.grid(row=1, column=0, sticky=tk.E, columnspan=2)

		# сохранить
		self.bnSave = tk.Button(self.frameButtons, text='Сохранить', width=80, command = self.save)
		self.bnSave.grid(row=3, column=0, sticky=tk.E, columnspan=2)

	## <- кнопки ##

	# def get_cfg(self, param_name, default):
	# 	if param_name in self.config: return self.config[param_name]
	# 	else: return default


	def send_stop(self):
		try:
			h = self.editHost.get()
			p = int(self.editPort.get())
			sock.sendSTOP(h, p)

		except Exception as E:
			sys.stderror.write(E)


	def create_spectrum(self):
		try:
			if self.checkout_config() is None: return

			fn = self.config['workdir']
			if len(fn) == 0:
				raise Exception('Path not found')

			if fn[-1] != '/': fn += '/'
			fn += self.config['filename_template']

			with open(fn + '.spectrum', 'w') as f:
				pass

			spectrum.edit_spectrum(sffn=fn + '.spectrum', s=self.config['sampling'], d=self.config['duration'], fmin=self.config['freq_min'], fmax=self.config['freq_max'])

		except Exception as E:
			print(E, file=sys.stderr)			


	def edit_spectrum(self):
		try:
			if self.checkout_config() is None: return

			fn = self.config['workdir']
			if len(fn) == 0:
				raise Exception('Path not found')

			if fn[-1] != '/': fn += '/'
			fn += self.config['filename_template']

			spectrum.edit_spectrum(sffn=fn + '.spectrum', s=self.config['sampling'], d=self.config['duration'], fmin=self.config['freq_min'], fmax=self.config['freq_max'])

		except Exception as E:
			print(E, file=sys.stderr)	


	def start(self):
		try:

			self.save()
			do(self.config)
	  
		except Exception as E:
			print('error in func _ui.start(): ', file=sys.stderr, end='')
			print(E, file=sys.stderr)  


	def save(self):

		self.checkout_config()

		cfg = self.config.copy()

		# читаем файл _main.config
		try:

			with open('_main.config', 'r') as configfile:
				lines = configfile.readlines()
	  
			with open('_main.config', 'w') as configfile:
				# проходим по параметрам, записанным в файле _main.config
				# если параметр есть в словаре self.config, то записываем этот параметр с его значением в файл
				for line in lines:
					p = line.split('=')
					
					if len(p) == 2 and p[0].strip() in cfg.keys():
						# print(str(p[0].strip()) + '=' + str(p[1].strip()) + '\n')
						configfile.write(str(p[0].strip()) + '=' + str(cfg.get(p[0])) + '\n')
						cfg.pop(p[0].strip(), 0)

					else:
						configfile.write(line)

				# записываем оставшиеся в словаре пары
				while len(cfg):
					p = cfg.popitem()
					configfile.write(str(p[0]) + '=' + str(p[1]) + '\n')
	  
		except Exception as E:
			print('error in func _ui.save(): ', file=sys.stderr, end='')
			print(E, file=sys.stderr)  


	def checkout_config(self):
		try:
			# собираем параметры
			self.config = {
				'signal_type': int(self.cbSignalType.current()),
				'freq':      int(self.editFrequency.get()),	
				'sampling':  int(self.editSampling.get()),
				'amplitude': int(self.editAmplitude.get()),
				'duration':  int(self.editDuration.get()),
				'fadein':    int(self.editFadeIn.get()),
				'fadeout':   int(self.editFadeOut.get()),
				'freq_min':   int(self.editFreqMin.get()),
				'freq_max':   int(self.editFreqMax.get()),
				'filtrate':            bool(self.filtrate.get()),
				# 'edit_spectrum_form':  bool(self.edit_spectrum_form.get()),
				'apply_spectrum_form': bool(self.apply_spectrum_form.get()),
				'channel_count':    int(self.editChannelCount.get()),
				'saw_count_per_point':      int(self.editSawpp.get()),
				'zero_smooth':  int(self.editZeroSmooth.get()),
				'channel_gap': int(self.editChannelGap.get()),
				'send':       bool(self.send.get()),
				'host':       self.editHost.get(),
				'port':       int(self.editPort.get()),
				'mode': 	  int(self.cbMode.current()),
				'plot_signal':            bool(self.plot_signal.get()),
				'plot_filtered_signal':   bool(self.plot_filtered_signal.get()),
				'plot_signal_spectrum':   bool(self.plot_signal_spectrum.get()),
				'plot_filtered_spectrum': bool(self.plot_filtered_spectrum.get()),
				'plot_shim':              bool(self.plot_shim.get()),
				'plot_signal_saw':        bool(self.plot_signal_saw.get()),
				'plot_from_point':          int(self.editPlotFromPoint.get()),
				'plot_to_point':            int(self.editPlotToPoint.get()),
				'workdir':                self.editWorkDir.get(),
				'filename_template':      self.editFilenameTemplate.get()
			}

			return self.config

		except Exception as E:
			print('error in func _ui.checkout_config(): ', file=sys.stderr, end='')
			print(E, file=sys.stderr)
			return None



def do(config):
	# >> проверяем, что заданы путь и шаблон имен файлов 
	try:
		if not ('workdir' in config or 'filename_template' in config):
			raise Exception('_main.config must contains params "filename_template" and "workdir" specifing path and names of created files\nexample: filename_template = home/user/  workdir=test_main')
	  
		filename_template = config['workdir']
		if len(filename_template) == 0:
			raise Exception("Path not found")

		if filename_template[-1] != '/': filename_template += '/'
		filename_template += config['filename_template']  # "d:/c++/AME/Generators/test_main" # добавляем разные расширения

	except Exception as E:
		print(E, file=sys.stderr)
		sys.exit(1)

	# << #

	# имена файлов
	filename_raw = filename_template + '.raw'
	filename_flt = filename_template + '.rawf'
	filename_shim = filename_template + '.shim'
	filename_spectrum = filename_template + '.spectrum'

	# генератор  s_type_noise | s_type_sinus | s_type_sinus_noise | s_type_sinus_sinus_noise
	signal_type = get_cfg_param(config, 'signal_type', gen.s_type_noise, 'i')
	freq = get_cfg_param(config, 'freq', 1000, 'i')
	sampling = get_cfg_param(config, 'sampling', 100000, 'i')
	duration = get_cfg_param(config, 'duration', 1000, 'i')
	amplitude = get_cfg_param(config, 'amplitude', 1024, 'i')
	fadein = get_cfg_param(config, 'fadein', 0, 'i')
	fadeout = get_cfg_param(config, 'fadeout', 0, 'i')
	  
	# фильтр
	filtrate = get_cfg_param(config, 'filtrate', True, 'b') and (signal_type != gen.s_type_sinus)
	freq_min = get_cfg_param(config, 'freq_min', 1000, 'i')
	freq_max = get_cfg_param(config, 'freq_max', 4000, 'i')
	edit_spectrum_form = get_cfg_param(config, 'edit_spectrum_form', False, 'b') and (signal_type != gen.s_type_sinus)
	apply_spectrum_form = get_cfg_param(config, 'apply_spectrum_form', False, 'b') and (signal_type != gen.s_type_sinus)
	 
	 
	# преобразование ШИМ
	channel_count = get_cfg_param(config, 'channel_count', 2, 'i')
	saw_count_per_point = get_cfg_param(config, 'saw_count_per_point', 1, 'i')
	zero_smooth = get_cfg_param(config, 'zero_smooth', 0, 'i')
	channel_gap = get_cfg_param(config, 'channel_gap', 0, 'i')
	 
	# загрузка по сети
	send = get_cfg_param(config, 'send', True, 'b')
	host = get_cfg_param(config, 'host', '172.16.4.55')
	port = get_cfg_param(config, 'port', 35580, 'i')
	mode = get_cfg_param(config, 'mode', sock.e_mode_loop, 'i')
	
	# отрисовка
	plot_from_point = get_cfg_param(config, 'plot_from_point', 1, 'i')
	plot_to_point = get_cfg_param(config, 'plot_to_point', 1000, 'i')
	plot_signal = get_cfg_param(config, 'plot_signal', True, 'b')
	plot_signal_spectrum = get_cfg_param(config, 'plot_signal_spectrum', True, 'b')
	plot_filtered_signal = get_cfg_param(config, 'plot_filtered_signal', True, 'b')
	plot_filtered_spectrum = get_cfg_param(config, 'plot_filtered_spectrum', True, 'b')
	plot_shim = get_cfg_param(config, 'plot_shim', True, 'b')
	plot_signal_saw = get_cfg_param(config, 'plot_signal_saw', False, 'b')
	 
	#####################################################
	#####################################################
	 
	SEND_STOP = 0
	 
	MAKE_SHIM = bool(1)
	 
	PLOT_SIGNAL = int(plot_signal)
	PLOT_FILTERED = int(plot_filtered_signal) & (int(filtrate) | int(apply_spectrum_form))
	PLOT_SIGNAL_SPECTRUM = int(plot_signal_spectrum)
	PLOT_FILTERED_SPECTRUM = int(plot_filtered_spectrum) & (int(filtrate) | int(apply_spectrum_form))
	PLOT_SHIM = int(plot_shim) and MAKE_SHIM
	PLOT_SIGNAL_SAW = int(plot_signal_saw)
	
	FLAGS = PLOT_SIGNAL | (PLOT_FILTERED << 1) | (PLOT_SIGNAL_SPECTRUM << 2) | (PLOT_FILTERED_SPECTRUM << 3) | (PLOT_SHIM << 4) | (PLOT_SIGNAL_SAW << 5)
	
	# hellooo
	READ_WAV = 0
	
	SEND = send
	PLOT = bool(1) and bool(FLAGS)
	
	#####################################################
	#####################################################
	 
	if SEND_STOP:
		sock.sendSTOP(host, port)
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


	if edit_spectrum_form:
		spectrum.edit_spectrum(s=sampling, d=duration,
						   signal_data=araw,
						   sffn=filename_spectrum,
						   band_pass=filtrate,
						   fmin=freq_min, fmax=freq_max)
	 
	# sys.exit(0)

	arawf = spectrum.apply_spectrum(s=sampling, d=duration,
								   signal_data=araw,
								   rawf=filename_flt,
								   apply_spectrum_form=apply_spectrum_form,
								   sffn=filename_spectrum,
								   band_pass_filter=filtrate,
								   fmin=freq_min, fmax=freq_max)

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
					data=arawf):
					# fmin=freq_min,
					# fmax=freq_max,
					# falg=filter_algorithm,
					# ftype=filter_type,
					# rp=filter_rp,
					# rs=filter_rs,
					# tb=transition_band,
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
				a=amplitude,
				p1=plot_from_point,
				p2=plot_to_point,
				flags=FLAGS)


def showWindow(version):
	window = tk.Tk()
	window.title("Генератор ШИМ v.{}".format(version))
	# window.geometry("200x200")
	
	frame = mainFrame(window)
	window.grid()
	window.mainloop()
	# print(frame.config)
	# window.close()


def get_cfg_param(config, param_name, default, type='s'):
	try:
		if type == 'i':
			if param_name in config: return int(config[param_name])
			else: return default
		elif type == 'b':
			# if param_name == 'send': print(str(config[param_name]).lower())
			if param_name in config:
				return str(config[param_name]).lower() in ['1', 'yes', 'y', 'true', 't']
			else: return default
		else:
			if param_name in config: return config[param_name]
			else: return default
	except Exception as E:
		print('error in func _exec_main.get_cfg_param(): ', file=sys.stderr, end='')
		print(E)
		return None
