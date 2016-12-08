import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import *
import time
import numpy as np
import array as arr

from _defs import *

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

			with open('_main.config', 'r', encoding="utf8") as configfile:
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
				# print(self.config)

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
		self.cbSignalType = ttk.Combobox(self.frameSignal, width=13, values=['Шум', 'Синус', 'Меандр', 'Пакет синусов', 'Синус+Синус+Шум', 'ЛЧМ', 'Пакет меандров', 'Из спектра'])
		self.cbSignalType.grid(row=0, column=1, sticky=tk.W)
		self.cbSignalType.current(newindex=get_cfg_param(self.config, c_signal_type, 0, 'i'))
	
		# частота начальная
		self.lblFrequency0 = tk.Label(self.frameSignal, text='Частота начальная', width=25)
		self.lblFrequency0.grid(row=1, column=0, sticky=tk.E)
		self.editFrequency0 = tk.Entry(self.frameSignal, width=16)
		self.editFrequency0.grid(row=1, column=1, sticky=tk.W)
		self.editFrequency0.insert(0, get_cfg_param(self.config, c_freq0, '8000'))

		# частота конечная
		self.lblFrequency1 = tk.Label(self.frameSignal, text='Частота конечная', width=25)
		self.lblFrequency1.grid(row=2, column=0, sticky=tk.E)
		self.editFrequency1 = tk.Entry(self.frameSignal, width=16)
		self.editFrequency1.grid(row=2, column=1, sticky=tk.W)
		self.editFrequency1.insert(0, get_cfg_param(self.config, c_freq1, '8000'))


		# дискретизация
		self.lblSampling = tk.Label(self.frameSignal, text='Дискретизация', width=25)
		self.lblSampling.grid(row=3, column=0, sticky=tk.E)
		self.editSampling = tk.Entry(self.frameSignal, width=16)
		self.editSampling.grid(row=3, column=1, sticky=tk.W)
		self.editSampling.insert(0, get_cfg_param(self.config, c_sampling, '100000'))


		# длительность (мс.)
		self.lblDuration = tk.Label(self.frameSignal, text='Общая длительность (мс)', width=25)
		self.lblDuration.grid(row=4, column=0, sticky=tk.E)
		self.editDuration = tk.Entry(self.frameSignal, width=16)
		self.editDuration.grid(row=4, column=1, sticky=tk.W)
		self.editDuration.insert(0, get_cfg_param(self.config, c_duration, '1000'))

		# длительность тишины (мс.)
		self.lblHush = tk.Label(self.frameSignal, text='Длительность тишины (мс)', width=25)
		self.lblHush.grid(row=5, column=0, sticky=tk.E)
		self.editHush = tk.Entry(self.frameSignal, width=16)
		self.editHush.grid(row=5, column=1, sticky=tk.W)
		self.editHush.insert(0, get_cfg_param(self.config, c_hush, '0'))

		# амплитуда
		self.lblAmplitude = tk.Label(self.frameSignal, text='Амплитуда', width=25)
		self.lblAmplitude.grid(row=6, column=0, sticky=tk.E)
		self.editAmplitude = tk.Entry(self.frameSignal, width=16)
		self.editAmplitude.grid(row=6, column=1, sticky=tk.W)
		self.editAmplitude.insert(0, get_cfg_param(self.config, c_amplitude, '1024'))

		# раскачка сигнала
		self.lblFadeIn = tk.Label(self.frameSignal, text='Раскачка (%)', width=25)
		self.lblFadeIn.grid(row=7, column=0, sticky=tk.E)
		self.editFadeIn = tk.Entry(self.frameSignal, width=16)
		self.editFadeIn.grid(row=7, column=1, sticky=tk.W)
		self.editFadeIn.insert(0, get_cfg_param(self.config, c_fadein, '0'))

		# затухание сигнала
		lblFadeOut = tk.Label(self.frameSignal, text='Затухание (%)', width=25).grid(row=8, column=0, sticky=tk.E)
		self.editFadeOut = tk.Entry(self.frameSignal, width=16)
		self.editFadeOut.grid(row=8, column=1, sticky=tk.W)
		self.editFadeOut.insert(0, get_cfg_param(self.config, c_fadeout, '0'))


	### <- параметры сигнала ###	

	## -> постобработка

		self.framePostprocessing = tk.LabelFrame(self, text='Постобработка сигнала')
		self.framePostprocessing.grid(row=1, column=0, sticky=tk.N, rowspan=1)

		# метод наложения
		self.lblSignalWindowMethod = tk.Label(self.framePostprocessing, text='Способ наложения', width=25).grid(row=1, column=0, sticky=tk.E)
		self.cbSignalWindowMethod = ttk.Combobox(self.framePostprocessing, width=13, values=['Нет окна', 'Поверх сигнала', 'Добавить шум', 'Обрезать'])
		self.cbSignalWindowMethod.grid(row=0, column=1, sticky=tk.W)
		self.cbSignalWindowMethod.current(newindex=get_cfg_param(self.config, c_signal_window_method, 0, 'i'))

		# тип окна
		self.lblSignalWindowType = tk.Label(self.framePostprocessing, text='Тип окна', width=25).grid(row=0, column=0, sticky=tk.E)
		self.cbSignalWindowType = ttk.Combobox(self.framePostprocessing, width=13, values=['Трапеция', 'Cosinus', 'S-образное'])
		self.cbSignalWindowType.grid(row=1, column=1, sticky=tk.W)
		self.cbSignalWindowType.current(newindex=get_cfg_param(self.config, c_signal_window_type, 0, 'i'))

		# куда накладывать
		self.lblSignalWindowPlace = tk.Label(self.framePostprocessing, text='Место наложения', width=25).grid(row=2, column=0, sticky=tk.E)
		self.cbSignalWindowPlace = ttk.Combobox(self.framePostprocessing, width=13, values=['Начало и конец каждой пачки', 'Начало каждой пачки', 'Конец каждой пачки', 'Начало и конец сигнала', 'Начало сигнала', 'Конец сигнала'])
		self.cbSignalWindowPlace.grid(row=2, column=1, sticky=tk.W)
		self.cbSignalWindowPlace.current(newindex=get_cfg_param(self.config, c_signal_window_place, 0, 'i'))

		# длительность окна
		lblWindowDuration = tk.Label(self.framePostprocessing, text='Длительность окна, мс.', width=25).grid(row=3, column=0, sticky=tk.E)
		self.editWindowDuration = tk.Entry(self.framePostprocessing, width=16)
		self.editWindowDuration.grid(row=3, column=1, sticky=tk.W)
		self.editWindowDuration.insert(0, get_cfg_param(self.config, c_signal_window_duration, '1'))	


		# self.frameCycleSignal = tk.LabelFrame(self.framePostprocessing, text='Повтор сигнала')
		# self.frameCycleSignal.grid(row=1, column=0, sticky=tk.W, columnspan=2)

		# количество повторений сгенерированного сигнала
		lblCyclesCount = tk.Label(self.framePostprocessing, text='Повторить сигнал, раз', width=25).grid(row=4, column=0, sticky=tk.E)
		self.editRepeatCount = tk.Entry(self.framePostprocessing, width=16)
		self.editRepeatCount.grid(row=4, column=1, sticky=tk.W)
		self.editRepeatCount.insert(0, get_cfg_param(self.config, c_repeat_count, '1'))	

		# пауза после всех повторов
		lblPause = tk.Label(self.framePostprocessing, text='Пауза после (мс.)', width=25).grid(row=5, column=0, sticky=tk.E)
		self.editPause = tk.Entry(self.framePostprocessing, width=16)
		self.editPause.grid(row=5, column=1, sticky=tk.W)
		self.editPause.insert(0, get_cfg_param(self.config, c_pause, '0'))	

	## <- постобработка

	## -> фильтрация ##

		self.frameFilter = tk.LabelFrame(self, text='Фильтрация')
		self.frameFilter.grid(row=0, column=1, sticky=tk.W, rowspan=2)

		self.filtrate = BooleanVar()
		self.checkFilter = tk.Checkbutton(self.frameFilter, text='Применить полосовой фильтр', variable=self.filtrate)
		self.checkFilter.grid(row=0, column=0, sticky=tk.W, columnspan=2)
		self.filtrate.set(get_cfg_param(self.config, c_filtrate, True, 'b'))
		# else: self.filtrate.set(False)

		# минимальная частота
		self.lblFilterFreqMin = tk.Label(self.frameFilter, text='Мин. частота', width=25)
		self.lblFilterFreqMin.grid(row=1, column=0, sticky=tk.E)
		self.editFilterFreqMin = tk.Entry(self.frameFilter, width=16)
		self.editFilterFreqMin.grid(row=1, column=1, sticky=tk.W)
		self.editFilterFreqMin.insert(0, get_cfg_param(self.config, c_filter_freq_min, '1000'))

		# максимальная частота
		self.lblFilterFreqMax = tk.Label(self.frameFilter, text='Макс. частота', width=25)
		self.lblFilterFreqMax.grid(row=2, column=0, sticky=tk.E)
		self.editFilterFreqMax = tk.Entry(self.frameFilter, width=16)
		self.editFilterFreqMax.grid(row=2, column=1, sticky=tk.W)
		self.editFilterFreqMax.insert(0, get_cfg_param(self.config, c_filter_freq_max, '4000'))
		
		# редактировать форму спектра
		# self.edit_spectrum_form = BooleanVar()
		# self.checkEditSpectrumForm = tk.Checkbutton(self.frameFilter, text='Редактировать форму спектра', variable=self.edit_spectrum_form)
		# self.checkEditSpectrumForm.grid(row=3, column=0, sticky=tk.W, columnspan=2)
		# self.edit_spectrum_form.set(get_cfg_param(self.config, 'edit_spectrum_form', False, 'b'))


		# # применить форму спектра
		self.apply_spectrum_form = BooleanVar()
		self.checkApplySpectrumForm = tk.Checkbutton(self.frameFilter, text='Применить заданную форму спектра', variable=self.apply_spectrum_form)
		self.checkApplySpectrumForm.grid(row=4, column=0, sticky=tk.W, columnspan=2)
		self.apply_spectrum_form.set(get_cfg_param(self.config, c_apply_spectrum_form, False, 'b'))

		# подгонять значения точно заданной форме
		self.apply_accurately_to_form = BooleanVar()
		self.checkApplyFccuratelyToForm = tk.Checkbutton(self.frameFilter, text='Точно по форме', variable=self.apply_accurately_to_form)
		self.checkApplyFccuratelyToForm.grid(row=5, column=0, sticky=tk.W, columnspan=2)
		self.apply_accurately_to_form.set(get_cfg_param(self.config, c_apply_accurately_to_form, False, 'b'))


		# редактор формы спектра
		self.frameSpectrumFormEditor = tk.LabelFrame(self.frameFilter, text='Редактор формы спектра')
		self.frameSpectrumFormEditor.grid(row=6, column=0, sticky=tk.W, columnspan=4 )

		# новая форма спектра
		self.bnCreateSpectrumForm = tk.Button(self.frameSpectrumFormEditor, text='Новая форма', command=self.create_spectrum)
		self.bnCreateSpectrumForm.grid(row=0, column=0, sticky=tk.W) #, columnspan=2)

		# редактор
		self.bnEditSpectrumForm = tk.Button(self.frameSpectrumFormEditor, text='Редактировать', command=self.edit_spectrum)
		self.bnEditSpectrumForm.grid(row=0, column=1, sticky=tk.E) #, columnspan=2)

	## <- фильтрация ##

	## -> преобразование шим ##

		self.frameShim = tk.LabelFrame(self, text='Преобразование ШИМ')
		self.frameShim.grid(row=2, column=0, sticky=tk.N, rowspan=1)

		# кол-во каналов
		self.lblChannelCount = tk.Label(self.frameShim, text='Кол-во каналов', width=25).grid(row=0, column=0, sticky=tk.E)
		self.editChannelCount = tk.Entry(self.frameShim, width=16)
		self.editChannelCount.grid(row=0, column=1, sticky=tk.W)
		self.editChannelCount.insert(0, get_cfg_param(self.config, c_channel_count, '2'))
		
		# пил на точку
		self.lblSawpp = tk.Label(self.frameShim, text='Пил на точку', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editSawpp = tk.Entry(self.frameShim, width=16)
		self.editSawpp.grid(row=1, column=1, sticky=tk.W)
		self.editSawpp.insert(0, get_cfg_param(self.config, c_saw_count_per_point, '1'))
		
		# размытие нуля
		self.lblZeroSmooth = tk.Label(self.frameShim, text='Размытие нуля (%)', width=25).grid(row=2, column=0, sticky=tk.E)
		self.editZeroSmooth = tk.Entry(self.frameShim, width=16)
		self.editZeroSmooth.grid(row=2, column=1, sticky=tk.W)
		self.editZeroSmooth.insert(0, get_cfg_param(self.config, c_zero_smooth, '0'))

		# разрыв между каналами
		self.lblChannelGap = tk.Label(self.frameShim, text='Разрыв между каналами (%)', width=25).grid(row=3, column=0, sticky=tk.E)
		self.editChannelGap = tk.Entry(self.frameShim, width=16)
		self.editChannelGap.grid(row=3, column=1, sticky=tk.W)
		self.editChannelGap.insert(0, get_cfg_param(self.config, c_channel_gap, '0'))

	## <- преобразование шим ##

	## -> выгрузка на устройство ##

		self.frameSend = tk.LabelFrame(self, text='Выгрузка')
		self.frameSend.grid(row=2, column=1, sticky=tk.N)

		self.send = BooleanVar()
		self.checkSend = tk.Checkbutton(self.frameSend, text='Выгрузить сигнал на устройство', variable=self.send)
		self.checkSend.grid(row=0, column=0, sticky=tk.E, columnspan=2)
		self.send.set(get_cfg_param(self.config, c_send, True, 'b'))

		# host
		self.lblHost = tk.Label(self.frameSend, text='IP', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editHost = tk.Entry(self.frameSend, width=16)
		self.editHost.grid(row=1, column=1, sticky=tk.W)
		self.editHost.insert(0, get_cfg_param(self.config, c_host, '172.16.4.55'))
		
		# port
		self.lblPort = tk.Label(self.frameSend, text='Порт', width=25).grid(row=2, column=0, sticky=tk.E)
		self.editPort = tk.Entry(self.frameSend, width=16)
		self.editPort.grid(row=2, column=1, sticky=tk.W)
		self.editPort.insert(0, get_cfg_param(self.config, c_port, '35580'))
		
		# режим работы: ONE или LOOP
		self.lblMode = tk.Label(self.frameSend, text='Режим работы', width=25).grid(row=3, column=0, sticky=tk.E)
		self.cbMode = ttk.Combobox(self.frameSend, width=13, values=['ONE', 'LOOP'])
		self.cbMode.grid(row=3, column=1, sticky=tk.W)
		self.cbMode.current(newindex=get_cfg_param(self.config, c_mode, 1))

		# send STOP
		self.bnSendStop = tk.Button(self.frameSend, text='Отправить STOP', command=self.send_stop)
		self.bnSendStop.grid(row=4, column=0, sticky=tk.E, columnspan=2)

		# выгрузить файл
		self.bnSendFile = tk.Button(self.frameSend, text='Выгрузить файл', command=self.send_file)
		self.bnSendFile.grid(row=5, column=0, sticky=tk.E, columnspan=2)

	## <- выгрузка на устройство ##


	## -> отрисовка ##

		self.framePlot = tk.LabelFrame(self, text='Отрисовка')
		self.framePlot.grid(row=3, column=0, sticky=tk.W, columnspan=3)

		# отобразить сигнал
		self.plot_signal = BooleanVar()
		self.checkPlotSignal = tk.Checkbutton(self.framePlot, text='Сигнал', variable=self.plot_signal)
		self.checkPlotSignal.grid(row=0, column=0, sticky=tk.W, columnspan=4)
		self.plot_signal.set(get_cfg_param(self.config, c_plot_signal, True, 'b'))

		# отобразить спектр сигнала
		self.plot_signal_spectrum = BooleanVar()
		self.checkSignalSpectrum = tk.Checkbutton(self.framePlot, text='Спектр сигнала', variable=self.plot_signal_spectrum)
		self.checkSignalSpectrum.grid(row=0, column=1, sticky=tk.W, columnspan=4)
		self.plot_signal_spectrum.set(get_cfg_param(self.config, c_plot_signal_spectrum, True, 'b'))
		
		# отобразить отфильтрованный сигнал
		self.plot_filtered_signal = BooleanVar()
		self.checkPlotFiltered = tk.Checkbutton(self.framePlot, text='Отфильтрованный сигнал', variable=self.plot_filtered_signal)
		self.checkPlotFiltered.grid(row=1, column=0, sticky=tk.W, columnspan=4)
		self.plot_filtered_signal.set(get_cfg_param(self.config, c_plot_filtered_signal, True, 'b'))
	
		# отобразить спектр отфильтрованного сигнала
		self.plot_filtered_spectrum = BooleanVar()
		self.checkPlotFilteredSignalSpectrum = tk.Checkbutton(self.framePlot, text='Спектр отфильтрованного сигнала', variable=self.plot_filtered_spectrum)
		self.checkPlotFilteredSignalSpectrum.grid(row=1, column=1, sticky=tk.W, columnspan=4)
		self.plot_filtered_spectrum.set(get_cfg_param(self.config, c_plot_filtered_spectrum, True, 'b'))

		# отобразить ШИМ
		self.plot_shim = BooleanVar()
		self.checkPlotShim = tk.Checkbutton(self.framePlot, text='ШИМ', variable=self.plot_shim)
		self.checkPlotShim.grid(row=2, column=0, sticky=tk.W, columnspan=4)
		self.plot_shim.set(get_cfg_param(self.config, c_plot_shim, True, 'b'))
		
		# отобразить сигнал + пила
		self.plot_signal_saw = BooleanVar()
		self.checkSignalSaw = tk.Checkbutton(self.framePlot, text='Сигнал + Пила', variable=self.plot_signal_saw)
		self.checkSignalSaw.grid(row=2, column=1, sticky=tk.W, columnspan=4)
		self.plot_signal_saw.set(get_cfg_param(self.config, c_plot_signal_saw, False, 'b'))

		# сигнал с точки .. по ..
		lblPlotFromPoint = tk.Label(self.framePlot, text='Показать точки с', width=25).grid(row=3, column=0, sticky=tk.E)
		self.editPlotFromPoint = tk.Entry(self.framePlot, width=5)
		self.editPlotFromPoint.grid(row=3, column=1, sticky=tk.W)
		self.editPlotFromPoint.insert(0, get_cfg_param(self.config, c_plot_from_point, '1'))
		
		lblPlotToPoint = tk.Label(self.framePlot, text=' по ', width=4).grid(row=3, column=2, sticky=tk.E)
		self.editPlotToPoint = tk.Entry(self.framePlot, width=53)
		self.editPlotToPoint.grid(row=3, column=3, sticky=tk.W)
		self.editPlotToPoint.insert(0, get_cfg_param(self.config, c_plot_to_point, '1000'))

	## <- отрисовка ##

	## -> общее ##
	
		self.frameGen = tk.LabelFrame(self, text='Общее')
		self.frameGen.grid(row=5, column=0, sticky=tk.W, columnspan=2)

		# рабочий каталог
		lblWorkDir = tk.Label(self.frameGen, text='Рабочий каталог', width=25).grid(row=0, column=0, sticky=tk.E)
		self.editWorkDir = tk.Entry(self.frameGen, width=65)
		self.editWorkDir.grid(row=0, column=1, sticky=tk.W)
		self.editWorkDir.insert(0, get_cfg_param(self.config, c_workdir, ''))
		
		# шаблон имен файлов
		lblFilenameTemplate = tk.Label(self.frameGen, text='Шаблон имен файлов', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editFilenameTemplate = tk.Entry(self.frameGen, width=65)
		self.editFilenameTemplate.grid(row=1, column=1, sticky=tk.W)
		self.editFilenameTemplate.insert(0, get_cfg_param(self.config, c_filename_template, ''))
		
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

		# редактор параметров
		self.bnEditSignalParams = tk.Button(self.frameButtons, text='Редактировать параметры', width=80, command=self.edit_signal_params)
		self.bnEditSignalParams.grid(row=4, column=0, sticky=tk.E, columnspan=2)

	## <- кнопки ##

	# def get_cfg(self, param_name, default):
	# 	if param_name in self.config: return self.config[param_name]
	# 	else: return default

	def send_file(self):
		try:
			
			filename = filedialog.askopenfilename(defaultextension='shim', initialdir=self.config[c_workdir], multiple=False, filetypes=[('shim files', '.shim'), ('all files', '.*')])
			
			if filename:
				sock.send(self.config, fname=filename)

		except Exception as E:
			sys.stderror.write(E)


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

			fn = self.config[c_workdir]
			if len(fn) == 0:
				raise Exception('Path not found')

			if fn[-1] != '/': fn += '/'
			fn += self.config[c_filename_template]

			with open(fn + '.spectrum', 'w') as f:
				pass

			spectrum.edit_spectrum(self.config)

		except Exception as E:
			print(E, file=sys.stderr)			


	def edit_spectrum(self):
		try:
			if self.checkout_config() is None: return

			fn = self.config[c_workdir]
			if len(fn) == 0:
				raise Exception('Path not found')

			if fn[-1] != '/': fn += '/'
			fn += self.config[c_filename_template]

			spectrum.edit_spectrum(self.config)

		except Exception as E:
			print(E, file=sys.stderr)	


	def edit_signal_params(self):
		try:
			with open('_main.config', 'r', encoding="utf8") as configfile:
				lines = configfile.readlines()

				# разбираем параметры записанные в файле _main.config
				lst=[]
				for line in lines: # если строка начинается не с буквы, то эту строку пропускаем
					if line[0] in ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']:
						lst.append(line.split('='))
	  
				for i in range(len(lst)):
					for j in range(len(lst[i])):
						lst[i][j] = lst[i][j].strip()

			param_window = tk.Tk()
			param_window.title('Параметры')
			param_window.geometry("575x400")

			
			frame = Frame(param_window)
			frame.grid()

			frameParams = tk.LabelFrame(frame, text='Параметры')
			frameParams.grid(row=0, column=0, sticky=tk.N, columnspan=2)

			text1 = Text(frameParams, height=22, width=70)
			text1.grid(row=0, column=0, columnspan=2)
			# text1.pack()

			bnCancelParams = tk.Button(frame, text='Отмена', width=20, command=self.edit_signal_params)
			bnCancelParams.grid(row=1, column=0, sticky=tk.W)

			bnSaveParams = tk.Button(frame, text='Сохранить', width=20, command=self.edit_signal_params)
			bnSaveParams.grid(row=1, column=1, sticky=tk.E)

			param_window.grid()
			param_window.mainloop()

			text1.insert('0.0', 'lst')
			# self.config = dict(lst)

		except Exception as E:
			print('error on edit config file: ', file=sys.stderr, end='')
			print(E, file=sys.stderr)  


	def start(self):
		try:

			self.save()

			

			do(self.config)
	  
		except Exception as E:
			print('error in func _ui.start(): %s' % E, file=sys.stderr, end='')


	def save(self):

		self.checkout_config()

		cfg = self.config.copy()

		# читаем файл _main.config
		try:

			with open('_main.config', 'r', encoding="utf8") as configfile:
				lines = configfile.readlines()
	  
			with open('_main.config', 'w', encoding="utf8") as configfile:
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
			print('error in func _ui.save(): %s' % E, file=sys.stderr, end='')


	def re_read_params(self, pnames):
 
		# читаем файл _main.config
		try:

			with open('_main.config', 'r', encoding="utf8") as configfile:
				lines = configfile.readlines()

				# разбираем параметры записанные в файле _main.config
				lst=[]
				for line in lines: # если строка начинается не с буквы, то эту строку пропускаем
					if line[0] in ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']:
						lst.append(line.split('='))
				
				for i in range(len(lst)):
					for j in range(len(lst[i])):
						lst[i][j] = lst[i][j].strip()

				_cfg = dict(lst)
				for param in pnames:
					self.config[param] = _cfg[param]

				# print(self.config)

		except Exception as E:
			print('error on reading self.config file: %s' % E, file=sys.stderr)


	def checkout_config(self):
		try:
			cfg = self.config.copy()
			
			# собираем параметры
			self.config = {
				c_signal_type: int(self.cbSignalType.current()),
				c_freq0:      int(self.editFrequency0.get()),	
				c_freq1:      int(self.editFrequency1.get()),	
				c_sampling:  int(self.editSampling.get()),
				c_amplitude: int(self.editAmplitude.get()),
				c_duration:  int(self.editDuration.get()),
				c_hush:      int(self.editHush.get()),
				c_fadein:    int(self.editFadeIn.get()),
				c_fadeout:   int(self.editFadeOut.get()),
				c_repeat_count: 		   int(self.editRepeatCount.get()),
				c_pause: 				   int(self.editPause.get()),
				c_signal_window_type:		int(self.cbSignalWindowType.current()),
				c_signal_window_method:		int(self.cbSignalWindowMethod.current()),
				c_signal_window_place:		int(self.cbSignalWindowPlace.current()),
				c_signal_window_duration:	int(self.editWindowDuration.get()),
				# c_meandr_pulse_width:	   get_cfg_param(cfg, c_meandr_pulse_width, 250, 'i'),
				# c_meandr_interval_width:   get_cfg_param(cfg, c_meandr_interval_width, 100, 'i'),
				# c_meandr_type:  		   get_cfg_param(cfg, c_meandr_type, m_one_channel, 'i'),
				# c_meandr_random_interval:  get_cfg_param(cfg, c_meandr_random_interval, 0, 'i'),
				c_filter_freq_min:   int(self.editFilterFreqMin.get()),
				c_filter_freq_max:   int(self.editFilterFreqMax.get()),
				c_filtrate:            bool(self.filtrate.get()),
				# c_edit_spectrum_form:  bool(self.edit_spectrum_form.get()),
				c_apply_spectrum_form: bool(self.apply_spectrum_form.get()),
				c_apply_accurately_to_form: bool(self.apply_accurately_to_form.get()),
				c_channel_count:    int(self.editChannelCount.get()),
				c_saw_count_per_point:      int(self.editSawpp.get()),
				c_zero_smooth:  int(self.editZeroSmooth.get()),
				c_channel_gap: int(self.editChannelGap.get()),
				c_send:       bool(self.send.get()),
				c_host:       self.editHost.get(),
				c_port:       int(self.editPort.get()),
				c_mode: 	  int(self.cbMode.current()),
				c_plot_signal:            bool(self.plot_signal.get()),
				c_plot_filtered_signal:   bool(self.plot_filtered_signal.get()),
				c_plot_signal_spectrum:   bool(self.plot_signal_spectrum.get()),
				c_plot_filtered_spectrum: bool(self.plot_filtered_spectrum.get()),
				c_plot_shim:              bool(self.plot_shim.get()),
				c_plot_signal_saw:        bool(self.plot_signal_saw.get()),
				c_plot_from_point:          int(self.editPlotFromPoint.get()),
				c_plot_to_point:            int(self.editPlotToPoint.get()),
				c_workdir:                self.editWorkDir.get(),
				c_filename_template:      self.editFilenameTemplate.get()
			}

			self.re_read_params([c_meandr_pulse_width, c_meandr_interval_width, c_meandr_type, c_meandr_random_interval, c_save_log, c_sinus_pack_step, c_meandr_pack_step])

			log_file_name = None
			
			if get_cfg_param(self.config, c_save_log, True, 'b') == True:
				work_dir = self.config[c_workdir]
				if work_dir[-1] != '/': work_dir += '/'
				log_file_name = work_dir + time.strftime('%d_%m_%Y %H_%M_%S') + '.log'

			self.config[c_log_file_name] = log_file_name

			return self.config

		except Exception as E:
			print('error in func _ui.checkout_config(): %s' % E, file=sys.stderr)
			return None



def do(config):
	config[c_cur_date] = time.strftime('%d_%m_%Y')
	config[c_cur_time] = time.strftime('%H_%M_%S')

	# пишем текущую конфигурацию в лог
	if not config[c_log_file_name] is None:
		with open(config[c_log_file_name], 'w') as log_file:
			for key in config.keys():
				log_file.write(key + '=' + str(config[key]) + '\n')

			log_file.write('\n')


	# имена файлов
	filename_raw = get_path(config, 'raw')
	filename_flt = get_path(config, 'rawf')
	filename_shim = get_path(config, 'shim')
	filename_spectrum = get_path(config, 'spectrum')

	#####################################################
	#####################################################
	 
	SEND_STOP = 0
	 
	MAKE_SHIM = bool(1)
	
	filtrate = get_cfg_param(config, c_filtrate, True, 'b') and (signal_type != gen.s_type_sinus) and (signal_type != gen.s_type_lfm)
	apply_spectrum_form = get_cfg_param(config, c_apply_spectrum_form, False, 'b') and (signal_type != gen.s_type_sinus) and (signal_type != gen.s_type_lfm)

	PLOT_SIGNAL = int(get_cfg_param(config, c_plot_signal, True, 'b'))
	PLOT_FILTERED = int(get_cfg_param(config, c_plot_filtered_signal, True, 'b')) & (int(filtrate) | int(apply_spectrum_form))
	PLOT_SIGNAL_SPECTRUM = int(get_cfg_param(config, c_plot_signal_spectrum, True, 'b'))
	PLOT_FILTERED_SPECTRUM = int(get_cfg_param(config, c_plot_filtered_spectrum, True, 'b')) & (int(filtrate) | int(apply_spectrum_form))
	PLOT_SHIM = int(get_cfg_param(config, c_plot_shim, True, 'b')) and MAKE_SHIM
	PLOT_SIGNAL_SAW = int(get_cfg_param(config, c_plot_signal_saw, False, 'b'))
	
	FLAGS = PLOT_SIGNAL | (PLOT_FILTERED << 1) | (PLOT_SIGNAL_SPECTRUM << 2) | (PLOT_FILTERED_SPECTRUM << 3) | (PLOT_SHIM << 4) | (PLOT_SIGNAL_SAW << 5)
	
	# hellooo
	READ_WAV = 0
	
	SEND = get_cfg_param(config, c_send, True, 'b')
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
		araw = gen.generate(config)
		

	# >> перебор интервалов

		# araw = intervals(config)

    # << перебор интервалов

	 
	if araw is None:
		return

	 
	# sys.exit(0)
	if filtrate or apply_spectrum_form:
		arawf = spectrum.apply_spectrum(config, signal_data=araw)

	else:
		arawf = araw

	if arawf is None:
		return

	 
	if MAKE_SHIM:
		if not shim.shim(config, data=arawf):
			return


	if SEND:
		sock.send(config)

	 
	if PLOT:
		plot.plot(config, flags=FLAGS)



def showWindow(version):
	window = tk.Tk()
	window.title("Генератор ШИМ v.{}".format(version))
	# window.geometry("200x200")
	
	frame = mainFrame(window)
	window.grid()
	window.mainloop()
	# print(frame.config)
	# window.close()


def intervals(config):
	araw = arr.array('d')
	dur = 0
	i = 1

	try:
		int_file = get_path(config, 'txt')
		with open(int_file, 'w') as ifile:

			ifile.write(int_file + '\n\n')
			
			for low_int in np.arange(200, 260, 10): # 5 кГц - 4 кГц
				
				config[c_meandr_interval_width] = low_int
				
				for high_int in np.arange(500, 1050, 50): # 2 кГц - 1 кГц
					
					config[c_meandr_random_interval] = high_int
					
					a = gen.generate(config)
					
					araw.extend(a)
					
					dur += config[c_duration]
					ifile.write('%i\timp=%s\tint0=%i\tint1=%i\n' % (i, config[c_meandr_pulse_width], low_int, high_int))
					i += 1
	
			ifile.write('\nduration=%i\n' % dur)
			config[c_duration] = dur

		
		with open(get_path(config, 'raw'), 'wb') as f:
			araw.tofile(f)

		print('полный файл записан ok')

		return araw

	except Exception as E:
		print('ошибка при переборе интервалов: %s' % E, file=sys.stderr)
		return None
