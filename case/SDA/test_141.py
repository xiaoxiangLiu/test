import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import MytestOnePlayer
from common.connectMysql import ConnectMysql
from common._mytest import sda_account_withdraw
from common.connectRedis import ConnectRedis
from common._mytest import sda_order_create
from common._mytest import sda_fund_balance
from common._mytest import query_account_position_get
from common.AccountTest.AccountUtil import positions_value
from common.AccountTest.AccountUtil import open_positions_value
from common._mytest import assert_list
from common._mytest import MyTestOn
from common._mytest import set_stock_price
from common._mytest import assert_one
from common.params import *
from common.logger import logger
from common._mytest import market_info_get
from common.jsonparser import JMESPathExtractor
from common._mytest import account_info
import time

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_create_url = names.sda_order_create_url
sda_order_get_open_url = names.sda_order_get_open_url
sda_order_cancel_url = names.sda_order_cancel_url
positions_url = names.sda_account_positions_get_url

sda_get_url = names.sda_get_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url
sda_account_positions_get_url = names.sda_account_positions_get_url

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan


class TestCase(MyTestOn):
    """
    持仓状态转出余额测试类
    """
    def test_01(self):
        """
        有持仓，有委托情况下，可转出金额为0
        :return:
        """
        logger.info("用例编号：141-1--有持仓、有委托情况下，可转出金额为0")
        info_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(info_dict["stockPrice"])
        buy_resp = sda_order_create(user=self.buyer, session=self.session, sda_id=sda_id, order_type=多单,
                                    order_price_type=限价,
                                    order_price=now_stock_price, order_num=1*100000000)
        fund_dict = sda_fund_balance(user=self.buyer, session=self.session, sda_id=sda_id)
        flag = assert_one(int(fund_dict["withdrawMargin"]), 0)

        self.assertEqual(True, flag)

    def test_02(self):
        """
        有持仓，有平仓委托的情况下，可转出金额为0
        :return:
        """
        logger.info("用例编号：141-2--有持仓，有平仓委托的情况下，可转出金额为0")
        info_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(info_dict["stockPrice"])
        buy_resp = sda_order_create(user=self.buyer, session=self.session, sda_id=sda_id, order_type=平多,
                                    order_price_type=限价,
                                    order_price=now_stock_price, order_num=1 * 100000000)
        fund_dict = sda_fund_balance(user=self.buyer, session=self.session, sda_id=sda_id)
        flag = assert_one(int(fund_dict["withdrawMargin"]), 0)

        self.assertEqual(True, flag)

    def test_03(self):
        """
        有持仓情况下，转出金额后，预估爆仓价变化
        :return:
        """
        logger.info("用例编号：141-3--有持仓情况下，转出金额后，预估爆仓价变化")
        withdraw_resp = sda_account_withdraw(user=self.buyer, session=self.session, sda_id=sda_id,
                                             amount=self.sda_balance)
        print(withdraw_resp)


if __name__ == '__main__':
    unittest.main()
