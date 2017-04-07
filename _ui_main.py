import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import *
import time
from datetime import datetime, date, time
import numpy as np
import array as arr

import shutil

from _defs import *

import _generator_main as gen
import _plot_main as plot
import _shim_main as shim
import _socket_main as sock
import _spectrum_main as spectrum
import _wav as wav
import _matlab as matlab
# from _exec_main import execute
# from _exec_main import get_cfg_param

import matplotlib.pyplot as plt


def showWindow(version):
	window = tk.Tk()
	window.title("Генератор ШИМ v.{}".format(version))
	# window.geometry("200x200")
	
	frame = mainFrame(window)
	window.grid()
	window.mainloop()
	# print(frame.config)
	# window.close()


class mainFrame(Frame):
	def __init__(self, master):
		super(mainFrame, self).__init__(master)
		self.grid() #row=0, column=0, sticky=tk.W)
		
		self.config = {}

		self.showFrame()


	def showFrame(self):
 		
		# создаем виджеты
		self.frameLeft = tk.Frame(self)
		self.frameLeft.grid(row=0, column=0, sticky=tk.W)

		self.frameRight = tk.Frame(self)
		self.frameRight.grid(row=0, column=1, sticky=tk.E)
		
		# self.lblSignalType = tk.Label(self.frameRight, text='Тип сигнала', width=25)
		# self.lblSignalType.grid(row=0, column=0, sticky=tk.E)

	## >> параметры генерации исходного сигнала ##

		self.frameSignal = tk.LabelFrame(self.frameLeft, text='Генератор')
		self.frameSignal.grid(row=0, column=0, sticky=tk.N)

		# тип сигнала
		self.lblSignalType = tk.Label(self.frameSignal, text='Тип сигнала', width=25)
		self.lblSignalType.grid(row=0, column=0, sticky=tk.E)
		self.cbSignalType = ttk.Combobox(self.frameSignal, width=13, values=['Шум', 'Синус', 'Меандр', 'Пакет синусов', 'Синус+Синус+Шум', 'ЛЧМ', 'Пакет меандров', 'Из спектра', 'Ровный спектр', 'Из формы спектра'])
		self.cbSignalType.grid(row=0, column=1, sticky=tk.W)
	
		# частота начальная
		self.lblFrequency0 = tk.Label(self.frameSignal, text='Частота начальная', width=25)
		self.lblFrequency0.grid(row=1, column=0, sticky=tk.E)
		self.editFrequency0 = tk.Entry(self.frameSignal, width=16)
		self.editFrequency0.grid(row=1, column=1, sticky=tk.W)

		# частота конечная
		self.lblFrequency1 = tk.Label(self.frameSignal, text='Частота конечная', width=25)
		self.lblFrequency1.grid(row=2, column=0, sticky=tk.E)
		self.editFrequency1 = tk.Entry(self.frameSignal, width=16)
		self.editFrequency1.grid(row=2, column=1, sticky=tk.W)

		# дискретизация
		self.lblSampling = tk.Label(self.frameSignal, text='Дискретизация', width=25)
		self.lblSampling.grid(row=3, column=0, sticky=tk.E)
		self.editSampling = tk.Entry(self.frameSignal, width=16)
		self.editSampling.grid(row=3, column=1, sticky=tk.W)

		# длительность (мс.)
		self.lblDuration = tk.Label(self.frameSignal, text='Общая длительность (мс)', width=25)
		self.lblDuration.grid(row=4, column=0, sticky=tk.E)
		self.editDuration = tk.Entry(self.frameSignal, width=16)
		self.editDuration.grid(row=4, column=1, sticky=tk.W)

		# длительность тишины (мс.)
		self.lblHush = tk.Label(self.frameSignal, text='Длительность тишины (мс)', width=25)
		self.lblHush.grid(row=5, column=0, sticky=tk.E)
		self.editHush = tk.Entry(self.frameSignal, width=16)
		self.editHush.grid(row=5, column=1, sticky=tk.W)

		# количество повторений сгенерированного сигнала
		lblCyclesCount = tk.Label(self.frameSignal, text='Повторить сигнал, раз', width=25).grid(row=6, column=0, sticky=tk.E)
		self.editRepeatCount = tk.Entry(self.frameSignal, width=16)
		self.editRepeatCount.grid(row=6, column=1, sticky=tk.W)

		# пауза после всех повторов
		lblPause = tk.Label(self.frameSignal, text='Пауза в конце (мс.)', width=25).grid(row=7, column=0, sticky=tk.E)
		self.editPause = tk.Entry(self.frameSignal, width=16)
		self.editPause.grid(row=7, column=1, sticky=tk.W)

		# амплитуда
		self.lblAmplitude = tk.Label(self.frameSignal, text='Амплитуда', width=25)
		self.lblAmplitude.grid(row=8, column=0, sticky=tk.E)
		self.editAmplitude = tk.Entry(self.frameSignal, width=16)
		self.editAmplitude.grid(row=8, column=1, sticky=tk.W)

		# коэффициент уровня сигнала
		self.lblKoeff = tk.Label(self.frameSignal, text='Коэфф. уровня сигнала', width=25)
		self.lblKoeff.grid(row=9, column=0, sticky=tk.E)
		self.editKoeff = tk.Entry(self.frameSignal, width=16)
		self.editKoeff.grid(row=9, column=1, sticky=tk.W)

	## << параметры сигнала

	## >> наложение окна
		self.frameWindow = tk.LabelFrame(self.frameLeft, text='Наложение окна')
		self.frameWindow.grid(row=1, column=0, sticky=tk.N)

		# тип окна
		self.lblSignalWindowType = tk.Label(self.frameWindow, text='Тип окна', width=25).grid(row=0, column=0, sticky=tk.E)
		self.cbSignalWindowType = ttk.Combobox(self.frameWindow, width=13, values=['Нет окна', 'Поверх сигнала', 'Добавить шум', 'Обрезать'])
		self.cbSignalWindowType.grid(row=0, column=1, sticky=tk.W)
		
		# форма окна
		self.lblSignalWindowForm = tk.Label(self.frameWindow, text='Форма окна', width=25).grid(row=1, column=0, sticky=tk.E)
		self.cbSignalWindowForm = ttk.Combobox(self.frameWindow, width=13, values=['Трапеция', 'Cosinus', 'S-образное'])
		self.cbSignalWindowForm.grid(row=1, column=1, sticky=tk.W)

		# куда накладывать
		self.lblSignalWindowPlace = tk.Label(self.frameWindow, text='Место наложения', width=25).grid(row=2, column=0, sticky=tk.E)
		self.cbSignalWindowPlace = ttk.Combobox(self.frameWindow, width=13, values=['Начало и конец каждой пачки', 'Начало каждой пачки', 'Конец каждой пачки', 'Начало и конец сигнала', 'Начало сигнала', 'Конец сигнала'])
		self.cbSignalWindowPlace.grid(row=2, column=1, sticky=tk.W)

		# длительность окна
		lblWindowDuration = tk.Label(self.frameWindow, text='Длительность окна, мс.', width=25).grid(row=3, column=0, sticky=tk.E)
		self.editWindowDuration = tk.Entry(self.frameWindow, width=16)
		self.editWindowDuration.grid(row=3, column=1, sticky=tk.W)
	## << наложение окна

	## >> преобразование шим ##
		self.frameShim = tk.LabelFrame(self.frameLeft, text='Преобразование ШИМ')
		self.frameShim.grid(row=2, column=0, sticky=tk.N)

		# кол-во каналов
		self.lblChannelCount = tk.Label(self.frameShim, text='Кол-во каналов', width=25).grid(row=0, column=0, sticky=tk.E)
		self.editChannelCount = tk.Entry(self.frameShim, width=16)
		self.editChannelCount.grid(row=0, column=1, sticky=tk.W)

		# пил на точку
		self.lblSawpp = tk.Label(self.frameShim, text='Пил на точку', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editSawpp = tk.Entry(self.frameShim, width=16)
		self.editSawpp.grid(row=1, column=1, sticky=tk.W)

		# размытие нуля
		self.lblZeroSmooth = tk.Label(self.frameShim, text='Размытие нуля (%)', width=25).grid(row=2, column=0, sticky=tk.E)
		self.editZeroSmooth = tk.Entry(self.frameShim, width=16)
		self.editZeroSmooth.grid(row=2, column=1, sticky=tk.W)

		# разрыв между каналами
		self.lblChannelGap = tk.Label(self.frameShim, text='Разрыв между каналами (%)', width=25).grid(row=3, column=0, sticky=tk.E)
		self.editChannelGap = tk.Entry(self.frameShim, width=16)
		self.editChannelGap.grid(row=3, column=1, sticky=tk.W)

	## << преобразование шим ##

	## >> редактор формы спектра ##
		self.frameSpectrumFormEditor = tk.LabelFrame(self.frameRight, text='Редактор формы спектра')
		self.frameSpectrumFormEditor.grid(row=0, column=0, sticky=tk.N)

		# имя файла
		lblSpectrumFormFile = tk.Label(self.frameSpectrumFormEditor, text='Файл', width=10).grid(row=0, column=0, sticky=tk.W, columnspan=2)
		self.editSpectrumFormFile = tk.Entry(self.frameSpectrumFormEditor, width=32)
		self.editSpectrumFormFile.grid(row=0, column=1, sticky=tk.W, columnspan=3)

		# выбор файла
		self.bnSelectSpectrumFormFile = tk.Button(self.frameSpectrumFormEditor, text='...', command=self.select_spectrum_form_file)
		self.bnSelectSpectrumFormFile.grid(row=0, column=2, sticky=tk.E, columnspan=2)

		# новая форма спектра
		self.bnCreateSpectrumForm = tk.Button(self.frameSpectrumFormEditor, text='Новая форма', command=self.create_spectrum)
		self.bnCreateSpectrumForm.grid(row=1, column=0, sticky=tk.E)#, columnspan=3)

		# редактор
		self.bnEditSpectrumForm = tk.Button(self.frameSpectrumFormEditor, text='Редактировать', command=self.edit_spectrum)
		self.bnEditSpectrumForm.grid(row=1, column=1, sticky=tk.E, columnspan=3)

		# подгонять значения точно заданной форме
		self.apply_accurately_to_form = BooleanVar()
		self.checkApplyFccuratelyToForm = tk.Checkbutton(self.frameSpectrumFormEditor, text='Точно по форме', variable=self.apply_accurately_to_form)
		self.checkApplyFccuratelyToForm.grid(row=5, column=0, sticky=tk.W, columnspan=2)

	## << редактор формы спектра ##


	## >> фильтрация ##
		self.frameFilter = tk.LabelFrame(self.frameRight, text='Фильтрация')
		self.frameFilter.grid(row=1, column=0, sticky=tk.N)

		self.filtrate = BooleanVar()
		self.checkFilter = tk.Checkbutton(self.frameFilter, text='Применить полосовой фильтр', variable=self.filtrate)
		self.checkFilter.grid(row=0, column=0, sticky=tk.W, columnspan=2)

		# минимальная частота
		self.lblFilterFreqMin = tk.Label(self.frameFilter, text='Мин. частота', width=25)
		self.lblFilterFreqMin.grid(row=1, column=0, sticky=tk.E)
		self.editFilterFreqMin = tk.Entry(self.frameFilter, width=16)
		self.editFilterFreqMin.grid(row=1, column=1, sticky=tk.W)

		# максимальная частота
		self.lblFilterFreqMax = tk.Label(self.frameFilter, text='Макс. частота', width=25)
		self.lblFilterFreqMax.grid(row=2, column=0, sticky=tk.E)
		self.editFilterFreqMax = tk.Entry(self.frameFilter, width=16)
		self.editFilterFreqMax.grid(row=2, column=1, sticky=tk.W)

		# # применить форму спектра
		# self.apply_spectrum_form = BooleanVar()
		# self.checkApplySpectrumForm = tk.Checkbutton(self.frameFilter, text='Применить заданную форму спектра', variable=self.apply_spectrum_form)
		# self.checkApplySpectrumForm.grid(row=4, column=0, sticky=tk.W, columnspan=2)

	## << фильтрация ##

	## >> выгрузка на устройство ##
		self.frameSend = tk.LabelFrame(self.frameRight, text='Работа с устройством')
		self.frameSend.grid(row=2, column=0, sticky=tk.N)

		self.send = BooleanVar()
		self.checkSend = tk.Checkbutton(self.frameSend, text='Выгрузить сигнал на устройство', variable=self.send)
		self.checkSend.grid(row=0, column=0, sticky=tk.E, columnspan=2)

		# host
		self.lblHost = tk.Label(self.frameSend, text='IP', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editHost = tk.Entry(self.frameSend, width=16)
		self.editHost.grid(row=1, column=1, sticky=tk.W)

		# port
		self.lblPort = tk.Label(self.frameSend, text='Порт', width=25).grid(row=2, column=0, sticky=tk.E)
		self.editPort = tk.Entry(self.frameSend, width=16)
		self.editPort.grid(row=2, column=1, sticky=tk.W)

		# режим работы: ONE или LOOP
		self.lblMode = tk.Label(self.frameSend, text='Режим работы', width=25).grid(row=3, column=0, sticky=tk.E)
		self.cbMode = ttk.Combobox(self.frameSend, width=13, values=['ONE', 'LOOP'])
		self.cbMode.grid(row=3, column=1, sticky=tk.W)

		# начать воспроизведение
		self.bnSendStart = tk.Button(self.frameSend, text='Пуск', command=self.send_start)
		self.bnSendStart.grid(row=4, column=0, sticky=tk.W, columnspan=1)

		# send STOP
		self.bnSendStop = tk.Button(self.frameSend, text='Стоп', command=self.send_stop)
		self.bnSendStop.grid(row=4, column=1, sticky=tk.E, columnspan=1)

		# выгрузить файл
		self.bnSendFile = tk.Button(self.frameSend, text='Выгрузить файл', command=self.send_file)
		self.bnSendFile.grid(row=5, column=0, sticky=tk.E, columnspan=1)

	## << выгрузка на устройство ##

	## >> выходные файлы ##
		self.frameOutputFormats = tk.LabelFrame(self.frameRight, text='Выходные файлы')
		self.frameOutputFormats.grid(row=3, column=0, sticky=tk.N)
		
		self.make_shim = BooleanVar()
		self.checkMakeShim = tk.Checkbutton(self.frameOutputFormats, text='ШИМ', variable=self.make_shim, width=18)
		self.checkMakeShim.grid(row=0, column=0, sticky=tk.W, columnspan=2)

		self.make_wav = BooleanVar()
		self.checkMakeWav = tk.Checkbutton(self.frameOutputFormats, text='WAV', variable=self.make_wav, width=18)
		self.checkMakeWav.grid(row=1, column=0, sticky=tk.W, columnspan=1)

		# взять принятый файл
		self.bnReceivedData = tk.Button(self.frameOutputFormats, text='Данные с микрофона', command = self.get_received_data, width=18)
		self.bnReceivedData.grid(row=1, column=1, sticky=tk.W, columnspan=1)

		# self.play_wav = BooleanVar()
		# self.checkPlayWav = tk.Checkbutton(self.frameOutputFormats, text='Проиграть', variable=self.play_wav, width=10)
		# self.checkPlayWav.grid(row=1, column=1, sticky=tk.W, columnspan=2)

		self.make_matlab = BooleanVar()
		self.checkMakeMatlab = tk.Checkbutton(self.frameOutputFormats, text='Matlab', variable=self.make_matlab, width=18)
		self.checkMakeMatlab.grid(row=2, column=0, sticky=tk.W, columnspan=2)

	## << выходные форматы ##


	## >> отрисовка ##
		self.framePlot = tk.LabelFrame(self, text='Отрисовка')
		self.framePlot.grid(row=1, column=0, sticky=tk.W, columnspan=2)

		# отобразить сигнал
		self.plot_signal = BooleanVar()
		self.checkPlotSignal = tk.Checkbutton(self.framePlot, text='Сигнал', variable=self.plot_signal)
		self.checkPlotSignal.grid(row=0, column=0, sticky=tk.W, columnspan=4)

		# отобразить спектр сигнала
		self.plot_signal_spectrum = BooleanVar()
		self.checkSignalSpectrum = tk.Checkbutton(self.framePlot, text='Спектр сигнала', variable=self.plot_signal_spectrum)
		self.checkSignalSpectrum.grid(row=0, column=1, sticky=tk.W, columnspan=4)

		# отобразить отфильтрованный сигнал
		self.plot_filtered_signal = BooleanVar()
		self.checkPlotFiltered = tk.Checkbutton(self.framePlot, text='Отфильтрованный сигнал', variable=self.plot_filtered_signal)
		self.checkPlotFiltered.grid(row=1, column=0, sticky=tk.W, columnspan=4)

		# отобразить спектр отфильтрованного сигнала
		self.plot_filtered_spectrum = BooleanVar()
		self.checkPlotFilteredSignalSpectrum = tk.Checkbutton(self.framePlot, text='Спектр отфильтрованного сигнала', variable=self.plot_filtered_spectrum)
		self.checkPlotFilteredSignalSpectrum.grid(row=1, column=1, sticky=tk.W, columnspan=4)

		# отобразить ШИМ
		self.plot_shim = BooleanVar()
		self.checkPlotShim = tk.Checkbutton(self.framePlot, text='ШИМ', variable=self.plot_shim)
		self.checkPlotShim.grid(row=2, column=0, sticky=tk.W, columnspan=4)

		# отобразить сигнал + пила
		self.plot_signal_saw = BooleanVar()
		self.checkSignalSaw = tk.Checkbutton(self.framePlot, text='Сигнал + Пила', variable=self.plot_signal_saw)
		self.checkSignalSaw.grid(row=2, column=1, sticky=tk.W, columnspan=4)

		# сигнал с точки .. по ..
		lblPlotFromPoint = tk.Label(self.framePlot, text='Показать точки с', width=25).grid(row=3, column=0, sticky=tk.E)
		self.editPlotFromPoint = tk.Entry(self.framePlot, width=5)
		self.editPlotFromPoint.grid(row=3, column=1, sticky=tk.W)

		lblPlotToPoint = tk.Label(self.framePlot, text=' по ', width=4).grid(row=3, column=2, sticky=tk.E)
		self.editPlotToPoint = tk.Entry(self.framePlot, width=53)
		self.editPlotToPoint.grid(row=3, column=3, sticky=tk.W)

	## << отрисовка ##

	## >> общее ##
		self.frameGen = tk.LabelFrame(self, text='Общее')
		self.frameGen.grid(row=2, column=0, sticky=tk.W, columnspan=2)

		# рабочий каталог
		lblWorkDir = tk.Label(self.frameGen, text='Рабочий каталог', width=25).grid(row=0, column=0, sticky=tk.E)
		self.editWorkDir = tk.Entry(self.frameGen, width=65)
		self.editWorkDir.grid(row=0, column=1, sticky=tk.W)

		# шаблон имен файлов
		lblFilenameTemplate = tk.Label(self.frameGen, text='Шаблон имен файлов', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editFilenameTemplate = tk.Entry(self.frameGen, width=65)
		self.editFilenameTemplate.grid(row=1, column=1, sticky=tk.W)

		self.lastFileName = StringVar()
		self.lblLastFile = tk.Label(self.frameGen, textvariable=self.lastFileName, width=25).grid(row=2, column=0, sticky=tk.E, columnspan=2)


	## << общее ##

	## >> кнопки ##
		self.frameButtons = tk.Frame(self)
		self.frameButtons.grid(row=3, column=0, sticky=tk.W, columnspan=2)

		# ПУСК
		self.bnStart = tk.Button(self.frameButtons, text='Начать выполнение', width=80, command = self.start)
		self.bnStart.grid(row=1, column=0, sticky=tk.E, columnspan=2)

		# сохранить
		self.bnSaveConfig = tk.Button(self.frameButtons, text='Сохранить текущие параметры', width=40, command = self.save)
		self.bnSaveConfig.grid(row=3, column=0, sticky=tk.E, columnspan=1)

		# загрузить конфигурацию
		self.bnLoadConfig = tk.Button(self.frameButtons, text='Загрузить конфигурацию', width=40, command = self.load_config)
		self.bnLoadConfig.grid(row=3, column=1, sticky=tk.E, columnspan=1)

		# редактор параметров
		self.bnEditSignalParams = tk.Button(self.frameButtons, text='Редактировать параметры', width=80, command=self.edit_signal_params)
		self.bnEditSignalParams.grid(row=5, column=0, sticky=tk.E, columnspan=2)

	## << кнопки ##
 		
 		# читаем файл _main.config
		self.config = self.read_config_file()			
		# if self.config == {}:
		# 	raise Exception('wrong configuration')
		
		self.set_widget_values()



	def read_config_file(self, **kwargs):
		
		config = {}

		try:
			filename = '_main.config'
			fromlog = 'config_file_name' in kwargs

			if fromlog:
				filename = kwargs['config_file_name']
			
			# если файл отстутствует, то он будет создан. если _main.config уже существует, то он не будет изменен
			with open(filename, 'a', encoding="utf8") as configfile: pass

			lst=[]
			with open(filename, 'r', encoding="utf8") as configfile:
				lines = configfile.readlines()
				
				# разбираем параметры записанные в файле .config или .log
				for line in lines: # если строка начинается не с буквы, то эту строку пропускаем
					if line[0] in ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']:
						key_n_val = line.split('=')
						if len(key_n_val) == 2 and \
							not (key_n_val[0] in [c_cur_time, c_signal_name]) and \
							not (fromlog == True and key_n_val[0] in [c_workdir, c_filename_template, \
																		c_send, c_plot_signal, c_plot_shim, \
																		c_plot_signal_spectrum, c_plot_filtered_signal, \
																		c_plot_filtered_spectrum, c_plot_signal_saw, \
																		c_plot_from_point, c_plot_to_point, \
																		c_make_wav, c_make_shim, c_make_matlab]):
							lst.append(key_n_val)

				for i in range(len(lst)):
					for j in range(len(lst[i])):
						lst[i][j] = lst[i][j].strip()

							
			config = dict(lst)
			# self.config = dict(lst)
			# print(self.config)

		except Exception as E:
			print('error in func mainFrame.read_config_file(): %s' % E, file=sys.stderr, end='')
			
		finally:
			return config


	def set_widget_values(self):
		
	## >> параметры генерации исходного сигнала ##
		self.cbSignalType.current(newindex=get_cfg_param(self.config, c_signal_type, 0, 'i'))
		
		self.editFrequency0.delete(0, END)
		self.editFrequency0.insert(0, get_cfg_param(self.config, c_freq0, '8000'))
		self.editFrequency1.delete(0, END)
		self.editFrequency1.insert(0, get_cfg_param(self.config, c_freq1, '8000'))
		self.editSampling.delete(0, END)
		self.editSampling.insert(0, get_cfg_param(self.config, c_sampling, '100000'))
		self.editDuration.delete(0, END)
		self.editDuration.insert(0, get_cfg_param(self.config, c_duration, '1000'))
		self.editHush.delete(0, END)
		self.editHush.insert(0, get_cfg_param(self.config, c_hush, '0'))
		self.editRepeatCount.delete(0, END)
		self.editRepeatCount.insert(0, get_cfg_param(self.config, c_repeat_count, '1'))	
		self.editPause.delete(0, END)
		self.editPause.insert(0, get_cfg_param(self.config, c_pause, '0'))	
		self.editAmplitude.delete(0, END)
		self.editAmplitude.insert(0, get_cfg_param(self.config, c_amplitude, '65535'))
		self.editKoeff.delete(0, END)
		self.editKoeff.insert(0, get_cfg_param(self.config, c_koeff, '1.0'))
		# self.editAmplitude.configure(state=DISABLED) #, disabledbackground='white', disabledforeground='black')
	## << параметры сигнала ##

	## >> наложение окна
		self.cbSignalWindowType.current(newindex=get_cfg_param(self.config, c_signal_window_type, 0, 'i'))
		self.cbSignalWindowForm.current(newindex=get_cfg_param(self.config, c_signal_window_form, 0, 'i'))
		self.cbSignalWindowPlace.current(newindex=get_cfg_param(self.config, c_signal_window_place, 0, 'i'))
		self.editWindowDuration.delete(0, END)
		self.editWindowDuration.insert(0, get_cfg_param(self.config, c_signal_window_duration, '1'))	
	## << наложение окна

	## >> редактор формы спектра ##
		self.editSpectrumFormFile.delete(0, END)
		self.editSpectrumFormFile.insert(0, get_cfg_param(self.config, c_spectrum_form_file, ''))
	## << редактор формы спектра ##

	## >> преобразование шим ##
		self.editChannelCount.delete(0, END)
		self.editChannelCount.insert(0, get_cfg_param(self.config, c_channel_count, '2'))
		self.editSawpp.delete(0, END)
		self.editSawpp.insert(0, get_cfg_param(self.config, c_saw_count_per_point, '1'))
		self.editZeroSmooth.delete(0, END)
		self.editZeroSmooth.insert(0, get_cfg_param(self.config, c_zero_smooth, '0'))
		self.editChannelGap.delete(0, END)
		self.editChannelGap.insert(0, get_cfg_param(self.config, c_channel_gap, '0'))
	## << преобразование шим ##

	## >> фильтрация ##
		self.filtrate.set(get_cfg_param(self.config, c_filtrate, False, 'b'))
		self.editFilterFreqMin.delete(0, END)
		self.editFilterFreqMin.insert(0, get_cfg_param(self.config, c_filter_freq_min, '1000'))
		self.editFilterFreqMax.delete(0, END)		
		self.editFilterFreqMax.insert(0, get_cfg_param(self.config, c_filter_freq_max, '4000'))
		# self.apply_spectrum_form.set(get_cfg_param(self.config, c_apply_spectrum_form, False, 'b'))
		self.apply_accurately_to_form.set(get_cfg_param(self.config, c_apply_accurately_to_form, False, 'b'))
	## << фильтрация ##

	## >> выгрузка на устройство ##
		self.send.set(get_cfg_param(self.config, c_send, True, 'b'))
		self.editHost.delete(0, END)
		self.editHost.insert(0, get_cfg_param(self.config, c_host, '172.16.4.55'))
		self.editPort.delete(0, END)
		self.editPort.insert(0, get_cfg_param(self.config, c_port, '35580'))
		self.cbMode.current(newindex=get_cfg_param(self.config, c_mode, 1))
	## << выгрузка на устройство ##

	## >> выходные форматы ##
		self.make_shim.set(get_cfg_param(self.config, c_make_shim, True, 'b'))
		self.make_wav.set(get_cfg_param(self.config, c_make_wav, False, 'b'))
		# self.play_wav.set(get_cfg_param(self.config, c_play_wav, False, 'b'))
		self.make_matlab.set(get_cfg_param(self.config, c_make_matlab, True, 'b'))
	## << выходные форматы ##

	## >> отрисовка ##
		self.plot_signal.set(get_cfg_param(self.config, c_plot_signal, True, 'b'))
		self.plot_signal_spectrum.set(get_cfg_param(self.config, c_plot_signal_spectrum, True, 'b'))
		self.plot_filtered_signal.set(get_cfg_param(self.config, c_plot_filtered_signal, False, 'b'))
		self.plot_filtered_spectrum.set(get_cfg_param(self.config, c_plot_filtered_spectrum, False, 'b'))
		self.plot_shim.set(get_cfg_param(self.config, c_plot_shim, False, 'b'))
		self.plot_signal_saw.set(get_cfg_param(self.config, c_plot_signal_saw, False, 'b'))
		self.editPlotFromPoint.delete(0, END)
		self.editPlotFromPoint.insert(0, get_cfg_param(self.config, c_plot_from_point, '1'))
		self.editPlotToPoint.delete(0, END)
		self.editPlotToPoint.insert(0, get_cfg_param(self.config, c_plot_to_point, '1000'))
	## << отрисовка ##

	## >> общее ##
		self.editWorkDir.delete(0, END)
		self.editWorkDir.insert(0, get_cfg_param(self.config, c_workdir, './{DATE}'))
		self.editFilenameTemplate.delete(0, END)
		self.editFilenameTemplate.insert(0, get_cfg_param(self.config, c_filename_template, '{EXT}_{TIME}'))
	## << общее ##


	def send_file(self):
		try:
			
			filename = filedialog.askopenfilename(defaultextension=C_SHIM, initialdir=self.config[c_workdir], multiple=False, filetypes=[('shim files', '.shim'), ('all files', '.*')])
			
			if filename:
				sock.send(self.config, fname=filename)

		except Exception as E:
			print(E, file=sys.stderr)


	def select_spectrum_form_file(self):
		try:
			self.config[c_workdir] = self.editWorkDir.get()
			filename = filedialog.askopenfilename(defaultextension=C_SPECTRUM, initialdir=get_folder_name(self.config, ''), multiple=False, filetypes=[('spectrum files', '.spectrum'), ('all files', '.*')])
			
			if filename:
				self.editSpectrumFormFile.delete(0, END)
				self.editSpectrumFormFile.insert(0, filename)

		except Exception as E:
			print('error in func _ui_main.select_spectrum_form_file(): %s' % E, file=sys.stderr)


	def get_received_data(self):
		try:
			if not c_cur_time in self.config:
				return

			# self.config[c_cur_time] = datetime.now().timetuple()
			self.config[c_workdir] = self.editWorkDir.get()
			
			received_file_path = filedialog.askopenfilename(defaultextension='', initialdir=self.config[c_received_folder] if c_received_folder in self.config else '', multiple=False, filetypes=[('all files', '.*'), ('pcm files', '.pcm'), ('dat files', '.dat')])
			
			if received_file_path :
				_fp = get_folder_name(self.config, C_RECEIVED)
				if not _fp:
					return

				received_file_name = os.path.split(received_file_path)[1]
				
				shutil.copyfile(received_file_path, _fp + received_file_name)

				if bool(self.make_matlab.get()):
					matlab.write_m_file(self.config, received_file_name)
					# matlab_path = get_path(self.config, C_MATLAB)
					# with open(matlab_path, 'r', encoding="utf8") as mfile:
					# 	lines = mfile.readlines()

					# 	for line in lines:
					# 		if line

					

		except Exception as E:
			print('error in func _ui_main.get_received_data(): %s' % E, file=sys.stderr)	
				

	def send_start(self):
		try:
			host = self.editHost.get()
			port = int(self.editPort.get())
			file_name = get_path(self.config, C_SHIM)

			if self.cbMode.current() == sock.e_mode_loop:
				if not sock.sendLOOP(host, port, file_name):
					raise Exception('Не удалось выполнить команду')
    
			elif self.cbMode.current() == sock.e_mode_one:
				if not sock.sendONE(host, port, file_name):
					raise Exception('Не удалось выполнить команду')

		except Exception as E:
			print('error in func _ui_main.send_start(): %s' % E, file=sys.stderr)

	def send_stop(self):
		try:
			h = self.editHost.get()
			p = int(self.editPort.get())
			sock.sendSTOP(h, p)

		except Exception as E:
			print('error in func _ui_main.send_stop(): %s' % E, file=sys.stderr)


	def create_spectrum(self):
		try:
			self.save()
			spectrum.edit_spectrum(self.config, newForm=True)

		except Exception as E:
			print(E, file=sys.stderr)


	def edit_spectrum(self):
		try:
			self.save()
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


	def load_config(self):
		try:
			self.config[c_workdir] = self.editWorkDir.get()
			self.config[c_cur_time] = datetime.now().timetuple()

			filename = filedialog.askopenfilename(defaultextension=C_LOG, initialdir=get_folder_name(self.config, C_LOG), multiple=False, filetypes=[('log files', '.log'), ('config files', '.config'), ('all files', '.*')])
			
			if not filename:
				return

			self.config = self.read_config_file(config_file_name=filename)
			if self.config == {}:
				raise Exception('wrong configuration')

			self.set_widget_values()


		except Exception as E:
			print(E, file=sys.stderr)


	def start(self):
		try:

			self.save()
			do(self.config)

			self.lastFileName.set("Последний файл: %s" % get_path(self.config, '', only_filename=True))
	  
		except Exception as E:
			print('error in func _ui.start(): %s' % E, file=sys.stderr, end='')


	def save(self):

		self.checkout_config()

		cfg = self.config.copy()

		# читаем файл _main.config
		try:

			lines = []
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
				keys = []
				keys.extend(cfg.keys())
				keys.sort()
			
				for key in keys:
					configfile.write(key + '=' + str(cfg[key]) + '\n')

				# while len(cfg):
				# 	p = cfg.popitem()
				# 	configfile.write(str(p[0]) + '=' + str(p[1]) + '\n')
	  
		except Exception as E:
			print('error in func _ui_main.save(): %s' % E, file=sys.stderr, end='')


	def re_read_params(self, params):
 		
		try:
			_cfg = self.read_config_file()

			for param in params:
				self.config[param[0]] = get_cfg_param(_cfg, param[0], param[1]) 

				# print(self.config)

		except Exception as E:
			print('error in func _ui_main.re_read_params(): %s' % E, file=sys.stderr)


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
				# c_fadein:    int(self.editFadeIn.get()),
				# c_fadeout:   int(self.editFadeOut.get()),
				c_repeat_count: 		   int(self.editRepeatCount.get()),
				c_pause: 				   int(self.editPause.get()),
				c_signal_window_type:		int(self.cbSignalWindowType.current()),
				c_signal_window_form:		int(self.cbSignalWindowForm.current()),
				c_signal_window_place:		int(self.cbSignalWindowPlace.current()),
				c_signal_window_duration:	int(self.editWindowDuration.get()),
				c_koeff: 				   	float(self.editKoeff.get()),
				# c_meandr_pulse_width:	   get_cfg_param(cfg, c_meandr_pulse_width, 250, 'i'),
				# c_meandr_interval_0:   get_cfg_param(cfg, c_meandr_interval_0, 100, 'i'),
				# c_meandr_type:  		   get_cfg_param(cfg, c_meandr_type, m_one_channel, 'i'),
				# c_meandr_interval_1:  get_cfg_param(cfg, c_meandr_interval_1, 0, 'i'),
				c_filter_freq_min:   int(self.editFilterFreqMin.get()),
				c_filter_freq_max:   int(self.editFilterFreqMax.get()),
				c_filtrate:            bool(self.filtrate.get()),
				c_spectrum_form_file:  self.editSpectrumFormFile.get(),
				# c_apply_spectrum_form: bool(self.apply_spectrum_form.get()),
				c_apply_accurately_to_form: bool(self.apply_accurately_to_form.get()),
				c_channel_count:    int(self.editChannelCount.get()),
				c_saw_count_per_point:      int(self.editSawpp.get()),
				c_zero_smooth:  int(self.editZeroSmooth.get()),
				c_channel_gap: int(self.editChannelGap.get()),
				c_send:       bool(self.send.get()),
				c_host:       self.editHost.get(),
				c_port:       int(self.editPort.get()),
				c_mode: 	  int(self.cbMode.current()),
				c_make_shim:  bool(self.make_shim.get()),
				c_make_wav:  bool(self.make_wav.get()),
				c_make_matlab:  bool(self.make_matlab.get()),
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
			# рабочий каталог
			self.config[c_workdir] = self.config[c_workdir].replace('\u005c', '/')
			if len(self.config[c_workdir]) > 0 and self.config[c_workdir][-1] != '/': self.config[c_workdir] += '/'
			self.editWorkDir.delete(0, END)
			self.editWorkDir.insert(0, get_cfg_param(self.config, c_workdir, ''))

			# перечитываем некоторые параметры из файла
			self.re_read_params([[c_meandr_pulse_width, 20], [c_meandr_interval_0, 20], [c_meandr_type, 0], [c_meandr_interval_1, 0],
								 [c_save_log, True], [c_spec_form_edit_control_count, 41],
								 [c_sinus_pack_step, 100], [c_meandr_pack_step, 200],
								 [c_spectrum_norm_level, 500], [c_spectrum_source_file, '']])

			

			self.config[c_signal_name] = self.cbSignalType.get()

			return self.config

		except Exception as E:
			print('error in func _ui.checkout_config(): %s' % E, file=sys.stderr)
			return None



def do(config):
	config[c_cur_time] = datetime.now().timetuple()
	# config[c_cur_date] = time.strftime(c_date_format)
	# config[] = time.strftime(c_time_format)

	# пишем текущую конфигурацию в лог
	# log_file_name = None
	if get_cfg_param(config, c_save_log, True, 'b') == True:
		log_file_name = get_path(config, C_LOG) # self.config[c_workdir] + time.strftime(c_date_format + ' ' + c_time_format) + '.log'

	# if not config[c_log_file_name] is None:
		with open(log_file_name, 'w') as log_file:
			keys = []
			keys.extend(config.keys())
			keys.remove(c_cur_time)
			keys.remove(c_signal_name)
			keys.sort()
			
			for key in keys:
				log_file.write(key + '=' + str(config[key]) + '\n')

			log_file.write('\n')

		if config[c_signal_type] == s_type_spectrum_form:
			shutil.copyfile(config[c_spectrum_form_file], get_path(config, C_SPECTRUM))


	# имена файлов
	filename_raw = get_path(config, C_RAWF)
	filename_flt = get_path(config, C_RAWF)
	filename_shim = get_path(config, C_SHIM)
	filename_spectrum = get_path(config, C_SPECTRUM)

	#####################################################
	#####################################################
	 
	SEND_STOP = 0
	 
	MAKE_SHIM = config[c_make_shim]
	MAKE_WAV = config[c_make_wav]
	MAKE_MATLAB = config[c_make_matlab]
	
	filtrate = get_cfg_param(config, c_filtrate, True, 'b') and (config[c_signal_type] != gen.s_type_noise)
	# apply_spectrum_form = get_cfg_param(config, c_apply_spectrum_form, False, 'b') and (signal_type != gen.s_type_sinus) and (signal_type != gen.s_type_lfm)

	PLOT_SIGNAL = int(get_cfg_param(config, c_plot_signal, True, 'b'))
	PLOT_FILTERED = int(get_cfg_param(config, c_plot_filtered_signal, True, 'b')) & (int(filtrate)) # | int(apply_spectrum_form))
	PLOT_SIGNAL_SPECTRUM = int(get_cfg_param(config, c_plot_signal_spectrum, True, 'b'))
	PLOT_FILTERED_SPECTRUM = int(get_cfg_param(config, c_plot_filtered_spectrum, True, 'b')) & (int(filtrate)) # | int(apply_spectrum_form))
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
		araw = wav.read_wav(file_name="D:/c++/AME/imperia march r.wav",
				   to_file=filename_raw)
	else:
		araw = gen.generate(config)
		

	# >> перебор интервалов

		# araw = intervals(config)

    # << перебор интервалов

	 
	if araw is None:
		return

	 
	# sys.exit(0)
	if filtrate: # or apply_spectrum_form:
		arawf = spectrum.apply_spectrum(config, signal_data=araw)

	else:
		arawf = araw

	if arawf is None:
		return

	 
	if MAKE_SHIM:
		if not shim.shim(config, data=arawf):
			return

	if MAKE_WAV:
		wav.write_wav(config, data=arawf)
		import os
		os.startfile('%s' % get_path(config, C_WAV))
		

	if SEND and MAKE_SHIM:
		sock.send(config)

	if MAKE_MATLAB:
		matlab.write_m_file(config)

	 
	if PLOT:
		plot.plot(config, flags=FLAGS)


def intervals(config):
	araw = arr.array('d')
	dur = 0
	i = 1

	try:
		int_file = get_path(config, 'txt')
		with open(int_file, 'w') as ifile:

			ifile.write(int_file + '\n\n')
			
			for low_int in np.arange(200, 260, 10): # 5 кГц - 4 кГц
				
				config[c_meandr_interval_0] = low_int
				
				for high_int in np.arange(500, 1050, 50): # 2 кГц - 1 кГц
					
					config[c_meandr_interval_1] = high_int
					
					a = gen.generate(config)
					
					araw.extend(a)
					
					dur += config[c_duration]
					ifile.write('%i\timp=%s\tint0=%i\tint1=%i\n' % (i, config[c_meandr_pulse_width], low_int, high_int))
					i += 1
	
			ifile.write('\nduration=%i\n' % dur)
			config[c_duration] = dur

		
		with open(get_path(config, C_RAW), 'wb') as f:
			araw.tofile(f)

		print('полный файл записан ok')

		return araw

	except Exception as E:
		print('ошибка при переборе интервалов: %s' % E, file=sys.stderr)
		return None
