__author__ = '123'
# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import MyTestTwoUser
from common._mytest import assert_one
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.logger import logger
from common._mytest import market_info_get
from common._mytest import query_account_position_get
from common._mytest import assert_list
from common.AccountTest.AccountUtil import employBalance
import time

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_create_url = names.sda_order_create_url
sda_order_get_open_url = names.sda_order_get_open_url
sda_order_cancel_url = names.sda_order_cancel_url

sda_get_url = names.sda_get_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan


class TestCase(MyTestTwoUser):
    """

    """

    def tet_01(self):
        """
        多单1单，空单1单，完全成交，互相平仓
        """
        logger.info("用例编号：1000-1---限价多单1单，限价空单1单，多单完全成交，空单部分成交，验证合约状态、用户余额")
        deal_num = 100000000
        sell_num = 100000000

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        # deal_price = int(int(now_stock_price) * 0.95)

        # 下一单多单、空单，完全成交，并平仓
        for i in range(9000000000):
            buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=now_stock_price, order_num=deal_num
            ))

            # time.sleep(2)
            sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=空单, order_price_type=限价, order_price=now_stock_price, order_num=sell_num
            ))
            time.sleep(0.2)
            self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=平多, order_price_type=限价, order_price=now_stock_price, order_num=deal_num
            ))

            sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=平空, order_price_type=限价, order_price=now_stock_price, order_num=sell_num
            ))

    def tes_02(self):
        """
        下单，平仓，记录金额和手续费，给代理商系统准备数据
        :return:
        """
        deal_num = 1000000000000
        sell_num = 1000000000000

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]
        unit = stock_price_dict["tradeUnit"]
        print(unit)

        # deal_price = int(int(now_stock_price) * 0.95)

        # 下一单多单、空单，完全成交，并平仓
        profit_list = []
        for i in range(10):
            buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=now_stock_price, order_num=deal_num
            ))

            # time.sleep(2)
            sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=空单, order_price_type=限价, order_price=now_stock_price, order_num=sell_num
            ))
            time.sleep(0.2)
            self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=平多, order_price_type=限价, order_price=now_stock_price, order_num=deal_num
            ))

            self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=平空, order_price_type=限价, order_price=now_stock_price, order_num=sell_num
            ))

            value = (int(now_stock_price) * deal_num / 100000000 ) / int(unit)
            # print("value ", value)
            profit = int(value * 0.002)
            profit_list.append(profit)
            # print("profit ", profit)
        print("list ", profit_list)
        print("sum list", sum(profit_list))


if __name__ == '__main__':
    unittest.main()