# -*- coding: utf-8 -*-

def get_cfg_param(config, param_name, default, type='s'):
	try:
		if type == 'i':
			if param_name in config: return int(config[param_name])
			else: return default
		elif type == 'b':
			if param_name in config:
				return str(config[param_name]).lower() in ['1', 'yes', 'y', 'true', 't']
			else: return default
		else:
			if param_name in config: return config[param_name]
			else: return default
	except Exception as E:
		print('error in func _exec_main.get_cfg_param(): %s' % E, file=sys.stderr)
		# print(E)
		return None


def get_path(config, extention):
	try:
		if not (c_workdir in config or c_filename_template in config):
			raise Exception('config must contains params "filename_template" and "workdir" specifing path and names of created files\nexample: filename_template = home/user/  workdir=test_main')
	  
		filename_template = config[c_workdir]
		if len(filename_template) == 0:
			raise Exception("Work directory not specified")

		if filename_template[-1] != '/': filename_template += '/'

		return filename_template + config[c_filename_template] + '.' + extention


	except Exception as E:
		print('error in func get_path(): %s' % E, file=sys.stderr)
		return None


# тип сигналов
s_type_noise = 0
s_type_sinus = 1
s_type_meandr = 2
s_type_sinus_pack = 3
s_type_sinus_sinus_noise = 4
s_type_lfm = 5
s_type_meandr_pack = 6
s_type_spectrum = 7

# тип меандра
m_one_channel = 0
m_channels_iterleaved = 1
m_channels_alternate = 2

w_type_no_window = 0
w_type_trapeze = 1
w_type_cos = 2
w_type_s = 3

w_method_atop = 0
w_method_add = 1

w_place_pack_begin_end = 0
w_place_pack_begin = 1
w_place_pack_end = 2
w_place_signal_begin_end = 3
w_place_signal_begin = 4
w_place_signal_end = 5


## константы
c_signal_type = 'signal_type'
c_freq0  = 'freq0'
c_freq1  = 'freq1'
c_sampling = 'sampling'			
c_duration = 'duration'		
c_hush = 'hush'
c_amplitude	= 'amplitude'
c_fadein = 'fadein'	
c_fadeout = 'fadeout'

c_meandr_pulse_width = 'meandr_pulse_width'
c_meandr_interval_width = 'meandr_interval_width'
c_meandr_type = 'meandr_type'
c_meandr_random_interval='meandr_random_interval'
c_meandr_pack_step = 'meandr_pack_step'
c_sinus_pack_step = 'sinus_pack_step'

# постобработка
c_signal_window_type = 'signal_window_type'
c_signal_window_method = 'signal_window_method' 
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


c_channel_count = 'channel_count'
c_saw_count_per_point = 'saw_count_per_point'
c_zero_smooth = 'zero_smooth'
c_channel_gap = 'channel_gap'


c_send = 'send'
c_host = 'host'
c_port = 'port'
c_mode = 'mode'


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

c_save_log='save_log'
c_log_file_name = 'log_file_name'