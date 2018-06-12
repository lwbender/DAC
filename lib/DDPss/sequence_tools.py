'''
# veriipy.optimizers.py:
# optimization, fitting, and other related algorithms.
#
'''
import matplotlib as mpl
import pylab as plt
import numpy
#import matplotlib.dates as mpd
import os
import json
import multiprocessing as mpp
import time
import math

#from numba import jit
#
def break_sequence_by_Pdy(XY, P_break = 0.01, n_breaks=None, fignum=None):
	'''
	#
	# this appears to be working properly, but could probably use some more testing...
	# break a sequence into sub-sequences by large Y-deviations.
	'''
	#
	#dy_dx = [[j,abs(y-XY[j][1])/(x-XY[j][0])] for j,(x,y) in enumerate(sorted(XY, key=lambda rw:rw[0])[1:])]
	dy_dx = [[j,y-XY[j][1]] for j,(x,y) in enumerate(sorted(XY, key=lambda rw:rw[0])[1:])]
	dy_dx.sort(key=lambda rw:rw[1])
	#
	n_breaks = (n_breaks or min(1, int(P_break*len(dy_dx))))
	#
	N = len(dy_dx)
	dydx_dist = [[k,x, (j+1)/N] for j,(k,x) in enumerate(sorted(dy_dx, key=lambda rw: rw[1]))]
	#
	break_indices = sorted([0] + [k for k,x,j in dydx_dist[-n_breaks:]])
	#print('bki: ', break_indices)
	#
	if not fignum is None:
		plt.figure(fignum)
		plt.clf()
		ax=plt.gca()
		#plt.plot(*zip(*XY))
		ax.set_xscale('log')
		ax.plot(*zip(*[[x,j] for k,x,j in dydx_dist]), '.')
		#plt.plot(sorted(dy_dx), range(1, len(dy_dx)+1), marker='.', ls='-')
		#plt.plot([min(dy_dx), max(dy_dx)], [1.,1.], ls='-', lw=2.)
		#
		#plt.gca().set_ylim(-.1, 1.1)
	return [XY[break_indices[j-1]:break_indices[j]] for j in range(1,len(break_indices))]
#
def stitch_sequence_by_dydx(data_in, dy_factor=1.5, dy_dx_0=None, dy_dx_break=None, median_out=0., fignum=None):
	# stitch together sequences by extreme fluctuations.
	# for now, force the input to be like [[x,y], ...]
	# some notes on this simple approach:
	#   - the idea is to stitch together data with "steps", where the data fluctuate about some value and then jump to a new value.
	#   - the problem is that, while we see this, we see other types of fluctuations that get caught up in this.
	#   - of particular note, this makes a mess with asymetrical changes (aka a steep jump up then a more gradual decline, like we 
	#   - see when we open the cooler lid (with a dosimter in a cooler). for these cases, this algorithm will often correct the
	#	 initial jump, but then not the subsequent smaller changes, so it introduces steps... like the steps it was designed to remove.
	#   - this is nominally corrected by using a smaller change-threshold, but then we act on more parts of the sequence, and so the probability
	#	 of affecting signal (particularly when signal coincides with noise) increases, and we get really pretty, flat, low-stdev nonsense.
	#   - so, it might be possible to use something like this, but a much more sophisticated definition of the "step" feature is required
	#   
	#	 
	#
	dy_dx = [(y-data_in[j][1])/(x-data_in[j][0]) for j,(x,y) in enumerate(data_in[1:])]
	dy_dx_0 = (dy_dx_0 or numpy.median([x for x in dy_dx if x!=0 and not numpy.isnan(x)]) )
	#
	if not fignum is None:
		plt.figure(fignum)
		plt.plot([x for x,y in data_in[1:]], dy_dx/dy_dx_0, '.-')
	#
	if dy_dx_break is None:
		dy_dx_break = dy_factor*dy_dx_0
		
	#print('dy_break: ', dy_break )
	#
	dy = 0.
	output_data = [data_in[0]]
	for j, (x,y) in enumerate(data_in[1:]):
		dydx = dy_dx[j]
		#dydx = (y-data_in[j][1])/(x-data_in[j][0])
		#
		if abs(dydx)>dy_dx_break:
			#print('adjust dy by: ', (y-data_in[j][1]))
			dy -= (y-data_in[j][1])
		output_data += [[x,y+dy]]
	#
	return output_data
		
