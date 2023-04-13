import unittest
import pandas as pd

from OutController import DoublyLinkedList

class TestDLL(unittest.TestCase):

    def setUp(self, size: int):
        self.queue = DoublyLinkedList(max_size = size)


    def test_push(self):
        self.queue.push(1)
        self.queue.push(2)
        self.queue.push(3)
        self.assertEqual(len(self.queue), 3)
        self.assertEqual(self.queue.pop(), 1)
        self.assertEqual(len(self.queue), 2)
        self.queue.print_dll()
        print('test_push ОК')


    def test_pop(self):
        # with self.assertRaises(IndexError):
        #     self.queue.pop()
        self.queue.push(4)
        self.queue.push(5)
        self.queue.push(6)
        self.queue.push(7)
        self.queue.print_dll()
        self.assertEqual(self.queue.pop(), 3)
        self.assertEqual(self.queue.pop(), 4)
        self.assertEqual(self.queue.pop(), 5)
        self.queue.print_dll()
        self.assertEqual(self.queue.pop(), 6)
    
        # with self.assertRaises(IndexError):
        #     self.queue.pop()
        print('test_pop ОК')


    def test_resize(self):
        self.queue.print_dll()
        self.queue.resize(2)
        self.assertEqual(len(self.queue), 1)
        self.queue.push(8)
        self.queue.push(9)
        self.queue.resize(3)
        self.assertEqual(len(self.queue), 2)
        self.assertEqual(self.queue.pop(), 8)
        self.assertEqual(self.queue.pop(), 9)
        self.assertEqual(len(self.queue), 0)
        print('test_resize OK')



qt = TestDLL()
qt.setUp(5)
qt.queue.print_dll()
qt.test_push()
qt.test_pop()
qt.test_resize()
# q = DoublyLinkedList(5)
# q.push(1)
# #q.print_dll()
# q.push(2)
# #q.print_dll()
# q.push(3)
# #q.print_dll()
# #print(q.__len__())
# q.push(4)
# #q.print_dll()
# q.push(5)
# #q.print_dll()
# q.push(6)
# #print(q.__len__())
# #q.print_dll()
# q.pop()
# #q.print_dll()
# q.pop()
# #print(q.__len__())
# #q.print_dll()
# q.push(7)
# #q.print_dll()
# q.pop()
# #q.print_dll()
# q.pop()
# #q.print_dll()
# q.resize(2)
# q.pop()
# q.push(10)
# q.push(20)
# # print(q.__len__())
# q.print_dll()

