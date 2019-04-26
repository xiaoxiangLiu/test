__author__ = '123'
# coding=utf-
import unittest
from common.tools import init_environment_213
from common.tools import init_environment_252
from common.names import names
from common._mytest import MyTestTwoUser
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.logger import logger
from common._mytest import query_account_position_get
from common._mytest import assert_one
from common._mytest import assert_list
from common._mytest import market_info_get
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
    部分成交测试类
    """
    def test_01(self):
        """
        空单1单，多单1单，空单完全成交，多单部分成交，验证合约状态、用户余额
        """
        logger.info("用例编号：42-1---空单1单，多单1单，空单完全成交，多单部分成交，验证合约状态、用户余额")
        sell_num = 100000000
        buy_num = 200000000

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        deal_price = int(int(now_stock_price) * 0.95)

        # 下一单多单、空单，部分成交
        for i in range(1):
            buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=空单, order_price_type=限价,order_price=deal_price,order_num=sell_num
            ))

            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
                self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
            ))

            sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=deal_price, order_num=buy_num
            ))
            sell_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=sell_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
                self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
            ))

            time.sleep(4)
            # 查询当前持仓中买卖方持仓数量、保证金、开仓均价
            after_buy_position_dict = query_account_position_get(user=self.buyer, session=self.session)
            after_sell_position_dict = query_account_position_get(user=self.seller, session=self.sell_session)

            after_buy_sdaAveragePrice = after_buy_position_dict["sdaAveragePrice"]
            after_buy_sdaCount = after_buy_position_dict["sdaCount"]
            after_buy_currencyBalancePosition = after_buy_position_dict["currencyBalancePosition"]

            after_sell_sdaAveragePrice = after_sell_position_dict["sdaAveragePrice"]
            after_sell_sdaCount = after_sell_position_dict["sdaCount"]
            after_sell_currencyBalancePosition = after_sell_position_dict["currencyBalancePosition"]

            # 计算保证金
            # buy_currency_balance = make_currency_balance(num=deal_num, price=deal_price)
            # sell_currency_balance = make_currency_balance(num=deal_num, price=deal_price)
            # 检验持仓均价，持仓量，保证金
            price_flag = assert_one(int(deal_price), int(after_buy_sdaAveragePrice))
            num_flag = assert_one(int(sell_num), int(after_buy_sdaCount))
            # after_buy_flag = assert_one(buy_currency_balance, int(after_buy_currencyBalancePosition))
            after_sell_flag = assert_list([int(deal_price), int(sell_num)], [int(after_sell_sdaAveragePrice),
                                                                             int(after_sell_sdaCount)])
            self.assertListEqual([True, True, True], [price_flag, num_flag,after_sell_flag])

    def test_03(self):
        """
        空单1单，多单1单，空单部分成交，多单完全成交，验证合约状态、用户余额
        """
        logger.info("用例编号：42-3---空单1单，多单1单，空单部分成交，多单完全成交，验证合约状态、用户余额")
        sell_num = 200000000
        buy_num = 100000000

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        deal_price = int(int(now_stock_price) * 0.95)

        # 下一单多单、空单，完全成交
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=空单,order_price_type=限价,order_price=deal_price,order_num=sell_num
        ))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))
        buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=buy_resp.text)
        sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=多单,order_price_type=限价,order_price=deal_price,order_num=buy_num
        ))
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
            self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
        ))

        # time.sleep(4)
        # 查询当前持仓中买卖方持仓数量、保证金、开仓均价
        after_buy_position_dict = query_account_position_get(user=self.buyer, session=self.session, sync_key=sync_id)
        after_sell_position_dict = query_account_position_get(user=self.seller, session=self.sell_session,
                                                              sync_key=sync_id)

        after_buy_sdaAveragePrice = after_buy_position_dict["sdaAveragePrice"]
        after_buy_sdaCount = after_buy_position_dict["sdaCount"]
        after_buy_currencyBalancePosition = after_buy_position_dict["currencyBalancePosition"]

        after_sell_sdaAveragePrice = after_sell_position_dict["sdaAveragePrice"]
        after_sell_sdaCount = after_sell_position_dict["sdaCount"]
        after_sell_currencyBalancePosition = after_sell_position_dict["currencyBalancePosition"]

        # 计算保证金
        # buy_currency_balance = make_currency_balance(num=deal_num, price=deal_price)
        # sell_currency_balance = make_currency_balance(num=deal_num, price=deal_price)
        # 检验持仓均价，持仓量，保证金
        price_flag = assert_one(int(deal_price), int(after_buy_sdaAveragePrice))
        num_flag = assert_one(int(buy_num), int(after_buy_sdaCount))
        # after_buy_flag = assert_one(buy_currency_balance, int(after_buy_currencyBalancePosition))
        after_sell_flag = assert_list([int(deal_price), int(buy_num)], [int(after_sell_sdaAveragePrice),
                                                                        int(after_sell_sdaCount)])
        self.assertListEqual([True, True, True], [price_flag, num_flag,after_sell_flag])


if __name__ == '__main__':
    unittest.main()
