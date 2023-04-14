import typing as tp
import numpy as np
import pandas as pd
import copy

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