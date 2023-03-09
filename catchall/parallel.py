#!/usr/bin/env python
# vim: noet:ts=4:sts=4:sw=4

import h5py
from mpi4py import MPI
from .work import compute_worker

def compute_worker_parallel(num=None):
	"""
	Worker for a single parallel process that writes to a collective H5 file.
	"""
	# note that we include the rank in the structure of the data
	rank = MPI.COMM_WORLD.rank
	# if you do not use the right driver, and you do not implement your own
	#   locking system, you will eventually get a BlockingIOError just try
	#   padding some writes and turning off the driver below to see
	kwargs_h5 = dict(
		driver='mpio',
		comm=MPI.COMM_WORLD,)
	# set a random seed by rank
	np.random.seed(746574366 + rank)
	# dev: if you attach rank to result, you get an error that seems to be 
	#   related to the warning on the docs, see
	#     https://docs.h5py.org/en/latest/\
	#        mpi.html#collective-versus-independent-operations
	#   that says "all processes must do this". the easiest solution is to use
	#   the same group address. another option is to require_group in each of 
	#   the ranks, which probably organizes the format of the data
	#   related error is
	#     File "h5py/h5g.pyx", line 166, in h5py.h5g.create
	#     ValueError: Unable to create group (bad symbol table node signature)
	return compute_worker(
		address=f'result',
		do_lock=False,
		write_mode='a',
		kwargs_h5=kwargs_h5)