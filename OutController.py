import typing as tp
import numpy as np
import pandas as pd

class ResizableQueue:
    '''
    Класс очереди, в которой можно изменять ее размер.
    '''
    def __init__(self, size: int):
        self.queue = [None] * size
        self.front = 0
        self.rear = 0
        self.size = size

    def push(self, item: tp.Optional[pd.DataFrame]):
        if self.is_full():
            self.front = (self.front + 1) % self.size
        self.queue[self.rear] = item
        self.rear = (self.rear + 1) % self.size

    def pop(self):
        try:
            if self.is_empty():
                raise IndexError("Очередь пуста!")
            item = self.queue[self.front]
            self.queue[self.front] = None
            self.front = (self.front + 1) % self.size
            return item
        except IndexError as e:
            print(e)

    def is_empty(self):
        return self.front == self.rear and self.queue[self.front] is None

    def is_full(self):
        return self.front == self.rear and self.queue[self.front] is not None

    def resize(self, new_size: int):
        if new_size < len(self):
            for _ in range(len(self) - new_size):
                self.pop()
        elif new_size > len(self):
            for _ in range(new_size - len(self)):
                self.queue.append(None)
        
        self.size = new_size

    def __len__(self):
        return (self.rear - self.front + self.size) % self.size
    

class MyDataFrame(pd.DataFrame):
    '''
    Класс позволяет возвращать измененный pd.DataFrame
    '''
    def __setitem__(self, key, value) -> "MyDataFrame":
        super().__setitem__(key, value)
        return self  # возвращаем измененный DataFrame
    
    def __delitem__(self, key) -> "MyDataFrame":
        super().__setitem__(key)
        return self  # возвращаем измененный DataFrame
    

class DataPreparingController(MyDataFrame):
    '''
    Этот класс помогает упрощать предобработку данных и
    делать из них статистические выводы.
    '''
    __MAX_HIST_SIZE = 10

    data: pd.DataFrame = None
    __history = ResizableQueue(size = 5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def __setitem__(self, key, value):
        self.__history.push(self.data.copy())
        self.data = super().__setitem__(key, value)

    def __delitem__(self, key):
        self.__history.push(self.data.copy())
        self.data = super().__delitem__(key)


    def set_history_len(self, buffer_len: int):
        '''
        Description:
            Метод класса, устанавливающий длину хранящейся истории изменений
        
        Args:
            buffer_len (int): новая длина истории
        '''
        try:
            if buffer_len > self.__MAX_HIST_SIZE:
                raise ValueError("Слишком большое значение!")
            else:
                self.__history.resize(buffer_len)
                print(f'Теперь будет храниться история на {self.__history.__len__()} шагов.')
        except ValueError as e:
            print(e)
        

    def сallback(self):
        '''
        Description:
            Откат последней продецуры изменения данных
        '''
        try:
            if self.__history.is_empty:
                raise IndexError('Нет истории, чтобы сделать возврат!')
            self.data = self.__history.pop()

        except IndexError as e:
            print(e)


    def iqr_outliers_percent(
        self,   
        df: pd.DataFrame,
        columns: tp.List[str], 
        threshold: tp.Union[int, float] = 10
    ) -> tp.List[str]:
        '''
        Description:
            Метод выводит процент выбросов в столбцах columns матрицы признаков df

        Args:
            df (pd.DataFrame): матрица признаков
            columns (list): колонки, из которых удалять выбросы
            threshold (float): порог удаления выбросов из drop_cols

        Returns:
            drop_cols (list): список колонок, откуда можно удалить выбросы
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
    
    
    def remove_outliers(
        self,
        df: pd.DataFrame,
        columns: tp.List[str] = 'all',
        threshold: tp.Union[int, float] = 1.5, 
        drop_percent: tp.Union[int, float] = 100
    ) -> pd.DataFrame:
        '''
        Description:
            Метод удаляет строки, в которых есть выбросы, определенные по методу Тьюки (межквартильное расстояние)

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
                raise ValueError(f"Неверное значение 'threshold' {threshold}, должно быть неотрицательным!")
            if drop_percent < 0 or drop_percent > 100:
                raise ValueError(f"Неверное значение 'drop_persent' {drop_percent}, должно быть на промежутке [0, 100]")

            self.__history.push(df.copy())

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

        except TypeError as e:
            print(e)
    

    @classmethod
    def missing_values_table(cls, df: tp.Optional[pd.DataFrame]):
        if isinstance(pd.DataFrame, df):
            DataPreparingController.__missing_values_table(df)
        else:
            DataPreparingController.__missing_values_table(cls.data)

    def __missing_values_table(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        '''
        Description:
            Метод вычисляет процент пропущенных значений в каждом столбце
        Args:
            df (pd.DataFrame): матрица признаков
        Returns:
            mis_val_table_ren_columns (pd.DataFrame): матрица информации
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
    





'''
Я хочу изначально обернуть свой датасет в класс, затем иметь возможность:

1) Небольшая история изменений, на случай того, если после какого-то изменения
метрики ухудшатся, чтобы было несложно откатиться назад

2) Делать статистические выводы из данных:
    - Выбросы
    - Статистики
    - Проверка на соответствие какому-то распределению

    
и ещё много-много всего

'''