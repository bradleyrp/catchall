#!/usr/bin/env python
# vim: noet:ts=4:sts=4:sw=4

import os
import time
import datetime as dt
import h5py
from h5py import File as h5pyFile
import numpy as np
from .test_stddev import stddev_benchmark

class H5WriteLocker(h5pyFile):
	"""
	Queue writes to a single HDF5 file.
	"""
	def __init__(self,*args,do_lock=True,**kwargs):
		probe_interval = kwargs.pop("probe_interval", 1)
		self._lock = "%s.lock" % args[0]
		self._do_lock = do_lock
		if not self._do_lock:
			super().__init__(*args,**kwargs)
			return
		# standard locking behavior
		while True:
			try:
				# via: https://stackoverflow.com/a/29014295
				self._flock = os.open(self._lock, 
					os.O_CREAT | os.O_EXCL | os.O_WRONLY)
				break
			except FileExistsError:
				print('sleeping')
				time.sleep(probe_interval)
		# remove the lock on failures or else the next run fails
		try:
			super().__init__(*args,**kwargs)
		except Exception as e:
			self.__exit__()
			raise
	def __exit__(self, *args, **kwargs):
		super().__exit__(self, *args, **kwargs)
		if self._do_lock:
			os.close(self._flock)
			os.remove(self._lock)

def traverse_datasets(hdf_file):
	"""
	Read nested arbitrary datasets with h5py.
	"""
	# via: https://stackoverflow.com/a/51548857
	def h5py_dataset_iterator(g, prefix=''):
		for key in g.keys():
			item = g[key]
			path = f'{prefix}/{key}'
			if isinstance(item, h5py.Dataset): # test for dataset
				yield (path, item)
			elif isinstance(item, h5py.Group): # test for group (go down)
				yield from h5py_dataset_iterator(item, path)
	for path, _ in h5py_dataset_iterator(hdf_file):
		yield path

def save(data,filename,address,subkey,
	do_lock=True,kwargs_h5=None,write_mode=None,atomic=True):
	"""
	Save data to an H5 file via queue with a consistent naming scheme.
	"""
	if kwargs_h5 == None:
		kwargs_h5 = {}
	if write_mode == None:
		write_mode = 'a'
	if write_mode not in ['a','w']:
		raise Exception(f'invalid write mode: {write_mode}')
	# make sure you use append or you will be severely confused!
	with H5WriteLocker(filename,write_mode,do_lock=do_lock,**kwargs_h5) \
		as store:
		# dev: consider setting atomic when using MPI with store.atomic
		keys = store.keys()
		key = os.path.join(address,subkey)
		head,tail = os.path.dirname(key),os.path.basename(key)
		try: 
			try: 
				store.require_group(head)
				# store.create_group(head)
			# dev: more clear exception
			except:
				pass
			group = store[head]
			if tail in group.keys():
				print(
					f'warning: possible collision on key {key} hence discard')
				return
			group.create_dataset(tail,
				data=data,
				dtype=data.dtype.str)
		except Exception as e:
			print(
				f'error: failing to serialize type {data.dtype.str}: {data}, '
				f'exception {e}')
			raise

def get_filename():
	"""Work with a file in the current directory."""
	filename = os.path.abspath(os.path.join(os.getcwd(),'output.h5'))
	return filename

def compute_worker(num=None,address=None,
	do_lock=True,kwargs_h5=None,write_mode=None):
	"""
	Perform a series of standard deviation benchmark calculations as an example.
	Uses the `save` function which relies on `H5WriteLocker` to queue writes. 
	"""
	if num == None:
		raise Exception(f'need a number of iterations, received {num}')
	# in catchall.parallel, we add rank to the seed, here we decrement one
	np.random.seed(746574366 - 1)
	if kwargs_h5 == None:
		kwargs_h5 = {}
	if address == None:
		address = 'result'
	filename = get_filename()
	it = 0
	while True:
		# select the appropriate interval, recording milliseconds here
		ts = (dt.datetime.strftime(
			dt.datetime.now(),'%Y.%m.%d.%H%M.%S.%f')[:-3])
		print(f'status: iteration at {ts}')
		data_this = stddev_benchmark(
			# use a larger sequence for the test so we can watch the parallel
			#   writes inside the log
			testseq=range(1000, 20000, 1000))
		save(
			data=data_this,
			filename=filename,
			address=address,
			subkey=ts,
			do_lock=do_lock,
			write_mode=write_mode,
			kwargs_h5=kwargs_h5)
		read_output(verbose=False)
		it += 1
		if num != None and it >= num:
			break

def read_output(verbose=False):
	"""Traverse paths in the output."""
	filename = get_filename()
	with h5pyFile(filename,'r') as store:
		nitems = 0
		for path in traverse_datasets(store):
			if verbose:
				print(path)
			nitems += 1
	print(f'status: file {filename} has {nitems} results')

