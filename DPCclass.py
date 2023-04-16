import typing as tp
import numpy as np
import pandas as pd
import copy
import inspect
import time

from utils import (
    _iqr_outliers_percent,
    _missing_values_table,
    DoublyLinkedList
)

DEFAULT_HISTORY_LEN = 5

class NewDataFrame(pd.DataFrame):
    '''
    Modified pd.DataFrame with support for change history.
    '''
    __NO_HISTORY_METHODS = {
        'remove_outliers',
        '_rollback'
    }

    _history = DoublyLinkedList(max_size = DEFAULT_HISTORY_LEN)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        caller = inspect.stack()[1][3]
        print(f'__setattr__: {name} : {value}, {caller} NewDF')
        if name != '_mgr' and caller not in self.__NO_HISTORY_METHODS:
            self.__save_history('__setattr__', name, value)
        super().__setattr__(name, value)

    def __getattr__(self, name):
        return super().__getattr__(name)

    def __setitem__(self, key, value):
        caller = inspect.stack()[1][3]
        print(f'__setitem__: {key} : {value}, {caller}')
        if caller != '_rollback':
            new = not key in self.columns.values
            history_value = value if new else self.loc[:, key].values
            self.__save_history('__setitem__', key, history_value, new)
        super().__setitem__(key, value)

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
                raise ValueError(f"Deletion of rows is not yet implemented!")
        
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
    This class helps to simplify data preprocessing and make statistical inferences from the data.
    '''
    __MAX_HISTORY_LEN = 10
    data : NewDataFrame = None
    
    def __init__(self, data: pd.DataFrame):
        self.data = NewDataFrame(data)

    def __setattr__(self, name, value):
        print(f'__setattr__ {name} : {value} DPC')
        super().__setattr__(name, value)

    def __getattr__(self, name):
        print(f'__setattr__ {name} : DPC')
        return super().__getattr__(name)

    def set_history_len(self, buffer_len: int):
        '''
        Description:
            Set the maximum length of the stored history of changes.
        
        Args:
            buffer_len (int): maximum length of the history list.
        '''
        try:
            if buffer_len > self.__MAX_HISTORY_LEN:
                raise ValueError(f"Very big value {buffer_len}, \
                                max len must be <={self.__MAX_HISTORY_LEN}!")
            else:
                self._history.resize(buffer_len)
                print(f'Now the history will be stored for {self._history.__len__()} steps!')
        except ValueError as e:
            print(e)

    def _rollback(self):
        '''
        Description:
            Roll back the last data manipulation procedure
        '''
        try:
            #print('_rollback :')
            if self._history.__len__() <= 1:
                raise IndexError('No history to perform rollback!')
            
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
                    raise AttributeError(f"Object has no attribute :{name} !")
                
            elif method == '__drop__':
                columns, values = args
                self.data[columns] = values

            elif method == '__remove_outliers__':
                rows = pd.DataFrame(
                                np.squeeze(args), 
                                columns = self.data.columns)
                       
                self.data = pd.concat([self.data, rows], axis = 0)
                self._history.rpop()

        except IndexError as e:
            print(e)
        except AttributeError as e:
            print(e)
        
    @classmethod
    def iqr_outliers_percent(
        cls,   
        df: tp.Optional[tp.Union[pd.DataFrame, NewDataFrame]],
        columns: tp.Union[str, tp.List[str]] = 'all', 
        threshold: tp.Union[int, float] = 10
    ) -> tp.List[str]:
        '''
        Description:
            This method prints the percentage of outliers in the columns \
            specified in the columns parameter of the feature matrix df. \
            It can be called both from the class and from an instance of the class.

        Args:
            df (pd.DataFrame): feature matrix
            columns (list): columns to remove outliers from
            threshold (float): threshold for removing outliers from drop_cols in percentage
        
        Returns:
            drop_cols (list): a list of columns from which outliers can be removed.
        '''
        try:
            if threshold < 0 or threshold > 100:
                raise ValueError(f"Invalid 'threshold' value {threshold}, \
                                 should be in the range [0, 100]!")


            if isinstance(pd.DataFrame, df):
                if columns == 'all':
                    columns = df.columns
                return _iqr_outliers_percent(df, columns, threshold)
            elif df is None:
                if columns == 'all':
                    columns = cls.data.columns
                return _iqr_outliers_percent(cls.data, columns, threshold)
            else:
                raise TypeError("'df' should either be None and the method should be called from an instance of the class, \
                                or pd.DataFrame and the method should be called from the class.")
            
        except TypeError as e:
            print(e)
        except ValueError as e:
            print(e)
    
    def remove_outliers(
        self, 
        columns: tp.Union[str, tp.List[str]] = 'all',
        threshold: tp.Union[int, float] = 1.5, 
        drop_percent: tp.Union[int, float] = 100          
    ) -> pd.DataFrame:
        '''
        Description:
            The method removes rows that contain outliers determined by Tukey's method (interquartile range).
        
        Args:
            columns (list): list of numeric features
            threshold (float): threshold in Tukey's method
            drop_percent (float): percentage of outliers to drop
            
        Returns:
            df (pd.DataFrame): feature matrix with some fraction of outliers removed.
        '''
        try:
            if threshold < 0:
                raise ValueError(f"Неверное значение 'threshold' {threshold}, \
                                должно быть неотрицательным!")
            if drop_percent < 0 or drop_percent > 100:
                raise ValueError(f"Неверное значение 'drop_persent' {drop_percent}, \
                                должно быть на промежутке [0, 100]")

            df = pd.DataFrame(self.data.copy())

            if columns == 'all':
                columns = df.columns

            bounds = []
            extra_records = None
            for column in columns:
                q1, q3 = df[column].quantile(0.25), df[column].quantile(0.75)
                iqr = q3 - q1
                lower_bound, upper_bound = q1 - threshold * iqr, q3 + threshold * iqr
                bounds.append((lower_bound, upper_bound))

            for (lower_bound, upper_bound), column in zip(bounds, columns):

                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)][column]
                outliers = outliers.sort_values()    
                n_to_remove = int(len(outliers) * drop_percent / 100)
                to_remove = outliers.head(n_to_remove).index.union(outliers.tail(n_to_remove).index)

                if extra_records is None:
                    extra_records = df.loc[to_remove].copy()
                else:
                    extra_records = pd.concat([extra_records, df.loc[to_remove].copy()], axis = 0)

                cleaned_col = df[column].drop(to_remove)
                df = df.loc[cleaned_col.index].copy()
            
            super()._NewDataFrame__save_history('__remove_outliers__', extra_records.values)
            df.reset_index(drop = True, inplace = True)
            self.data = df
            self._history.rpop() # удалим то что положили выше
            return df
            
        except ValueError as e:
            print(e)

    @classmethod
    def missing_values_table(
        cls, 
        df: tp.Optional[tp.Union[pd.DataFrame, NewDataFrame]]
    ) -> pd.DataFrame:
        '''
        Description:
            The method calculates the percentage of missing values in each column of the feature matrix. 
            If df is not specified, it is computed for the 'data' object field.
            
        Args:
            df (pd.DataFrame): feature matrix
            
        Returns:
            mis_val_table_ren_columns (pd.DataFrame): dataframe with the missing value statistics.
        '''
        try:
            if isinstance(pd.DataFrame, df) or isinstance(NewDataFrame, df):
                return _missing_values_table(df)
            elif df is None:
                return _missing_values_table(cls.data)
            else:
                raise TypeError("'df' should be either None or pd.DataFrame.")
            
        except TypeError as e:
            print(e)

    def get_data(
        self, 
        copy = True
    ) -> tp.Union[pd.DataFrame, NewDataFrame]:
        '''
        Description:
            The method returns either a reference to self.data or a copy, depending on the copy flag.

        Args:
            copy (bool): a flag, True -> return a copy of self.data, otherwise -> a reference on self.data

        Returns:
            df (pd.DataFrame, NewDataFrame): a copy or a reference to self.data
        '''
        if copy:
          return pd.DataFrame(self.data.copy())
        return self.data

    def history(self):
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