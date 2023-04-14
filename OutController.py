import typing as tp
import numpy as np
import pandas as pd
import copy

# from utils import (
#     _iqr_outliers_percent,
#     _missing_values_table
# )

'''
Мини-проект по созданию удобного предобработчика файлов
'''

def _iqr_outliers_percent(df: pd.DataFrame, columns, threshold):
    '''
    Приватная функция выводит процент выбросов в столбцах columns матрицы признаков df
    '''
    drop_cols = []
    
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers_count = df[(df[col] < lower_bound) | (df[col] > upper_bound)].shape[0]
        total_count = df[col].shape[0]
        outliers_percent = outliers_count / total_count * 100

        if outliers_percent < threshold:
            drop_cols.append(col)
        print(f'{col}: {outliers_percent:.2f}%')
    
    return drop_cols


def _missing_values_table(df: pd.DataFrame):
    '''
    Приватный вычисляет процент пропущенных значений в каждом столбце
    '''
    mis_val = df.isnull().sum()
    mis_val_percent = 100 * df.isnull().sum() / len(df)
    mis_val_table = pd.concat([mis_val, mis_val_percent], axis = 1)
    mis_val_table_ren_columns = mis_val_table.rename(
    columns = {0 : 'Missing Values', 1 : '% of Total Values'})
    mis_val_table_ren_columns = mis_val_table_ren_columns[
        mis_val_table_ren_columns.iloc[:, 1] != 0].sort_values(
        '% of Total Values', ascending = False).round(1)
        
    print ("Your selected dataframe has " + str(df.shape[1]) + " columns.\n"      
            "There are " + str(mis_val_table_ren_columns.shape[0]) +
            " columns that have missing values.")
    
    return mis_val_table_ren_columns


class Node:
    def __init__(self, value = None, prev = None, next = None):
        self.value = value
        self.prev = prev
        self.next = next

class DoublyLinkedList:
    def __init__(self, max_size = 5):
        print('__init__ DLL')
        try:
            if max_size <= 0:
                raise ValueError(f"'max_size' должен быть больше 0")
            self.head = None
            self.tail = None
            self.size = 0
            self.max_size = max_size
        except ValueError as e:
            print(e)

    def is_empty(self):
        return self.size == 0

    def __len__(self):
        return self.size

    def __lpush(self, value):
        try:
            if self.size == self.max_size:
                raise ValueError(f"Достигнут максимальный размер списка!")
            new_node = Node(value)
            if self.is_empty():
                self.head = self.tail = new_node
            else:
                new_node.next = self.head
                self.head.prev = new_node
                self.head = new_node
            self.size += 1
        except ValueError as e:
            print(e)

    def push(self, value):
        print('push DLL')
        new_node = Node(value)
        if self.size == self.max_size:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
            self.head = self.head.next
            self.head.prev = None
        else:
            if self.is_empty():
                self.head = self.tail = new_node
            else:
                new_node.prev = self.tail
                self.tail.next = new_node
                self.tail = new_node
            self.size += 1

    def pop(self):
        print('pop DLL')
        if self.is_empty():
            raise Exception("Список пуст!")
        removed_node = self.head
        if self.head == self.tail:
            self.head = self.tail = None
        else:
            self.head = self.head.next
            self.head.prev = None
        self.size -= 1
        return removed_node.value

    def __rpop(self):
        if self.is_empty():
            raise Exception("Список пуст!")
        removed_node = self.tail
        if self.head == self.tail:
            self.head = self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.next = None
        self.size -= 1
        return removed_node.value
    
    def resize(self, new_max_size):
        '''
        Изменяет МАКСИМАЛЬНЫЙ допустимый размер списка
        '''
        print('resize DLL')
        if self.size < new_max_size:
            pass
        elif self.size > new_max_size:
            for _ in range(new_max_size, self.size):
                self.__rpop()
            self.size = new_max_size
        self.max_size = new_max_size

    def print_dll(self):
        print('print DLL')
        current_node = self.head
        while current_node:
            print(current_node.value)
            current_node = current_node.next
'''
aelfapfokapofekapoefk
aokef[ekafa
efo
afkoaoekfaoefoka
efkoa
ef[oa[
    kefo[
        akf[ka
        fe[k
        aef
        [akoef
        aef]]
    ]
]]]
'''

class MyDataFrame(pd.DataFrame):
    '''
    Класс позволяет возвращать измененный pd.DataFrame
    '''
    history = DoublyLinkedList(max_size = 3)

    def __init__(self, *args, **kwargs):
        print('__init__ MyDF')
        super().__init__(*args, **kwargs)
        #self.history = DoublyLinkedList(max_size = 3)

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
        self.history.push((method_name, *copy.deepcopy(args)))

    
