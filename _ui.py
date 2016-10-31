import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
import _socket_main as sock
import _spectrum_main as spectrum

class mainFrame(Frame):
	def __init__(self, master):
		super(mainFrame, self).__init__(master)
		self.grid() #row=0, column=0, sticky=tk.W)
		
		self.params = {}

		self.showFrame()



	def showFrame(self):
 
		# читаем файл ini = 0
		try:

		  with open('_main.ini', 'r') as inifile:
		    lines = inifile.readlines()
	  
		    # разбираем параметры записанные в файле ini
		    lst = []
		    for line in lines:
		    	if line[0] in ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']:
		    		lst.append(line.split('='))
	  
		    for i in range(len(lst)):
		    	for j in range(len(lst[i])):
		    		lst[i][j] = lst[i][j].strip()

		    ini = dict(lst)

		except Exception as E:
		  print('error on reading ini file: ', file=sys.stderr, end='')
		  print(E, file=sys.stderr)  
		  ini = []


	### -> параметры генерации исходного сигнала ###
	
		self.frameSignal = tk.LabelFrame(self, text='Генератор')
		self.frameSignal.grid(row=0, column=0, sticky=tk.W)

		# тип сигнала
		self.lblSignalType = tk.Label(self.frameSignal, text='Тип сигнала', width=25)
		self.lblSignalType.grid(row=0, column=0, sticky=tk.E)
	
		self.cbSignalType = ttk.Combobox(self.frameSignal, width=13)
		self.cbSignalType.grid(row=0, column=1, sticky=tk.W)
	
		# частота
		self.lblFrequency = tk.Label(self.frameSignal, text='Частота', width=25)
		self.lblFrequency.grid(row=1, column=0, sticky=tk.E)

		self.editFrequency = tk.Entry(self.frameSignal, width=16)
		self.editFrequency.grid(row=1, column=1, sticky=tk.W)
		if 'freq' in ini: self.editFrequency.insert(0, ini['freq'])
		else: self.editFrequency.insert(0, '8000')


		# дискретизация
		self.lblSampling = tk.Label(self.frameSignal, text='Дискретизация', width=25)
		self.lblSampling.grid(row=2, column=0, sticky=tk.E)

		self.editSampling = tk.Entry(self.frameSignal, width=16)
		self.editSampling.grid(row=2, column=1, sticky=tk.W)
		if 'sampling' in ini: self.editSampling.insert(0, ini['sampling'])
		else: self.editSampling.insert(0, '100000')


		# длительность (мс.)
		self.lblDuration = tk.Label(self.frameSignal, text='Длительность (мс)', width=25)
		self.lblDuration.grid(row=3, column=0, sticky=tk.E)

		self.editDuration = tk.Entry(self.frameSignal, width=16)
		self.editDuration.grid(row=3, column=1, sticky=tk.W)
		if 'duration' in ini: self.editDuration.insert(0, ini['duration'])
		else: self.editDuration.insert(0, '1000')

		# амплитуда
		self.lblAmplitude = tk.Label(self.frameSignal, text='Амплитуда', width=25)
		self.lblAmplitude.grid(row=4, column=0, sticky=tk.E)

		self.editAmplitude = tk.Entry(self.frameSignal, width=16)
		self.editAmplitude.grid(row=4, column=1, sticky=tk.W)
		if 'amplitude' in ini: self.editAmplitude.insert(0, ini['amplitude'])
		else: self.editAmplitude.insert(0, '1024')


		# раскачка сигнала
		self.lblFadeIn = tk.Label(self.frameSignal, text='Раскачка', width=25)
		self.lblFadeIn.grid(row=5, column=0, sticky=tk.E)

		self.editFadeIn = tk.Entry(self.frameSignal, width=16)
		self.editFadeIn.grid(row=5, column=1, sticky=tk.W)
		if 'fadein' in ini: self.editFadeIn.insert(0, ini['fadein'])
		else: self.editFadeIn.insert(0, '0')

		# затухание сигнала
		lblFadeOut = tk.Label(self.frameSignal, text='Затухание', width=25).grid(row=6, column=0, sticky=tk.E)
		self.editFadeOut = tk.Entry(self.frameSignal, width=16)
		self.editFadeOut.grid(row=6, column=1, sticky=tk.W)
		if 'fadeout' in ini: self.editFadeOut.insert(0, ini['fadeout'])
		else: self.editFadeOut.insert(0, '0')
	
	### <- параметры сигнала ###	

	## -> фильтрация ##

		self.frameFilter = tk.LabelFrame(self, text='Фильтрация')
		self.frameFilter.grid(row=1, column=0, sticky=tk.W)

		self.filtrate = BooleanVar()
		self.checkFilter = tk.Checkbutton(self.frameFilter, text='Применить полосовой фильтр', variable=self.filtrate)
		self.checkFilter.grid(row=0, column=0, sticky=tk.W, columnspan=2)
		self.filtrate.set(not 'filtrate' in ini or ('filtrate' in ini and ini['filtrate'].lower() in ['1', 'yes', 'y', 'true']))
		# else: self.filtrate.set(False)

		# минимальная частота
		self.lblFreqMin = tk.Label(self.frameFilter, text='Мин. частота', width=25)
		self.lblFreqMin.grid(row=1, column=0, sticky=tk.E)

		self.editFreqMin = tk.Entry(self.frameFilter, width=16)
		self.editFreqMin.grid(row=1, column=1, sticky=tk.W)
		if 'freqmin' in ini: self.editFreqMin.insert(0, ini['freqmin'])
		else: self.editFreqMin.insert(0, '1000')

		# максимальная частота
		self.lblFreqMax = tk.Label(self.frameFilter, text='Макс. частота', width=25)
		self.lblFreqMax.grid(row=2, column=0, sticky=tk.E)
		self.editFreqMax = tk.Entry(self.frameFilter, width=16)
		self.editFreqMax.grid(row=2, column=1, sticky=tk.W)
		if 'freqmax' in ini: self.editFreqMax.insert(0, ini['freqmax'])
		else: self.editFreqMax.insert(0, '4000')

		# редактировать форму спектра
		self.edit_spectrum_form = BooleanVar()
		self.checkEditSpectrumForm = tk.Checkbutton(self.frameFilter, text='Редактировать форму спектра', variable=self.edit_spectrum_form)
		self.checkEditSpectrumForm.grid(row=3, column=0, sticky=tk.W, columnspan=2)


		# # применить форму спектра
		self.apply_spectrum_form = BooleanVar()
		self.checkApplySpectrumForm = tk.Checkbutton(self.frameFilter, text='Применить заданную форму спектра', variable=self.apply_spectrum_form)
		self.checkApplySpectrumForm.grid(row=4, column=0, sticky=tk.W, columnspan=2)

		# редактор
		self.bnEditSpectrumForm = tk.Button(self.frameFilter, text='Редактор формы спектра', command=self.edit_spectrum)
		self.bnEditSpectrumForm.grid(row=5, column=0, sticky=tk.E)

	## <- фильтрация ##

	## -> преобразование шим ##

		self.frameShim = tk.LabelFrame(self, text='Преобразование ШИМ')
		self.frameShim.grid(row=0, column=1, sticky=tk.N, rowspan=1)

		# кол-во каналов
		lblChannelCount = tk.Label(self.frameShim, text='Кол-во каналов', width=25).grid(row=0, column=0, sticky=tk.E)
		self.editChannelCount = tk.Entry(self.frameShim, width=16)
		self.editChannelCount.grid(row=0, column=1, sticky=tk.W)
		if 'chcount' in ini: self.editChannelCount.insert(0, ini['chcount'])
		else: self.editChannelCount.insert(0, '2')

		# пил на точку
		lblSawpp = tk.Label(self.frameShim, text='Пил на точку', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editSawpp = tk.Entry(self.frameShim, width=16)
		self.editSawpp.grid(row=1, column=1, sticky=tk.W)
		if 'sawpp' in ini: self.editSawpp.insert(0, ini['sawpp'])
		else: self.editSawpp.insert(0, '1')

		# размытие нуля
		lblZeroSmooth = tk.Label(self.frameShim, text='Пил на точку', width=25).grid(row=2, column=0, sticky=tk.E)
		self.editZeroSmooth = tk.Entry(self.frameShim, width=16)
		self.editZeroSmooth.grid(row=2, column=1, sticky=tk.W)
		if 'zerosmoth' in ini: self.editZeroSmooth.insert(0, ini['zerosmoth'])
		else: self.editZeroSmooth.insert(0, '0')

		# разрыв между каналами
		lblChannelGap = tk.Label(self.frameShim, text='Разрыв между каналами', width=25).grid(row=3, column=0, sticky=tk.E)
		self.editChannelGap = tk.Entry(self.frameShim, width=16)
		self.editChannelGap.grid(row=3, column=1, sticky=tk.W)
		if 'channelgap' in ini: self.editChannelGap.insert(0, ini['channelgap'])
		else: self.editChannelGap.insert(0, '0')

	## <- преобразование шим ##

	## -> выгрузка на устройство ##

		self.frameSend = tk.LabelFrame(self, text='Выгрузка')
		self.frameSend.grid(row=1, column=1, sticky=tk.N)

		self.send = BooleanVar()
		self.checkSend = tk.Checkbutton(self.frameSend, text='Выгрузить сигнал на устройство', variable=self.send)
		self.checkSend.grid(row=0, column=0, sticky=tk.E, columnspan=2)

		# host
		lblHost = tk.Label(self.frameSend, text='IP', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editHost = tk.Entry(self.frameSend, width=16)
		self.editHost.grid(row=1, column=1, sticky=tk.W)
		if 'host' in ini: self.editHost.insert(0, ini['host'])
		else: self.editHost.insert(0, '172.16.4.55')

		# port
		lblPort = tk.Label(self.frameSend, text='Порт', width=25).grid(row=2, column=0, sticky=tk.E)
		self.editPort = tk.Entry(self.frameSend, width=16)
		self.editPort.grid(row=2, column=1, sticky=tk.W)
		if 'port' in ini: self.editPort.insert(0, ini['port'])
		else: self.editPort.insert(0, '35580')

		# режим работы: ONE или LOOP
		self.lblMode = tk.Label(self.frameSend, text='Режим работы', width=25)
		self.lblMode.grid(row=3, column=0, sticky=tk.E)
	
		self.cbMode = ttk.Combobox(self.frameSend, width=13)
		self.cbMode.grid(row=3, column=1, sticky=tk.W)

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

		# отобразить отфильтрованный сигнал
		self.plot_filtered_signal = BooleanVar()
		self.checkPlotFiltered = tk.Checkbutton(self.framePlot, text='Отфильтрованный сигнал', variable=self.plot_filtered_signal)
		self.checkPlotFiltered.grid(row=1, column=0, sticky=tk.W, columnspan=4)
	
		# отобразить спектр сигнала
		self.plot_signal_spectrum = BooleanVar()
		self.checkSignalSpectrum = tk.Checkbutton(self.framePlot, text='Спектр сигнала', variable=self.plot_signal_spectrum)
		self.checkSignalSpectrum.grid(row=0, column=1, sticky=tk.W, columnspan=4)
	
		# отобразить спектр отфильтрованного сигнала
		self.plot_filtered_spectrum = BooleanVar()
		self.checkPlotFilteredSignalSpectrum = tk.Checkbutton(self.framePlot, text='Спектр отфильтрованного сигнала', variable=self.plot_filtered_spectrum)
		self.checkPlotFilteredSignalSpectrum.grid(row=1, column=1, sticky=tk.W, columnspan=4)

		# отобразить ШИМ
		self.plot_shim = BooleanVar()
		self.checkPlotShim = tk.Checkbutton(self.framePlot, text='ШИМ', variable=self.plot_shim)
		self.checkPlotShim.grid(row=2, column=0, sticky=tk.W, columnspan=4)

		# сигнал с точки .. по ..
		lblPlotFromPoint = tk.Label(self.framePlot, text='Показать точки с', width=25).grid(row=3, column=0, sticky=tk.E)
		self.editPlotFromPoint = tk.Entry(self.framePlot, width=5)
		self.editPlotFromPoint.grid(row=3, column=1, sticky=tk.W)
		if 'plotfrompoint' in ini: self.editPlotFromPoint.insert(0, ini['plotfrompoint'])
		else: self.editPlotFromPoint.insert(0, '1')
		
		lblPlotToPoint = tk.Label(self.framePlot, text=' по ', width=4).grid(row=3, column=2, sticky=tk.E)
		self.editPlotToPoint = tk.Entry(self.framePlot, width=53)
		self.editPlotToPoint.grid(row=3, column=3, sticky=tk.W)
		if 'plottopoint' in ini: self.editPlotToPoint.insert(0, ini['plottopoint'])
		else: self.editPlotToPoint.insert(0, '1000')

	## <- отрисовка ##

	## -> общее ##
	
		self.frameGen = tk.LabelFrame(self, text='Общее')
		self.frameGen.grid(row=5, column=0, sticky=tk.W, columnspan=2)

		# рабочий каталог
		lblWorkDir = tk.Label(self.frameGen, text='Рабочий каталог', width=25).grid(row=0, column=0, sticky=tk.E)
		self.editWorkDir = tk.Entry(self.frameGen, width=65)
		self.editWorkDir.grid(row=0, column=1, sticky=tk.W)
		if 'workdir' in ini: self.editWorkDir.insert(0, ini['workdir'])
		else: self.editWorkDir.insert(0, '')

		# шаблон имен файлов
		lblFilenameTemplate = tk.Label(self.frameGen, text='Шаблон имен файлов', width=25).grid(row=1, column=0, sticky=tk.E)
		self.editFilenameTemplate = tk.Entry(self.frameGen, width=65)
		self.editFilenameTemplate.grid(row=1, column=1, sticky=tk.W)
		if 'fntemplate' in ini: self.editFilenameTemplate.insert(0, ini['fntemplate'])
		else: self.editFilenameTemplate.insert(0, '')


	## <- общее ##

	## -> кнопки ##

		self.frameButtons = tk.Frame(self)
		self.frameButtons.grid(row=6, column=0, sticky=tk.W, columnspan=2)

		# ПУСК
		self.bnStart = tk.Button(self.frameButtons, text='Старт', width=80, command = self.start)
		self.bnStart.grid(row=1, column=0, sticky=tk.E, columnspan=2)

		# отмена
		self.bnCancel = tk.Button(self.frameButtons, text='Отмена', width=80)
		self.bnCancel.grid(row=3, column=0, sticky=tk.E, columnspan=2)

	## <- кнопки ##



	def send_stop(self):
		try:
			h = self.editHost.get()
			p = int(self.editPort.get())
			sock.sendSTOP(h, p)

		except Exception as E:
			sys.stderror.write(E)


	def edit_spectrum(self):
		try:
			if self.checkout_params() is None: return

			fn = self.params['workdir']
			if len(fn) == 0:
				raise Exception('Path not found')

			if fn[-1] != '/': fn += '/'
			fn += self.params['fntemplate']

			spectrum.edit_spectrum(sff=fn + '.spectrum', raw=fn+'.raw', s=self.params['sampling'], d=self.params['duration'], fmin=self.params['freqmin'], fmax=self.params['freqmax'])

		except Exception as E:
			print(E, file=sys.stderr)			

	def start(self):
		self.checkout_params()


	def checkout_params(self):
		try:
			# собираем параметры
			self.params = {
				'frequency': int(self.editFrequency.get()),	
				'sampling':  int(self.editSampling.get()),
				'amplitude': int(self.editAmplitude.get()),
				'duration':  int(self.editDuration.get()),
				'fadein':    int(self.editFadeIn.get()),
				'fadeout':   int(self.editFadeOut.get()),
				'freqmin':   int(self.editFreqMin.get()),
				'freqmax':   int(self.editFreqMax.get()),
				'filtrate':            bool(self.filtrate.get()),
				'edit_spectrum_form':  bool(self.edit_spectrum_form.get()),
				'apply_spectrum_form': bool(self.apply_spectrum_form.get()),
				'chcount':    int(self.editChannelCount.get()),
				'sawpp':      int(self.editSawpp.get()),
				'zerosmoth':  int(self.editZeroSmooth.get()),
				'channelgap': int(self.editChannelGap.get()),
				'send':       bool(self.send.get()),
				'host':       self.editHost.get(),
				'port':       int(self.editPort.get()),
				'plot_signal':            bool(self.plot_signal.get()),
				'plot_filtered_signal':   bool(self.plot_filtered_signal.get()),
				'plot_signal_spectrum':   bool(self.plot_signal_spectrum.get()),
				'plot_filtered_spectrum': bool(self.plot_filtered_spectrum.get()),
				'plot_shim':              bool(self.plot_shim.get()),
				'plotfrompoint':          int(self.editPlotFromPoint.get()),
				'plottopoint':            int(self.editPlotToPoint.get()),
				'workdir':                self.editWorkDir.get(),
				'fntemplate':             self.editFilenameTemplate.get()
			}

			return self.params

		except Exception as E:
			sys.stderror.write(E)
			return None




window = tk.Tk()
# window.geometry("200x200")

frame = mainFrame(window)
window.grid()
window.mainloop()
print(frame.params)
# window.close()