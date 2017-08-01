# -*- coding: utf-8 -*-

##from _generator_main import *
import sys
import argparse
from _ui_main import showWindow
from _ui_main import do
import tkinter as tk
# from _ui_main import *
# from _ui import get_cfg_param


version = '1.1.2.3'

# ******** Script starts here ************* #

config = {}

parser = argparse.ArgumentParser()
parser.add_argument('-noui', '--noui', required=False, action='count')
namespace = parser.parse_args(sys.argv[1:])

if namespace.noui == None:
  showWindow(version)

  # window = tk.Tk()
  # frame = mainFrame(window)
  # window.grid()
  # window.mainloop()

else:
  try:

    with open('_main.config', 'r', encoding="utf8") as configfile:
      lines = configfile.readlines()
    
      # разбираем параметры записанные в файле ini
      lst = []
      for line in lines:
        p = line.split('=')
        if len(p) == 2: lst.append(p)
    
      for i in range(len(lst)):
        for j in range(len(lst[i])):
          lst[i][j] = lst[i][j].strip()
      

      config = dict(lst)
      do(config)
    
  except Exception as E:
    print('error on reading config file: %s' % E, file=sys.stderr, end='')
    sys.exit(1)




