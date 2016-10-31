import sys
import tkinter as tk
import tkinter.ttk as ttk


class window():
	def __init__(self, master):
		self.showWindow()


	def showWindow():
 
		# читаем файл ini = 0
		try:

		  with open('_main.ini', 'r') as inifile:
		    lines = inifile.readlines()
	  
		    # разбираем параметры записанные в файле ini
		    lst = []
		    for line in lines:
		      lst.append(line.split('='))
	  
		    for i in range(len(lst)):
		      for j in range(len(lst[i])):
		        lst[i][j] = lst[i][j].strip()

		    ini = dict(lst)

		except Exception as E:
		  print('error on reading ini file: ', file=sys.stderr, end='')
		  print(E, file=sys.stderr)  
		  ini = []


		self.window = tk.Tk()
		# window.geometry("200x200")

		self.mainFrame = tk.Frame(self.window)
		self.mainFrame.grid(row=0, column=0, sticky=tk.W)


	### -> параметры генерации исходного сигнала ###
	
		frameSignal = tk.LabelFrame(mainFrame, text='Генератор', height=200)
		frameSignal.grid(row=0, column=0, sticky=tk.W)

		# тип сигнала
		lblSignalType = tk.Label(frameSignal, text='Тип сигнала', width=25)
		lblSignalType.grid(row=0, column=0, sticky=tk.E)
	
		cbSignalType = ttk.Combobox(frameSignal, width=13)
		cbSignalType.grid(row=0, column=1, sticky=tk.W)
	
		# частота
		lblFrequency = tk.Label(frameSignal, text='Частота', width=25)
		lblFrequency.grid(row=1, column=0, sticky=tk.E)

		editFrequency = tk.Entry(frameSignal, width=16)
		editFrequency.grid(row=1, column=1, sticky=tk.W)
		if 'frequency' in ini: editFrequency.insert(0, ini['frequency'])
		else: editFrequency.insert(0, '8000')


		# дискретизация
		lblSampling = tk.Label(frameSignal, text='Дискретизация', width=25)
		lblSampling.grid(row=2, column=0, sticky=tk.E)

		editSampling = tk.Entry(frameSignal, width=16)
		editSampling.grid(row=2, column=1, sticky=tk.W)
		if 'sampling' in ini: editSampling.insert(0, ini['sampling'])
		else: editSampling.insert(0, '100000')


		# длительность (мс.)
		lblDuration = tk.Label(frameSignal, text='Длительность (мс)', width=25)
		lblDuration.grid(row=3, column=0, sticky=tk.E)

		editDuration = tk.Entry(frameSignal, width=16)
		editDuration.grid(row=3, column=1, sticky=tk.W)
		if 'duration' in ini: editDuration.insert(0, ini['duration'])
		else: editDuration.insert(0, '1000')

		# амплитуда
		lblAmplitude = tk.Label(frameSignal, text='Амплитуда', width=25)
		lblAmplitude.grid(row=4, column=0, sticky=tk.E)

		editAmplitude = tk.Entry(frameSignal, width=16)
		editAmplitude.grid(row=4, column=1, sticky=tk.W)
		if 'amplitude' in ini: editAmplitude.insert(0, ini['amplitude'])
		else: editAmplitude.insert(0, '1024')


		# раскачка сигнала
		lblFadeIn = tk.Label(frameSignal, text='Раскачка', width=25)
		lblFadeIn.grid(row=5, column=0, sticky=tk.E)

		editFadeIn = tk.Entry(frameSignal, width=16)
		editFadeIn.grid(row=5, column=1, sticky=tk.W)
		if 'fadein' in ini: editFadeIn.insert(0, ini['fadein'])
		else: editFadeIn.insert(0, '0')

		# затухание сигнала
		lblFadeOut = tk.Label(frameSignal, text='Затухание', width=25).grid(row=6, column=0, sticky=tk.E)
		editFadeOut = tk.Entry(frameSignal, width=16)
		editFadeOut.grid(row=6, column=1, sticky=tk.W)
		if 'fadeout' in ini: editFadeOut.insert(0, ini['fadeout'])
		else: editFadeOut.insert(0, '0')
	
	### <- параметры сигнала ###	

	## -> фильтрация ##

		frameFilter = tk.LabelFrame(mainFrame, text='Фильтрация')
		frameFilter.grid(row=1, column=0, sticky=tk.W)

		checkFilter = tk.Checkbutton(frameFilter, text='Применить полосовой фильтр')
		checkFilter.grid(row=0, column=0, sticky=tk.W, columnspan=2)

		# минимальная частота
		lblFreqMin = tk.Label(frameFilter, text='Мин. частота', width=25)
		lblFreqMin.grid(row=1, column=0, sticky=tk.E)

		editFreqMin = tk.Entry(frameFilter, width=16)
		editFreqMin.grid(row=1, column=1, sticky=tk.W)
		if 'freqmin' in ini: editFreqMin.insert(0, ini['freqmin'])
		else: editFreqMin.insert(0, '1000')

		# максимальная частота
		lblFreqMax = tk.Label(frameFilter, text='Макс. частота', width=25)
		lblFreqMax.grid(row=2, column=0, sticky=tk.E)
		editFreqMax = tk.Entry(frameFilter, width=16)
		editFreqMax.grid(row=2, column=1, sticky=tk.W)
		if 'freqmax' in ini: editFreqMax.insert(0, ini['freqmax'])
		else: editFreqMax.insert(0, '4000')

		# редактировать форму спектра
		checkEditSpectrumForm = tk.Checkbutton(frameFilter, text='Редактировать форму спектра')
		checkEditSpectrumForm.grid(row=3, column=0, sticky=tk.W, columnspan=2)

		# # применить форму спектра
		checkApplySpectrumForm = tk.Checkbutton(frameFilter, text='Применить заданную форму спектра')
		checkApplySpectrumForm.grid(row=4, column=0, sticky=tk.W, columnspan=2)

		# редактор
		bnEditSpectrumForm = tk.Button(frameFilter, text='Редактор формы спектра')
		bnEditSpectrumForm.grid(row=5, column=0, sticky=tk.E)

	## <- фильтрация ##

	## -> преобразование шим ##

		frameShim = tk.LabelFrame(mainFrame, text='Преобразование ШИМ')
		frameShim.grid(row=0, column=1, sticky=tk.N, rowspan=1)

		# кол-во каналов
		lblChannelCount = tk.Label(frameShim, text='Кол-во каналов', width=25).grid(row=0, column=0, sticky=tk.E)
		editChannelCount = tk.Entry(frameShim, width=16)
		editChannelCount.grid(row=0, column=1, sticky=tk.W)
		if 'chcount' in ini: editChannelCount.insert(0, ini['chcount'])
		else: editChannelCount.insert(0, '2')

		# пил на точку
		lblSawpp = tk.Label(frameShim, text='Пил на точку', width=25).grid(row=1, column=0, sticky=tk.E)
		editSawpp = tk.Entry(frameShim, width=16)
		editSawpp.grid(row=1, column=1, sticky=tk.W)
		if 'sawpp' in ini: editSawpp.insert(0, ini['sawpp'])
		else: editSawpp.insert(0, '1')

		# размытие нуля
		lblZeroSmooth = tk.Label(frameShim, text='Пил на точку', width=25).grid(row=2, column=0, sticky=tk.E)
		editZeroSmooth = tk.Entry(frameShim, width=16)
		editZeroSmooth.grid(row=2, column=1, sticky=tk.W)
		if 'zerosmoth' in ini: editZeroSmooth.insert(0, ini['zerosmoth'])
		else: editZeroSmooth.insert(0, '0')

			# разрыв между каналами
			lblChannelGap = tk.Label(frameShim, text='Разрыв между каналами', width=25).grid(row=3, column=0, sticky=tk.E)
			editChannelGap = tk.Entry(frameShim, width=16)
			editChannelGap.grid(row=3, column=1, sticky=tk.W)
			if 'channelgap' in ini: editChannelGap.insert(0, ini['channelgap'])
			else: editChannelGap.insert(0, '0')

	## <- преобразование шим ##

	## -> выгрузка на устройство ##

			frameSend = tk.LabelFrame(mainFrame, text='Выгрузка')
			frameSend.grid(row=1, column=1, sticky=tk.N)

			checkSend = tk.Checkbutton(frameSend, text='Выгрузить сигнал на устройство')
			checkSend.grid(row=0, column=0, sticky=tk.E, columnspan=2)

		# host
			lblHost = tk.Label(frameSend, text='IP', width=25).grid(row=1, column=0, sticky=tk.E)
			editHost = tk.Entry(frameSend, width=16)
			editHost.grid(row=1, column=1, sticky=tk.W)
			if 'host' in ini: editHost.insert(0, ini['host'])
			else: editHost.insert(0, '172.16.4.55')

		# port
			lblPort = tk.Label(frameSend, text='Порт', width=25).grid(row=2, column=0, sticky=tk.E)
			editPort = tk.Entry(frameSend, width=16)
			editPort.grid(row=2, column=1, sticky=tk.W)
			if 'port' in ini: editPort.insert(0, ini['port'])
			else: editPort.insert(0, '35580')

			# режим работы: ONE или LOOP
			lblMode = tk.Label(frameSend, text='Режим работы', width=25)
			lblMode.grid(row=3, column=0, sticky=tk.E)
	
		cbMode = ttk.Combobox(frameSend, width=13)
		cbMode.grid(row=3, column=1, sticky=tk.W)

			# send STOP
			bnSendStop = tk.Button(frameSend, text='Отправить STOP')
			bnSendStop.grid(row=4, column=0, sticky=tk.E, columnspan=2)

	## <- выгрузка на устройство ##


	## -> отрисовка ##

			framePlot = tk.LabelFrame(mainFrame, text='Отрисовка')
			framePlot.grid(row=3, column=0, sticky=tk.W, columnspan=3)

			# отобразить сигнал
			checkPlotSignal = tk.Checkbutton(framePlot, text='Сигнал')
			checkPlotSignal.grid(row=0, column=0, sticky=tk.W, columnspan=4)

			# отобразить отфильтрованный сигнал
			checkPlotFiltered = tk.Checkbutton(framePlot, text='Отфильтрованный сигнал')
			checkPlotFiltered.grid(row=1, column=0, sticky=tk.W, columnspan=4)
	
		# отобразить спектр сигнала
		checkSignalSpectrum = tk.Checkbutton(framePlot, text='Спектр сигнала')
		checkSignalSpectrum.grid(row=0, column=1, sticky=tk.W, columnspan=4)
	
		# отобразить спектр отфильтрованного сигнала
		checkPlotFilteredSignalSpectrum = tk.Checkbutton(framePlot, text='Спектр отфильтрованного сигнала')
		checkPlotFilteredSignalSpectrum.grid(row=1, column=1, sticky=tk.W, columnspan=4)

			# отобразить ШИМ
			checkPlotShim = tk.Checkbutton(framePlot, text='ШИМ')
			checkPlotShim.grid(row=2, column=0, sticky=tk.W, columnspan=4)

			# сигнал с точки .. по ..
			lblPlotFromPoint = tk.Label(framePlot, text='Показать точки с', width=25).grid(row=3, column=0, sticky=tk.E)
			editPlotFromPoint = tk.Entry(framePlot, width=5)
			editPlotFromPoint.grid(row=3, column=1, sticky=tk.W)
			if 'plotfrompoint' in ini: editPlotFromPoint.insert(0, ini['plotfrompoint'])
			else: editPlotFromPoint.insert(0, '1')
		
		lblPlotToPoint = tk.Label(framePlot, text=' по ', width=4).grid(row=3, column=2, sticky=tk.E)
		editPlotToPoint = tk.Entry(framePlot, width=53)
		editPlotToPoint.grid(row=3, column=3, sticky=tk.W)
		if 'plottopoint' in ini: editPlotToPoint.insert(0, ini['plottopoint'])
		else: editPlotToPoint.insert(0, '1000')

	## <- отрисовка ##

	## -> общее ##
	
		frameGen = tk.LabelFrame(mainFrame, text='Общее')
		frameGen.grid(row=5, column=0, sticky=tk.W, columnspan=2)

		# рабочий каталог
		lblWorkDir = tk.Label(frameGen, text='Рабочий каталог', width=25).grid(row=0, column=0, sticky=tk.E)
		editWorkDir = tk.Entry(frameGen, width=65)
		editWorkDir.grid(row=0, column=1, sticky=tk.W)
		if 'workdir' in ini: editWorkDir.insert(0, ini['workdir'])
		else: editWorkDir.insert(0, '')

		# шаблон имен файлов
		lblFilenameTemplate = tk.Label(frameGen, text='Шаблон имен файлов', width=25).grid(row=1, column=0, sticky=tk.E)
		editFilenameTemplate = tk.Entry(frameGen, width=65)
		editFilenameTemplate.grid(row=1, column=1, sticky=tk.W)
		if 'fntemplate' in ini: editFilenameTemplate.insert(0, ini['fntemplate'])
		else: editFilenameTemplate.insert(0, '')


	## <- общее ##


	## -> кнопки ##

		frameButtons = tk.Frame(mainFrame)
		frameButtons.grid(row=6, column=0, sticky=tk.W, columnspan=2)

		# ПУСК
		bnStart = tk.Button(frameButtons, text='Старт', width=80)
		bnStart.grid(row=1, column=0, sticky=tk.E, columnspan=2)
		bnStart['command'] = start

		# отмена
		bnCancel = tk.Button(frameButtons, text='Отмена', width=80)
		bnCancel.grid(row=3, column=0, sticky=tk.E, columnspan=2)

	## <- кнопки ##

		window.grid()
		window.mainloop()




		return params


	def start():
		print(editFrequency.get())

		# собираем параметры
		params = {'frequency': editFrequency.get()	}

		window.close()

showWindow()