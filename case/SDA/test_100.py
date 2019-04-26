# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.params import *
from common.logger import logger
from common.connectMysql import ConnectMysql
from common.jsonparser import JMESPathExtractor
from common._mytest import assert_list
from common._mytest import account_info
from common._mytest import assert_one
from common._mytest import ConnectRedis
from common._mytest import account_info_sync
from common._mytest import market_info_get
import time
import random

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_account_deposit_url = names.sda_account_deposit_url
get_user_balance_servlet_url = names.get_user_balance_servlet_url
currency_id = 2


class TestCase(MytestOnePlayer):
    """
    market_info接口访问二
    """

    def test_01(self):
        """
        正常访问
        """
        market_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        print(market_dict)
        print("stock_price", market_dict["stockPrice"])


if __name__ == '__main__':
    unittest.main()