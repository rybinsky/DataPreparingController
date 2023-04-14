import typing as tp
import numpy as np
import pandas as pd
import unittest

from OutController import (
    DataPreparingController
)

class TestDPC(unittest.TestCase):
    pass




data = np.array([(1, 2, 3), (4, 5, 6), (7, 8, 9)],
                dtype=[("a", "i4"), ("b", "i4"), ("c", "i4")])

df3 = pd.DataFrame(data, columns=['c', 'a'])
print('========================================1')

dpc = DataPreparingController(df3)
print('========================================2')
dpc.history.print_dll()
print('========================================3')
dpc.data['a'] += 1
print('========================================4')
dpc.data.iloc[1, 1] = 100
print('========================================5')
dpc.data.drop('c', axis=1, inplace=True)
print('========================================6')
dpc.data['yyy'] = [2, 2, 2]
print('========================================7')
dpc.history.print_dll()


