#
def get_sub_sequence_indices(data_in, dt_0=None, t_col=0, dt_0_factor=1.5):
	# a more general split_sequence_by_dt() like tool. find large discontinuities in data_in[t_col];
	# return a list if indices that mark the start of subsequences. append also len(data_in), so all subsequences are
	# defined by full_sequence[get_sub_sequence_indices()[j-1:j]]
	#
	# first, get intervals on X[t_col]:
	#print("tcol: ", t_col)
	intervals = [rw[t_col] - data_in[j][t_col] for j,rw in enumerate(data_in[1:])]
	dt_0 = (dt_0 or numpy.median([x for x in intervals if x>0]))  # filter out the dt=0 data. these should not exist, but errors in firmware produce
	#															  # some junk data, in this case the same record is repeated over and over.
	#
	
	dt_break = dt_0_factor*dt_0
	#
	#sub_sequence_indices = [0] + [j+1 for dt,j in enumerate(intervals) if dt>dt_break] + [len(data_in)]
	#
	# note: it is possible that this will give us repeated values at the start/finish. the simplest solution is to use set(X).
	# is it faster to write a copy of the list and use if() to truncate the ends? particularly, by the time we re-sort the indices
	# (becasue set() does not preserve order). all of that said, i think if we get repeaded indices, it might actually be because
	# the sequences are actually broken, so let's just keep it for now.
	#
	return [0] + [j+1 for j,dt in enumerate(intervals) if dt>dt_break] + [len(data_in)]
#
def split_sequence_by_dt(data_in, dt_0=None, dt_0_factor=1.5, fignum=None):
	'''
	# break up sequence into sub-sequences separated by dt>dt_0.
	# after it works, port it to dosimeter_board or veriipy or something like that.
	# assume list-like and that t are in col 0 and x are in col 1. ([[t,x], ...])
	# ... and for now, assume list-like.
	# @ dt_0: expected interval; split for dt>dt_0
	# @ dt_0_factor: ... times this factor; split for dt>dt_0_factor*dt_0 (allow for a bit of variation)
	#
	# TODO: add an option to return the sequence start (and stop?) indices. probably the easiest/best way to
	# to this is to return a dict object like {j_start:[data], }
	'''
	#
	#print('data_in: ', data_in[0:10])
	dt_0 = (dt_0 or numpy.median([rw[0]-data_in[j][0] for j,rw in enumerate(data_in[1:])]))
	#print("dt_0: ", dt_0)
	#
	working_datas = [list(data_in[0]) + [0.]] + [[rw[0], rw[1], rw[0]-data_in[j][0]] for j,rw in enumerate(data_in[1:])]
	#print('working_datas: ', working_datas[0:10])
	#
	measurement_sequences = [[]]
	for rw in working_datas:
		#if rw[2]>dt_0_factor*dt_0 and not len(measurement_sequences[-1])==0:
		if rw[2]>dt_0_factor*dt_0:
			#print("new sequence...")
			measurement_sequences+=[[]]
			#
		measurement_sequences[-1] += [rw[0:2]]
		#
	#
	# fignum, for diagnostics:
	if not fignum is None:
		plt.figure(fignum)
		plt.clf()
		for seq in measurement_squences:
			plt.plot(*zip(*seq), ls='-', marker='.')
	#
	return measurement_sequences
#
def make_zeroed_working_copy(ary, cols=['PC1', 'PC2', 'PC3', 'PC4', 'PC5', 'PC6', 'PC7']):
	new_ary = ary.copy()
	l_ary = len(ary)
	for col in cols: new_ary[col]=numpy.zeros(l_ary)
	return new_ary
