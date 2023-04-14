# import pandas as pd

# class DataFrameHistory(pd.DataFrame):
#     def __init__(self, *args, **kwargs):
#         print('__init__')
#         super().__init__(*args, **kwargs)
#         self._history = [self.copy()]
    
#     def __getattribute__(self, item):
#         print('__getattribute__, ', item)
#         attr = super().__getattribute__(item)
#         if isinstance(attr, pd.DataFrame):
#             return DataFrameHistory(attr)
#         else:
#             return attr
    
#     def __setattr__(self, key, value):
#         print('__setattr__')
#         super().__setattr__(key, value)
#         self._history.append(self.copy())

# # Создаем объект DataFrameHistory
# df = DataFrameHistory({'A': [1, 2, 3], 'B': [4, 5, 6]})
# print('=============================1')
# # Изменяем датасет
# df['C'] = [7, 8, 9]
# print('============================2')
# # Просмотр истории изменений
# for i, hist in enumerate(df._history):
#     print(f'История изменений № {i}:')
#     print(hist)
#     print()

# # Удаляем столбец
# del df['B']
# print('=============================3')
# # Просмотр истории изменений
# for i, hist in enumerate(df._history):
#     print(f'История изменений № {i}:')
#     print(hist)
#     print()

# import copy

# class Person(list):
#     # value = None
#     # name = None
#     # age = None
#     # arr = None
#     _history = None
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age
#         self._history = []

#     def __setattr__(self, name, value):
#         print(f'__setattr__ : {name}: {value}')
#         #print(bool(self._history))
#         if name == 'age' and self._history is not None:
#             print('-----------------------------------------------')
#             self._history.append(copy.deepcopy(self.age))
#             print('-----------------------------------------------')
#         # if self.value != value:
#         #     if name not in self._history:
#         #         self._history[name] = [value]
#         #     else:
#         #         self._history[name].append(value)

#         super().__setattr__(name, value)

#     def __setitem__(self, key, value):
#         print(f'__setitem__ : {key}: {value}')
#         self.age = super().__setitem__(key, value)

#     def __getitem__(self, name):
#         print(f'__getitem__ : {name}')
#         if name == 'age':
#             return self.age[name]
        
#     def __getattribute__(self, name):
#         print('__getattribute__ :', name)
#         value = super().__getattribute__(name)
#         print(name, ' : ', value)
#         # if name == 'age':
#         #     print(1)
#         #     if name not in self._history:
#         #         print(2)
#         #         #self._history.append(value)
#         #     elif value != self._history[name][-1]:
#         #         print(3)
#                 #self._history.append(value)

#         return value


# print('=================================1')
# person = Person("Alice", [1, 2, 3])
# print('=================================2')
# person.age  = [4, 5, 6]
# print(person._history, person.age)
# print('=================================3')
# #print(person._history, person.age)
# print('=================================4')
# person.age[1] = 10
# print(person._history, person.age)
# print('=================================5')
# person.age = [0, 0, 0]
# print(person._history, person.age)
# # {'name': ['Alice', 'Bob', 'Charlie'], 'age': [25, 30, 35]}


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
