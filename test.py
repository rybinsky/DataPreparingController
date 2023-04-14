import copy
import pandas as pd


class DataFrameWithHistory(pd.DataFrame):
    _history = []
    def __init__(self, *args, **kwargs):
        print('__init__')
        super().__init__(*args, **kwargs)
        self._history = []

    def __setattr__(self, name, value):
        print(f'__setattr__: {name} : {value}')
        self._save_history('__setattr__', name, value)
        super().__setattr__(name, value)

    def __setitem__(self, key, value):
        print(f'__setitem__: {key} : {value}')
        self._save_history('__setitem__', key, value)
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self._save_history('__delitem__', key)
        super().__delitem__(key)

    def _save_history(self, method_name, *args):
        self._history.append((method_name, *copy.deepcopy(args)))

df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
df = DataFrameWithHistory({'A': [1, 2, 3], 'B': [4, 5, 6]})
df.iloc[0, 0] = 10
df.drop('B', axis=1, inplace=True)
df.iloc[0, 0] = 11
print('=================================')
for i in df._history:
    print(i)
    print('---------------------------------------------')
# # Output: [('__setitem__', (0, 0), 10), ('drop', 'B', 1, None)]
# df = df.iloc[0:2]
# #print(type(df))
df = DataFrameWithHistory({'A': [1, 2, 3], 'B': [4, 5, 6]})
df.iloc[0, 0] = 11
df['B'] = [2, 2, 2]
print('=================================')
for i in df._history:
    print(i)
    print('---------------------------------------------')

print(df)
