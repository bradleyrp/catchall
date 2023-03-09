import numpy as np
import random
import timeit
import pandas as pd
# in jupyter: %matplotlib inline
from matplotlib import pyplot as plt

from catchall.test_stddev import stddev_benchmark

data = stddev_benchmark()
lengths = data[0]
data_results = data[1:]

df = pd.DataFrame(data_results.transpose(), index=lengths, columns=['Numpy', 'C++'])
plt.figure()
df.plot()
plt.legend(loc='best')
plt.ylabel('Time (Seconds)')
plt.xlabel('Number of Elements')
plt.title('1k Runs of Standard Deviation')
plt.savefig('numpy_vs_c.png')
plt.show()