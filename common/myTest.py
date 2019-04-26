__author__ = '123'
# coding=utf-8
from common.connectMysql import ConnectMysql
from common.config import GetInit
from common.jsonparser import JMESPathExtractor
from common.logger import logger
import unittest, time, requests


user_buyer_mail = GetInit().GetData("user", "user_buyer_mail")
user_seller_mail = GetInit().GetData("user", "user_seller_mail")
user_password = GetInit().GetData("user", "user_password")
base_url = GetInit().GetData("base", "base_url")
token = "c8edf9b44ad511fda9c686c911e3dfb2"

class MyTest(unittest.TestCase):

    def setUp(self):
        """
        user_list = ["38@qq.com", "39@qq.com", "40@qq.com", "41@qq.com"]
        transtion_id_list = [1, 2,3,4,15,6,13,18,16,17,14,23,24,19]
        for i in user_list:
            for k in transtion_id_list:
                ConnectMysql(_type=3).update_balance_value(user_mail=i, currency_id=k, balance_value=9900000000000000)
                time.sleep(0.2)
                """

    def tearDown(self):
        pass

    def sub_setUp(self):
        """
        user_list = ["38@qq.com", "39@qq.com", "40@qq.com", "41@qq.com"]
        transtion_id_list = [1, 2]
        for i in user_list:
            for k in transtion_id_list:
                ConnectMysql(_type=3).update_balance_value(user_mail=i, currency_id=k, balance_value=9900000000000000)
                """
    def sub_tearDown(self):
        pass

if __name__ == '__main__':
    pass
