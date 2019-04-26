__author__ = '123'
# coding=utf-8
from .test_02 import TestWinprobability
import unittest, time




class TestCase(TestWinprobability):
    """
    跑全量
    """

    def test_001(self):
        """
        跑2000次
        """
        for i in range(20):
            self.test_01()

if __name__ == '__main__':
    unittest.main()
