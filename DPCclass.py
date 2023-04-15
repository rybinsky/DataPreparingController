import typing as tp
import numpy as np
import pandas as pd
import copy
import inspect

from utils import (
    _iqr_outliers_percent,
    _missing_values_table,
    DoublyLinkedList
)

DEFAULT_HISTORY_LEN = 5


class NewDataFrame(pd.DataFrame):
    '''
    Класс позволяет возвращать измененный pd.DataFrame
    '''
    _history = DoublyLinkedList(max_size = DEFAULT_HISTORY_LEN)

    def __init__(self, *args, **kwargs):
        #print('__init__NewDF')
        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        caller = inspect.stack()[1][3]
        print(f'__setattr__: {name} : {value}, ')
        if name != '_mgr' and caller != '_rollback':
            self.__save_history('__setattr__', name, value)
        super().__setattr__(name, value)

    def __setitem__(self, key, value):
        caller = inspect.stack()[1][3]
        print(f'__setitem__: {key} : {value}')
        if caller != '_rollback':
            new = not key in self.columns.values
            history_value = value if new else self.loc[:, key].values
            #print(f'history_value = {history_value}')
            self.__save_history('__setitem__', key, history_value, new)
        super().__setitem__(key, value)

    def __getitem__(self, key):
        print(f'__getitem__ : {key}')
        return super().__getitem__(key)

    def __delitem__(self, key):
        caller = inspect.stack()[1][3]
        if caller != '_rollback':
            self.__save_history('__delitem__', key,)
        super().__delitem__(key)


    def drop(
        self, 
        labels = None, 
        axis = 1, 
        index = None, 
        columns = None, 
        level = None, 
        inplace = False,
        errors = 'raise'
    ):
        print(f'__drop__ NewDF: labels = {labels}, axis = {axis}, columns = {columns}', inspect.stack()[1][3])
        caller = inspect.stack()[1][3]
        try:
            if axis == 0:
                raise ValueError(f"Пока не реализовано удаление строк!")
        
            elif axis == 1:
                if caller != '_rollback':
                    self.__save_history('__drop__', columns, self.loc[:, columns].copy())
            super().drop(labels = labels, axis = axis, index = index, columns = columns, level = level, inplace = inplace, errors = errors)
        except ValueError as e:
            print(e)
    

    def __save_history(self, method_name, *args):
        self._history.push((method_name, *copy.deepcopy(args)))


class DataPreparingController(NewDataFrame):
    '''
    Этот класс помогает упрощать предобработку данных и
    делать из них статистические выводы.
    '''
    __MAX_HISTORY_LEN = 10
    data : NewDataFrame = None
    
    def __init__(self, data: pd.DataFrame):
        self.data = NewDataFrame(data)

    def __setattr__(self, name, value):
        #print(f'__setattr__ {name} : {value} DPC')
        super().__setattr__(name, value)   

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
                self._history.resize(buffer_len)
                print(f'Теперь будет храниться история на {self.__history.__len__()} шагов.')
        except ValueError as e:
            print(e)

    def _rollback(self):
        '''
        Description:
            Откат последней продецуры изменения данных
        '''
        try:
            print('_rollback :')
            if self._history.is_empty() or self._history.__len__() == 1:
                raise IndexError('Нет истории, чтобы сделать возврат!')
            method, *args = self._history.rpop()
            if method == '__setitem__':
                key, old_value, new = args
                if new:
                    self.data.drop(columns = key, axis = 1, inplace = True)
                else:
                    self.data[key] = old_value

            elif method == '__delitem__':
                key, value = args
                self.data[key] = value
            elif method == '__setattr__':
                name, value = args
                if name == 'data':
                    self.data = value
                else:
                    raise AttributeError(f"Неизвестный аттрибут :{name} !")
            elif method == '__drop__':
                columns, values = args
                self.data[columns] = values

        except IndexError as e:
            print(e)
        except AttributeError as e:
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
        df: tp.Optional[NewDataFrame],
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
            #print(1)
            if not isinstance(df, NewDataFrame):
                df = self.data.copy()
            df = pd.DataFrame(df)

            if columns == 'all':
                columns = df.columns
            #print(2)
            cleaned_indexes = []
            bounds = []
            for column in columns:
                #print(3, column)
                q1 = df[column].quantile(0.25)
                q3 = df[column].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - threshold * iqr
                upper_bound = q3 + threshold * iqr
                bounds.append((lower_bound, upper_bound))
            print(4, type(df), cleaned_indexes, bounds)
            for (lower_bound, upper_bound), column in zip(bounds, columns):
                print(1)
                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)][column]
                outliers = outliers.sort_values()    
                n_to_remove = int(len(outliers) * drop_percent / 100)
                
                to_remove = outliers.head(n_to_remove).index.union(outliers.tail(n_to_remove).index)
                #cleaned_col = df[column].drop(to_remove)
                cleaned_indexes.append(to_remove)
                #df = df.loc[cleaned_col.index].copy()
                #df.reset_index(drop = True, inplace = True)
            
            self._history.push('_-remove_out__', df.loc[cleaned_indexes].copy())
            df = df.drop(labels = cleaned_indexes, axis = 0)
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
        self._history.print_dll()
    


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

Операции:

df[col] = new_col

df.drop(колонки)



'''