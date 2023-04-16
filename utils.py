import typing as tp
import numpy as np
import pandas as pd
import copy


class Node:
    def __init__(self, value = None, prev = None, next = None):
        self.value = value
        self.prev = prev
        self.next = next

class DoublyLinkedList:
    def __init__(self, max_size = 5):
        try:
            if max_size <= 0:
                raise ValueError(f"'max_size' must be > 0")
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
                raise ValueError(f"The maximum size of the list has been reached!")
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
        if self.is_empty():
            raise Exception("Empty DLL!")
        removed_node = self.head
        if self.head == self.tail:
            self.head = self.tail = None
        else:
            self.head = self.head.next
            self.head.prev = None
        self.size -= 1
        return removed_node.value

    def rpop(self):
        if self.is_empty():
            raise Exception("Empty DLL!")
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
        Changes the MAXIMUM allowable size of the list.
        '''
        if self.size < new_max_size:
            pass
        elif self.size > new_max_size:
            for _ in range(new_max_size, self.size):
                self.__rpop()
            self.size = new_max_size
        self.max_size = new_max_size

    def print_dll(self):
        current_node = self.head
        while current_node:
            print(current_node.value)
            current_node = current_node.next



def _iqr_outliers_percent(df, columns, threshold):
    '''
    This private function calculates the percentage of outliers in the columns of the feature matrix 'df'.
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


def _missing_values_table(df):
    '''
    This private method calculates the percentage of missing values in each column of the feature matrix.    
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