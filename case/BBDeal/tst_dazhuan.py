__author__ = '123'
# coding=utf-8
import unittest
from zhongqiu_case.test_02 import TestWinprobability
from common.logger import logger


class TestCase(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_001(self):
        num = 0
        for i in range(3):
            num += 1
            TestWinprobability().test_02()
        logger.info("兑换抽奖次数{}".format(num))

if __name__ == '__main__':
    unittest.main()