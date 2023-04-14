import typing as tp
import numpy as np
import pandas as pd
import copy

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
        #print(f'__setattr__: {name} : {value}')
        self.__save_history('__setattr__', name, value)
        super().__setattr__(name, value)

    def __setitem__(self, key, value):
        #print(f'__setitem__: {key} : {value}')
        self.__save_history('__setitem__', key, value)
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self.__save_history('__delitem__', key)
        super().__delitem__(key)

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
            #print('_rollback__')
            if self._history.is_empty():
                raise IndexError('Нет истории, чтобы сделать возврат!')
            method, *args = self._history.rpop()
            if method == '__setitem__':
                key, old_value = args
                self.data[key] = old_value
            elif method == '__delitem__':
                key, value = args
                self.data[key] = value
            elif method == '__setattr__':
                name, value = args
                if name == '_mgr':
                    self.data = value
                else:
                    raise AttributeError(f"Неизвестный аттрибут :{name} !")

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

'''