class DataPreparingController(MyDataFrame):
    '''
    Этот класс помогает упрощать предобработку данных и
    делать из них статистические выводы.
    '''
    __MAX_HISTORY_LEN = 10

    data: MyDataFrame = None

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    def __init__(self, data: pd.DataFrame):
        self.data = MyDataFrame(data)

    def __setattr__(self, name, value):
        #print(f'__setattr__ {name} : {value} DPC')
        super().__setattr__(name, value)

    def __getattribute__(self, name):
        #print('__getattribute__ DPC__:', name)
        return super().__getattribute__(name)
   
    # def __setitem__(self, key, value):
    #     print('__setitem__ DPC')
    #     self.history.push(self.data.copy())
    #     self.data = super().__setitem__(key, value)

    # def __delitem__(self, key):
    #     print('__set_item__ DPC')
    #     self.history.push(self.data.copy())
    #     self.data = super().__delitem__(key)


    def set_history_len(self, buffer_len: int):
        '''
        Description:
            Метод класса, устанавливающий длину хранящейся истории изменений
        
        Args:
            buffer_len (int): новая длина истории
        '''
        try:
            if buffer_len > self.__MAX_HISTORY_LEN:
                raise ValueError(f"Слишком большое значение {buffer_len}, \
                                максимальная длина должна быть <={self.__MAX_HISTORY_LEN}!")
            else:
                self.history.resize(buffer_len)
                print(f'Теперь будет храниться история на {self.__history.__len__()} шагов.')
        except ValueError as e:
            print(e)
        

    def сallback(self):
        '''
        Description:
            Откат последней продецуры изменения данных
        '''
        try:
            if self.history.is_empty:
                raise IndexError('Нет истории, чтобы сделать возврат!')
            self.data = self.history.pop()

        except IndexError as e:
            print(e)

    @classmethod
    def iqr_outliers_percent(
        cls,   
        df: tp.Optional[pd.DataFrame],
        columns: tp.Union[str, tp.List[str]] = 'all', 
        threshold: tp.Union[int, float] = 10
    ) -> tp.List[str]:
        '''
        Description:
            Метод выводит процент выбросов в столбцах columns матрицы признаков df

        Args:
            df (pd.DataFrame): матрица признаков
            columns (list): колонки, из которых удалять выбросы
            threshold (float): порог удаления выбросов из drop_cols в процентах

        Returns:
            drop_cols (list): список колонок, откуда можно удалить выбросы
        '''
        try:
            if threshold < 0 or threshold > 100:
                raise ValueError(f"Неверное значение 'threshold' {threshold}, \
                                должно быть на интервале [0, 100]!")

            if isinstance(pd.DataFrame, df):
                if columns == 'all':
                    columns = df.columns
                return _iqr_outliers_percent(df, columns, threshold)
            elif df is None:
                if columns == 'all':
                    columns = cls.data.columns
                return _iqr_outliers_percent(cls.data, columns, threshold)
            else:
                raise TypeError("'df' должен быть либо None и метод должен вызываться от объекта класса, \
                                либо pd.DataFrame и метод вызывается от имени класса")
            
        except TypeError as e:
            print(e)
        except ValueError as e:
            print(e)
    
    def remove_outliers(
        self, 
        df: pd.DataFrame,
        columns: tp.Union[str, tp.List[str]] = 'all',
        threshold: tp.Union[int, float] = 1.5, 
        drop_percent: tp.Union[int, float] = 100          
    ) -> pd.DataFrame:
        '''
        Description:
            Метод удаляет строки, в которых есть выбросы, \
            определенные по методу Тьюки (межквартильное расстояние)

        Args:
            df (pd.DataFrame): матрица признаков
            columns (list): список числовых признаков
            threshold (float): порог в методе Тьюки
            drop_percent (float): доля удаляемых выбросов

        Returns:
            df (pd.DataFrame): матрица признаков, очищенные от какой-то доли выбросов
        '''
        try:
            if threshold < 0:
                raise ValueError(f"Неверное значение 'threshold' {threshold}, \
                                должно быть неотрицательным!")
            if drop_percent < 0 or drop_percent > 100:
                raise ValueError(f"Неверное значение 'drop_persent' {drop_percent}, \
                                должно быть на промежутке [0, 100]")

            self.history.push(df.copy())

            bounds = []
            for column in columns:
                q1 = df[column].quantile(0.25)
                q3 = df[column].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - threshold * iqr
                upper_bound = q3 + threshold * iqr
                bounds.append((lower_bound, upper_bound))

            for (lower_bound, upper_bound), column in zip(bounds, columns):

                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)][column]
                outliers = outliers.sort_values()    
                n_to_remove = int(len(outliers) * drop_percent / 100)
                
                to_remove = outliers.head(n_to_remove).index.union(outliers.tail(n_to_remove).index)
                cleaned_col = df[column].drop(to_remove)
                df = df.loc[cleaned_col.index].copy()
                df.reset_index(drop = True, inplace = True)
                
            self.data = df.copy()
            return df
            
        except ValueError as e:
            print(e)


    @classmethod
    def missing_values_table(cls, df: tp.Optional[pd.DataFrame]) -> pd.DataFrame:
        '''
        Description:
            Метод вычисляет процент пропущенных значений в каждом столбце
        Args:
            df (pd.DataFrame): матрица признаков
        Returns:
            mis_val_table_ren_columns (pd.DataFrame): матрица информации
        '''
        try:
            if isinstance(pd.DataFrame, df):
                return _missing_values_table(df)
            elif df is None:
                return _missing_values_table(cls.data)
            else:
                raise TypeError("'df' должен быть либо None, либо pd.DataFrame")
            
        except TypeError as e:
            print(e)

    def _print_history(self):
        print(1)
        self.history.print_dll()
    


'''
Я хочу изначально обернуть свой датасет в класс, затем иметь возможность:

1) Небольшая история изменений, на случай того, если после какого-то изменения
метрики ухудшатся, чтобы было несложно откатиться назад

2) Делать статистические выводы из данных:
    - Выбросы
    - Статистики
    - Проверка на соответствие какому-то распределению

    
и ещё много-много всего


Сделать:
1) Вынос приватных методов в отдельный файл

2) Проверить, что везде копируется где надо, и где не надо нет

3) Клиппинг

'''