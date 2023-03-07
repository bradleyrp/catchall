#!/usr/bin/env python
# vim: noet:ts=4:sts=4:sw=4

import unittest
import numpy as np
import random
import timeit

from catchall.ext import standard_dev

def stddev_benchmark(*,testseq=None):
    """
    Benchmark the Standard Deviation Tests.
    """
    if not testseq:
        testseq = range(1000, 20000, 1000)
    lp_time = []
    py_time = []
    np_time = []
    c_time = []
    for l in testseq:
        rands = [random.random() for _ in range(0, l)]
        numpy_rands = np.array(rands)
        np_time = np.append(np_time,
            timeit.timeit(lambda: np.std(numpy_rands), number=1000))
        c_time = np.append(c_time,
            timeit.timeit(lambda: standard_dev(rands), number=1000))
    data = np.array([np.transpose(np_time), np.transpose(c_time)])
    return data

class TestStdDev(unittest.TestCase):

    def test_bench(self):
        return stddev_benchmark()

if __name__ == '__main__':
    unittest.main()

