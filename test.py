import copy
import pandas as pd


# class DataFrameWithHistory(pd.DataFrame):
#     _history = []
#     def __init__(self, *args, **kwargs):
#         print('__init__')
#         super().__init__(*args, **kwargs)
#         self._history = []

#     def __setattr__(self, name, value):
#         print(f'__setattr__: {name} : {value}')
#         self._save_history('__setattr__', name, value)
#         super().__setattr__(name, value)

#     def __setitem__(self, key, value):
#         print(f'__setitem__: {key} : {value}')
#         self._save_history('__setitem__', key, value)
#         super().__setitem__(key, value)

#     def __delitem__(self, key):
#         self._save_history('__delitem__', key)
#         super().__delitem__(key)

#     def _save_history(self, method_name, *args):
#         self._history.append((method_name, *copy.deepcopy(args)))

# df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
# df = DataFrameWithHistory({'A': [1, 2, 3], 'B': [4, 5, 6]})
# df.iloc[0, 0] = 10
# df.drop('B', axis=1, inplace=True)
# df.iloc[0, 0] = 11
# print('=================================')
# for i in df._history:
#     print(i)
#     print('---------------------------------------------')
# # # Output: [('__setitem__', (0, 0), 10), ('drop', 'B', 1, None)]
# # df = df.iloc[0:2]
# # #print(type(df))
# df = DataFrameWithHistory({'A': [1, 2, 3], 'B': [4, 5, 6]})
# df.iloc[0, 0] = 11
# df['B'] = [2, 2, 2]
# print('=================================')
# for i in df._history:
#     print(i)
#     print('---------------------------------------------')

# print(df)


# import pandas as pd

# class MyDataFrame(pd.DataFrame):
#     def __setitem__(self, key, value):
#         print(f"Setting value {value} at index {key}")
#         super().__setitem__(key, value)

# df = MyDataFrame({'A': [0, 1, 2], 'B': [3, 4, 5], 'C': [6, 7, 8]})
# print(df)

# df.iloc[1, 1] = 1
# print(df)

import inspect

class Parent:
    def some_method(self):
        caller_class = type(self).__name__
        caller_method = inspect.currentframe().f_back.f_code.co_name
        print(f"Method {caller_method} of class {caller_class} called some_method")

class Child(Parent):
    def another_method(self):
        super().some_method()

c = Child()
c.another_method() 





