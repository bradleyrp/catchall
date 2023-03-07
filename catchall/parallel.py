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
	return compute_worker(
		address=f'result-{rank}',
			do_lock=False,
			kwargs_h5=kwargs_h5)