#
def modulus_stitch_1D(X, x_min=0., x_max=8.0, by_reff=False):
	#
	# stitch together a sequence on the assumption that large discontinuities are modulus errors.
	# since we can't guarantee the starting point, allow for gt and lt errors.
	if x_min is None: x_min = min(X)
	if x_max is None: x_max = max(X)
	delta_x = x_max - x_min
	#
	if not by_reff: X_working = X.copy()
	
	for j,x0 in enumerate(X_working[1:]):
		# summary of what we're doing (then in compact notation at the end).
		# this looks pretty de-optimized, but we want make this a running correction, so we actually need to build our copy as we go,
		# as opposed to using a list comprehension syntax.
		#
		#x0 = x
		#x_plus  = x0 + delta_x
		#x_minus = x0 - delta_x
		#print('**xx: ', x0, x_plus, x_minus)
		#
		#print('rw: ', [[x, (x-X[j])**2.] for x in [x0, x0+delta_x, x0-delta_x]])
		#deltas = [[x, (x-X[j])**2.] for x in [x0, x0+delta_x, x0-delta_x]]
		#new_x = min([[x, (x-X_working[j])**2.] for x in [x0, x0+delta_x, x0-delta_x]], key=lambda rw: rw[1])[0]
		#new_x = min(deltas, key=lambda rw: rw[1])[0]
		#
		X_working[j+1] = min([[x, (x-X_working[j])**2.] for x in [x0, x0+delta_x, x0-delta_x]], key=lambda rw: rw[1])[0]
	
	return X_working
#
class Element_Indices(list):
	def __init__(self, X=None, prms=None):
		'''
		# @X: sequence to be searched
		# @prms: a list(line) object of target parameter values, for which we want indices
		# returns: a list(like) object containing the interpolated index values. note that
		#		 though these are meant to be indices, they are retunred as floats, to reflect
		#		 the relative position of the input parameter value and the incrementation of X.
		#		 it is assumed that the user can handle the integer conversion externally,
		#		 ie, int(round(x)), int(x), int(ceil(x)), etc.
		'''
		#
		if X is None:
			raise ValueError('X cannot be None')
		#
		# TODO: get j_indices for new time domain definitions.
		# handle some default behavior, in case params are not in X
		j_prms = [None if p>X[0] else 0  for p in prms]
		j_prms[-1] = len(X)
		#
		for j,(x1,x2) in enumerate(zip(X[:-1], X[1:])):
			#
			for k,p in enumerate(prms):
				if p>x1 and p<=x2:
					j_prms[k] = j + (p-x1)/(x2-x1)
			#
			# ... and here we should code up a way to exit the loop when all parameters are discovered.
			#   in general, this proces is not fully optimized for a sorted sequence, but it should be
			#   ok for most of our applications (for now)
			#
			# we want to break the loop when we exceed the max date, but we don't know that just yet;
			# training might occur after predicting. we should reorganize this to use a data structure
			# instead of free-form variables, but for now just loop through the rest of the data...
		#
		del j,x1,x2,k,p
		self.__dict__.update({key:val for key,val in locals().items() if not key in ('self', '__class__')})
		#return j_prms
		super(Element_Indices, self).__init__(j_prms)
