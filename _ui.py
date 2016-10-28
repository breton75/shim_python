import sys
import tkinter as tk
import tkinter.ttk as ttk

def showWindow():

	# читаем файл ini
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


	window = tk.Tk()
	# window.geometry("200x200")

	mainFrame = tk.Frame(window)
	mainFrame.grid(row=0, column=0, sticky='W')
	
### параметры генерации исходного сигнала ###
	
	frameSignal = tk.LabelFrame(mainFrame, text='Генератор')
	frameSignal.grid(row=0, column=0, sticky='N')

	# тип сигнала
	lblSignalType = tk.Label(frameSignal, text='Тип сигнала')
	lblSignalType.grid(row=0, column=0, sticky='E')
	
	cbSignalType = ttk.Combobox(frameSignal)
	cbSignalType.grid(row=0, column=1, sticky='W')
	
	# частота
	lblFrequency = tk.Label(frameSignal, text='Частота')
	lblFrequency.grid(row=1, column=0, sticky='E')

	editFrequency = tk.Entry(frameSignal)
	editFrequency.grid(row=1, column=1, sticky='W')
	if 'frequency' in ini:
		editFrequency.insert(0, ini['frequency'])
	else:
		editFrequency.insert(0, '8000')


	# дискретизация
	lblSampling = tk.Label(frameSignal, text='Дискретизация')
	lblSampling.grid(row=2, column=0, sticky='E')

	editSampling = tk.Entry(frameSignal)
	editSampling.grid(row=2, column=1, sticky='W')
	if 'sampling' in ini:
		editSampling.insert(0, ini['sampling'])
	else:
		editSampling.insert(0, '100000')


	# длительность (мс.)
	lblDuration = tk.Label(frameSignal, text='Длительность (мс)')
	lblDuration.grid(row=3, column=0, sticky='E')

	editDuration = tk.Entry(frameSignal)
	editDuration.grid(row=3, column=1, sticky='W')
	if 'duration' in ini:
		editDuration.insert(0, ini['duration'])
	else:
		editDuration.insert(0, '1000')

	# амплитуда
	lblAmplitude = tk.Label(frameSignal, text='Амплитуда')
	lblAmplitude.grid(row=4, column=0, sticky='E')

	editAmplitude = tk.Entry(frameSignal)
	editAmplitude.grid(row=4, column=1, sticky='W')
	if 'amplitude' in ini:
		editAmplitude.insert(0, ini['amplitude'])
	else:
		editAmplitude.insert(0, '1024')


	# раскачка и затухание сигнала
	lblFadeIn = tk.Label(frameSignal, text='Раскачка')
	lblFadeIn.grid(row=5, column=0, sticky='E')

	editFadeIn = tk.Entry(frameSignal)
	editFadeIn.grid(row=5, column=1, sticky='W')
	if 'fadein' in ini:
		editFadeIn.insert(0, ini['fadein'])
	else:
		editFadeIn.insert(0, '0')


	lblFadeOut = tk.Label(frameSignal, text='Затухание')
	lblFadeOut.grid(row=6, column=0, sticky='E')

	editFadeOut = tk.Entry(frameSignal)
	editFadeOut.grid(row=6, column=1, sticky='W')
	if 'fadeout' in ini:
		editFadeOut.insert(0, ini['fadeout'])
	else:
		editFadeOut.insert(0, '0')
	
### параметры сигнала ###	
	
	window.grid()
	window.mainloop()


showWindow()