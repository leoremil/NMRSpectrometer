# %%

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os

path = os.path.dirname(os.path.abspath(__file__))

CAPTURE_DURATION = 0.1 #total sampling time
START_TIME = 0 #Rough start of FID signal
REFERENCE_START_TIME = 0.1 #Time where FID is gone to use as a comparison signal

NUM_FREQ_ARRAY_ELEMENTS = 2 #number of frequencies tested

NUM_DURATION_ARRAY_ELEMENTS = 2 #Number of different pulse widths tried
# Note that setting the averages to greater than 1 removes the peaks from the
# first trial (and only the first trial). Not sure why.
NUM_AVERAGES = 2 #number scans (or files) done for each frequency and pulse width combination
NUM_ECHOS = 10 #number of echo signals per scan

NUM_DURATION_ARRAY_ELEMENTS = 2 #Number of different pulse widths?
# Note that setting the averages to greater than 1 removes the peaks from the
# first trial (and only the first trial). Not sure why.
NUM_AVERAGES = 2 #number of scans per frequency?
NUM_ECHOS = 10 #number of echo signals per file


sample_time = 500e-3;

#Go through each frequency, each pulse width file and process the signals.
#First, all the scans (files) for a given freq and pusle width are averaged.
#Spikes in the averaged signal from relay switching are replaced with the average
#signal value. The location of the spikes are determined empirically. The NMR
#and reference signals are isolated. Then, the FFT is taken for each and magnitude
#calculated. A time domain and frequency domain plot is generated for each freq/
#pulse width combination.
for i in list(range(NUM_FREQ_ARRAY_ELEMENTS)):

	for j in list(range(NUM_DURATION_ARRAY_ELEMENTS)):

		signal_ave = 0
		reference_ave = 0
        
        #Averaging
		for k in list(range(NUM_AVERAGES)):

			data = np.loadtxt(path + '/test_data_' + str(i) + '_' + str(j) + '_' + str(k) + '.csv', delimiter=',', unpack=True, skiprows=1)[0:2]

			t = data[0]*1e-3
			sample_rate = 1/(t[1]-t[0])
			signal = data[1]

			signal_ave += signal

		signal_ave = signal_ave/(NUM_AVERAGES)
        
        # Remove Spikes due to relay switcgin, replace with average singal value.
		# Empirical fit to see what range to remove. (Note can set replacement
		# value as non zero (~0.3) to help align portion being removed with
		# spikes. Ideally this could be based on the relay delay time, the pulse
		# duration, and the echo sample spacing.
		for l in list(range(NUM_ECHOS + 1)):
			signal_ave[(t > 33.2e-3*l) & (t < 33.2e-3*l + 4e-3)] = np.average(signal_ave)
		
		# alternative method to remove noise by removing large value
		# signal_ave[np.abs(signal_ave - np.average(signal_ave)) > 0.7*np.average(np.abs(signal_ave))] = np.average(signal_ave)

        #Isolate the NMR signal
		signal_trimmed = (signal_ave)[(t <= START_TIME + CAPTURE_DURATION) & (t > START_TIME)]
        #Isolate the reference signal
		reference_trimmed = (signal_ave)[(t <= REFERENCE_START_TIME + CAPTURE_DURATION) & (t > REFERENCE_START_TIME)]

		f = np.fft.fftfreq(int(sample_rate*CAPTURE_DURATION),1/sample_rate) 

		signal_amplitude = 2/(sample_rate*CAPTURE_DURATION)*abs(np.fft.fft(signal_trimmed))
		reference_amplitude = 2/(sample_rate*CAPTURE_DURATION)*abs(np.fft.fft(reference_trimmed))

		signal_dBV = 20*np.log10(signal_amplitude/1)
		reference_dBV = 20*np.log10(reference_amplitude/1)

		min_f = 50e3
		max_f = 60e3
        
        #Take only values within the specified freq. range
		f_trimmed = f[(f > min_f) & (f < max_f)]
		signal_dBV = signal_dBV[(f > min_f) & (f < max_f)]
		reference_dBV = reference_dBV[(f > min_f) & (f < max_f)]

        #Find and display peak value, average noise, peak frequency
		signal_peak = np.max(signal_dBV)
		noise_ave = np.sum(signal_dBV)/np.size(f_trimmed)
		print(noise_ave)
		print(signal_peak)
		print((f_trimmed[signal_dBV >= signal_peak])/1e3)
		# print(signal_peak-noise_ave)
		print("\n")
        
        #Plotting for FFT of a frequency/pulsewidth combo
		plt.close('all')

		rc = {"font.family" : "serif", "mathtext.fontset" : "stix"}
		plt.rcParams.update(rc)
		plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]
		plt.rcParams['font.size'] = 10
		mpl.rcParams['axes.linewidth'] = 1

		fig, ax = plt.subplots()
		fig.subplots_adjust(left=0.15, bottom=0.16, right=0.85, top=0.97)

		width  = 3.487
		height = width / 1.618
		fig.set_size_inches(width, height)


		ax.xaxis.set_tick_params(which='major', size=5, width=1, direction='in')
		ax.xaxis.set_tick_params(which='minor', size=3, width=1, direction='in')

		ax.yaxis.set_tick_params(which='major', size=5, width=1, direction='in')
		ax.yaxis.set_tick_params(which='minor', size=3, width=1, direction='in')


		step_y1 = 25
		step_x = 5


		ax.set_xlim(min_f/1e3-step_x/4, max_f/1e3+step_x/4)

		ax.set_ylim(-112.5-step_y1/4, -37.5+step_y1/4)

		ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(step_x))
		ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(step_x/2))

		ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(step_y1))
		ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(step_y1/2))


		ax.set_xlabel('$f \\quad (\\rm{kHz})$', labelpad=1)
		ax.set_ylabel('$\\rm{Amplitude} \\quad (\\rm{dBV})$', labelpad=4)

		mpl.rcParams['axes.unicode_minus'] = False # uses dash instead of minus for axis numbers


		ax.plot(f_trimmed/1e3, signal_dBV, linewidth=1, color='r', linestyle='solid',markersize='2', label='Input')
		ax.plot(f_trimmed/1e3, reference_dBV, linewidth=1, color='k', linestyle='solid',markersize='2', label='Input')

		plt.savefig(path + '/FFT_' + str(i) + '_' + str(j)  + '.pdf')


        #Plot time domain of frequency/pulsewidth combo
		plt.close('all')

		rc = {"font.family" : "serif", "mathtext.fontset" : "stix"}
		plt.rcParams.update(rc)
		plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]
		plt.rcParams['font.size'] = 10
		mpl.rcParams['axes.linewidth'] = 1

		fig, ax = plt.subplots()
		fig.subplots_adjust(left=0.15, bottom=0.16, right=0.85, top=0.97)

		width  = 3.487
		height = width / 1.618
		fig.set_size_inches(width, height)


		ax.xaxis.set_tick_params(which='major', size=5, width=1, direction='in')
		ax.xaxis.set_tick_params(which='minor', size=3, width=1, direction='in')

		ax.yaxis.set_tick_params(which='major', size=5, width=1, direction='in')
		ax.yaxis.set_tick_params(which='minor', size=3, width=1, direction='in')


		step_y1 = 25
		step_x = 5

		ax.set_xlim(0, sample_time)

		# ax.set_ylim(-112.5-step_y1/4, -37.5+step_y1/4)

		# ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(step_x))
		# ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(step_x/2))

		# ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(step_y1))
		# ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(step_y1/2))


		ax.set_xlabel('$t \\quad (\\rm{s})$', labelpad=1)
		ax.set_ylabel('$\\rm{Amplitude} \\quad (\\rm{V})$', labelpad=4)

		mpl.rcParams['axes.unicode_minus'] = False # uses dash instead of minus for axis numbers

		ax.plot(t, signal_ave, linewidth=1, color='k', linestyle='solid',markersize='2', label='Input')

		plt.savefig(path + '/Time_' + str(i) + '_' + str(j)  + '.pdf')