#
class Sequence_Simulator(list):
	# create a simulated sequence. this class will be very simple, assuming shot-type noise with a gauss
	# distribution. nominally, use this as a base class for variants and possibly more sophisticated
	# seqnece models.
	# TODO: do we want to populate self with [[t,x], ...]? permit just populating with [x..]? keep the t,x
	# arrays internally? the main question is, if we to generate a set of seqeunces (see Simulated_Sequences_dict),
	# we have to choose between keeping [x,y] pairs (which is cumbersome) or dumping the sequence functionality, so we
	# can't load a set of sequences, then add dose, etc. to them. in the end, it looks like a lot of tradeoff between
	# intuitive default behavior and added functinoality...
	#
	def __init__(self, t_start=0., t_stop=500., dt_interval = 1., noise_sigma=1.,
				dose_magnitude=-10., dose_start=None, time_axis=None, dose_stop=None, output_file_name=None, temp_flg='False'):
		# default time input in hours (i mean, it's whatever we want it to be, until we do datetime
		# conversions.)
		# TODO: generalize to accept multiple doses 
		#
		dt_interval = dt_interval or self.dt_interval
		noise_sigma = noise_sigma or self.noise_sigma
		temp_flg = temp_flg or self.temp_flg
		if time_axis is None:
			time_axis   = numpy.arange(t_start, t_stop, dt_interval)
		#
		dose_start = dose_start or (t_stop-t_start)/2.
		# for convenience, if this is a "step" function, just set it to a finite slope of less than one interval.
		dose_stop  = dose_stop or (dose_start + .5*dt_interval)
		dose_stop = max(dose_stop, dose_start + .5*dt_interval)
		#
		# update:
		self.__dict__.update({key:val for key,val in locals().items() if not key in ('self', '__class__')})
		#
		# construct base sequence:
		seq = self.get_base_sequence()
		#super(Sequence_Simulator,self).__init__(seq)
		#print('**DEBUG: ', seq[0:5])
		#
		#seq = self.add_dose(seq)
		self.add_dose(seq, update_self=True)
		#
		#super(Sequence_Simulator,self).__init__(seq)
		if not (output_file_name is None or str.strip(output_file_name)==''):
			self.export_to_csv(output_file)
	#
	def export_to_csv(self, output_file='simulated_timeseries.csv', delim='\t'):
		pth,fl = os.path.split(output_file)
		if not os.path.isdir(pth) and not pth=='':
			os.makedirs(pth)
		#
		del pth,fl
		with open(output_file, 'w') as fout:
			fout.write('#simulated sequence\n')
			fout.write('#!noise_sigma={}, dose_magnitude={}, dose_start={}, dose_stop={}\n'.format(self.noise_sigma, self.dose_magnitude, self.dose_start, self.dose_stop))
			#
			for x,y in self:
				fout.write('{}{}{}\n'.format(x, delim,y))
			#
		#
		return None
	#
	#def get_base_sequence(self, t_start=None, t_stop=None, dt_interval=None, noise_sigma=None):
	def get_base_sequence(self, time_axis=None, noise_sigma=None):
		#t_start = t_start or self.t_start
		#t_stop = t_stop or self.t_stop
		#dt_interval = dt_interval or self.dt_interval
		#noise_sigma = noise_sigma or self.noise_sigma
		#
		time_axis = time_axis or self.time_axis
		noise_sigma = noise_sigma or self.noise_sigma
		#
		#X = numpy.arange(t_start, t_stop, dt_interval)
		if self.temp_flg==True: return numpy.array([time_axis, numpy.random.normal(loc=20, scale=0, size=len(time_axis))]).T
		else: return numpy.array([time_axis, numpy.random.normal(loc=0, scale=noise_sigma, size=len(time_axis))]).T
	#
	def add_dose(self, seq=None, dose_start=None, dose_stop=None, dose_magnitude=None, do_copy=True, update_self=True):
		if seq is None: seq = self
		#
		# we might be having some issues with change-in-place inconsistencies, so let's make a copy:
		if do_copy: seq = numpy.copy(seq)
		#
		dose_start = dose_start or self.dose_start
		dose_stop =  dose_stop or self.dose_stop
		dose_magnitude = dose_magnitude or self.dose_magnitude
		#
		dose_slope = dose_magnitude/(dose_stop - dose_start)
		#print('***DEBUG seq: ', seq[0:5])
		#
		calc_change = True
		for j, (t,x) in enumerate(seq):
			if t > dose_start:
				if calc_change:
					dy = dose_slope*(min(t, dose_stop) - dose_start)
				#
				# ... and now, expedite:
				if t>=dose_stop: calc_change = False
				seq[j][1] += dy
		#
		if update_self: super(Sequence_Simulator,self).__init__(seq)
		return seq
	#
	@property
	def X(self):
		return [x for t,x in self]
	
