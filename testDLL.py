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


