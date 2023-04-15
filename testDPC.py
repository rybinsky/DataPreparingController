import typing as tp
import numpy as np
import pandas as pd
import unittest

from DPCclass import (
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
dpc._history.print_dll()
print('========================================3')
dpc.data['a'] += 1
print('========================================4')
print()
print('========================================5')
dpc.data.drop(columns = 'c', axis = 1, inplace = True)
print('========================================6')
dpc.data['yyy'] = [2, 2, 2]
print('========================================7')
dpc.data.drop(columns = 'a', axis = 1, inplace = True)
print('========================================8')
dpc._history.print_dll()
print(dpc.data)
print('----------------------1')
dpc._rollback()
print('----------------------2')
dpc._history.print_dll()
print('----------------------3')
print(dpc.data)
print('----------------------4')
dpc._history.print_dll()
print('----------------------5')
dpc._rollback()
print('----------------------6')
print(dpc.data)
print('----------------------7')
dpc._history.print_dll()

