class Simulated_sequences_dict(dict):
	def __init__(self, t_start=0., t_stop=500., dt_interval = 1., time_axis=None,
				 seq_names=['pc2', 'pc4', 'pc5', 'pc6'],
				 noise_sigmas=1., dose_magnitudes=-10., dose_starts=None, dose_stops=None, output_file_name=None):
		#
		# TODO: start using new matplotlib color iterators...
		self.colors_ = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
		#
		# construct a time-axis:
		dt_interval = dt_interval or self.dt_interval
		if time_axis is None:
			time_axis   = numpy.arange(t_start, t_stop, dt_interval)
		# handle inputs:
		# TODO: can in do this with pointers?
		if numpy.ndim(noise_sigmas)==0: noise_sigmas = [noise_sigmas for _ in seq_names]
		while len(noise_sigmas)<len(seq_names): noise_sigmas += [noise_sigmas[-1]]
		#
		if numpy.ndim(dose_magnitudes)==0: dose_magnitudes = [dose_magnitudes for _ in seq_names]
		while len(dose_magnitudes)<len(seq_names): dose_magnitudes += [dose_magnitudes[-1]]
		#
		if numpy.ndim(dose_starts)==0: dose_starts = [dose_starts for _ in seq_names]
		while len(dose_starts)<len(dose_starts): dose_starts += [dose_starts[-1]]
		
		if numpy.ndim(dose_stops)==0:  dose_stops  = [dose_stops for _ in seq_names]
		while len(dose_stops)<len(dose_stops): dose_stops += [dose_stops[-1]]
		#
		self.__dict__.update({key:val for key,val in locals().items() if not key in ('self', '__class__')})
		#
		#self.update({col:Sequence_Simulator(t_start=t_start, t_stop=t_stop, dt_interval=dt_interval,
		#				noise_sigma=sig, dose_magnitude=mag, dose_start=dt1, dose_stop=dt2) 
		#			 for col, sig, mag, dt1, dt2 in 
		#			zip(seq_names, noise_sigmas, dose_magnitudes, dose_starts, dose_stops)})
		#self.update({col:[y for x,y in Sequence_Simulator(time_axis=time_axis,
		#				noise_sigma=sig, dose_magnitude=mag, dose_start=dt1, dose_stop=dt2)] 
		#			 for col, sig, mag, dt1, dt2 in 
		#			zip(seq_names, noise_sigmas, dose_magnitudes, dose_starts, dose_stops)})
		self.update({col:Sequence_Simulator(time_axis=time_axis,
						noise_sigma=sig, dose_magnitude=mag, dose_start=dt1, dose_stop=dt2).X 
					 for col, sig, mag, dt1, dt2 in 
					zip(seq_names, noise_sigmas, dose_magnitudes, dose_starts, dose_stops)})
		#
		if not (output_file_name is None or str.strip(output_file_name)==''):
			self.export_to_csv(output_file)
	#
	def export_to_csv(self, output_file='simulated_timeseries_array.csv', delim='\t'):
		pth,fl = os.path.split(output_file)
		if not os.path.isdir(pth) and not pth=='':
			os.makedirs(pth)
		#
		del pth,fl
		with open(output_file, 'w') as fout:
			fout.write('#simulated sequence\n')
			#fout.write('#!noise_sigma={}, dose_magnitude={}, dose_start={}, dose_stop={}\n'.format(self.noise_sigmas, self.dose_magnitudes, self.dose_starts, self.dose_stops))
			fout.write('#!time{}'.format(delim) + delim.join(self.seq_names) + '\n')
			#
			for rw in numpy.array([list(self.time_axis)] + [self[col] for col in self.seq_names]).T:
				fout.write('{}\n'.format(delim.join([str(x) for x in rw])))
			#
		#
		return None
	#
	#
	def add_dose(self, col=None, seq=None, dose_start=None, dose_stop=None, dose_magnitude=None, do_copy=True):
		if col is None and seq is None:
			raise ValueError('Input parameters col and seq cannot both be None.')
		#
		if seq is None: 
			seq = self[col]
		#
		# we might be having some issues with change-in-place inconsistencies, so let's make a copy:
		if do_copy: seq = numpy.copy(seq)
		#
		dose_start = dose_start or self.dose_start
		dose_stop =  dose_stop  or self.dose_stop
		dose_magnitude = dose_magnitude or self.dose_magnitude
		#
		dose_slope = dose_magnitude/(dose_stop - dose_start)
		#
		calc_change = True
		for j, (t,x) in enumerate(seq):
			if t>dose_start:
				if calc_change:
					dy = dose_slope*(min(t, dose_stop) - dose_start)
				#
				# ... and now, expedite:
				if t>=dose_stop: calc_change = False
				seq[j][1] += dy
		#
		return seq
	#
	def get_sequence(self, col):
		return numpy.array([self.time_axis, self[col]]).T
	#
	def plot_sequences(self, ax=None, ls='-', marker='', lw=1.5):
		# simple plot of sequences. primarily intended for diagnostics; more complex plots
		# should be handled offline.
		if ax is None:
			fg = plt.figure()
			plt.clf()
			ax = plt.gca()
		#
		for col,seq in sorted(self.items(), key=lambda rw:rw[0]):
			plt.plot(self.time_axis, seq, ls='-', marker='', lw=lw, label=col)
		plt.legend(loc=0)
		
#
