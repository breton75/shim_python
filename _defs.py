# -*- coding: utf-8 -*-
import time
import sys
import os


def get_cfg_param(config, param_name, default, type='s'):
	try:
		if type == 'i':
			if param_name in config: return int(config[param_name])
			else: return default
		elif type == 'b':
			if param_name in config:
				return str(config[param_name]).lower() in ['1', 'yes', 'y', 'true', 't']
			else: return default
		elif type == 'f':
			if param_name in config: return float(config[param_name])
			else: return default
		else:
			if param_name in config: return config[param_name]
			else: return default
	except Exception as E:
		print('error in func _defs.get_cfg_param(): %s' % E, file=sys.stderr)
		# print(E)
		return None


def replace_re(config, extention, string, **kwargs):
	return string.replace('{EXT}', extention) \
					.replace('{DATE}', time.strftime(c_date_format, config[c_cur_time])) \
					.replace('{TIME}', time.strftime(c_time_format, config[c_cur_time])) 


def get_folder_name(config, extention, **kwargs):
	try:
		workdir = replace_re(config, extention, config[c_workdir])
		workdir = os.path.abspath(workdir)
		workdir = workdir.replace("\u005c", "/")
		if workdir[-1] != '/': workdir += '/'
		if not os.path.exists(workdir):
			os.makedirs(workdir)

		return workdir

	except Exception as E:
		print('error in func get_folder_name(): %s' % E, file=sys.stderr)
		return None


def get_path(config, extention, **kwargs):
	try:
		if not (c_workdir in config or c_filename_template in config):
			raise Exception('config must contains params "filename_template" and "workdir" specifing path and names of created files\nexample: filename_template = home/user/  workdir=test_main')
	  
		if len(config[c_workdir]) == 0:
			raise Exception("Work directory not specified")
		
		workdir = ''
		if ('only_filename' not in kwargs) or (bool(kwargs['only_filename']) == False):
			workdir = get_folder_name(config, extention)
			
		filename = replace_re(config, extention, config[c_filename_template])

		return workdir + filename + '.' + extention


	except Exception as E:
		print('error in func get_path(): %s' % E, file=sys.stderr)
		return None


###########################################

c_cur_date = 'cur_date'
c_cur_time = 'cur_time'
c_date_format = '%Y_%m_%d'
c_time_format = '%H_%M_%S'

# имена стандартных папок
C_RECEIVED = 'received'
C_MATLAB = 'm'
C_RAW = 'raw'
C_RAWF = 'rawf'
C_WAV = 'wav'
C_SHIM = 'shim'
C_SPECTRUM = 'spectrum'
C_LOG = 'log'


# тип сигналов
s_type_noise = 0
s_type_sinus = 1
s_type_meandr = 2
s_type_sinus_pack = 3
# s_type_sinus_sinus_noise = 4
s_type_lfm = 4
s_type_meandr_pack = 5
# s_type_spectrum = 7
# s_type_flat_spectrum = 6
s_type_spectrum_form = 6

# тип меандра
m_one_channel = 0
m_channels_iterleaved = 1
m_channels_alternate = 2

w_form_trapeze = 0
w_form_cos = 1
w_form_s = 2

w_method_no_window = 0
w_method_atop = 1
w_method_add = 2
w_method_cut = 3

w_place_pack_begin_end = 0
w_place_pack_begin = 1
w_place_pack_end = 2
w_place_signal_begin_end = 3
w_place_signal_begin = 4
w_place_signal_end = 5


## константы
c_signal_type = 'signal_type'
c_signal_name = 'signal_name'
c_freq0  = 'freq0'
c_freq1  = 'freq1'
c_sampling = 'sampling'			
c_duration = 'duration'		
c_hush = 'hush'
c_amplitude	= 'amplitude'
c_fadein = 'fadein'	
c_fadeout = 'fadeout'

c_spectrum_norm_level = 'spectrum_norm_level'
c_spectrum_divider = 'spectrum_divider'
c_koeff = 'koeff'
c_spectrum_source_file = 'spectrum_source_file'

c_meandr_pulse_width = 'meandr_pulse_width'
c_meandr_interval_0 = 'meandr_interval_0'
c_meandr_interval_1='meandr_interval_1'
c_meandr_type = 'meandr_type'
c_meandr_pack_step = 'meandr_pack_step'
c_sinus_pack_step = 'sinus_pack_step'

# постобработка
c_signal_window_type = 'signal_window_type' 
c_signal_window_form = 'signal_window_form'
c_signal_window_place = 'signal_window_place'
c_signal_window_duration = 'signal_window_duration'
c_repeat_count = 'repeat_count'
c_pause = 'pause'

c_filtrate = 'filtrate'
# c_band_pass_filter
c_filter_freq_min = 'filter_freq_min'
c_filter_freq_max = 'filter_freq_max'
c_apply_spectrum_form = 'apply_spectrum_form'
c_apply_accurately_to_form = 'apply_accurately_to_form'
c_spectrum_form_file = 'spectrum_form_file'


c_channel_count = 'channel_count'
c_saw_count_per_point = 'saw_count_per_point'
c_zero_smooth = 'zero_smooth'
c_channel_gap = 'channel_gap'


c_send = 'send'
c_host = 'host'
c_port = 'port'
c_mode = 'mode'

c_make_shim = 'make_shim'
c_make_wav = 'make_wav'
c_play_wav = 'play_wav'
c_make_matlab = 'make_matlab'


c_plot_signal = 'plot_signal'
c_plot_signal_spectrum = 'plot_signal_spectrum'
c_plot_filtered_signal = 'plot_filtered_signal'
c_plot_filtered_spectrum = 'plot_filtered_spectrum'
c_plot_shim = 'plot_shim'
c_plot_signal_saw = 'plot_signal_saw'
c_plot_from_point = 'plot_from_point'
c_plot_to_point = 'plot_to_point'


c_workdir = 'workdir'
c_filename_template = 'filename_template'

c_received_folder = 'received_folder'
c_received_data_file = 'received_data_file'

c_save_log='save_log'
c_log_file_name = 'log_file_name'
c_spec_form_edit_control_count = 'spec_form_edit_control_count'