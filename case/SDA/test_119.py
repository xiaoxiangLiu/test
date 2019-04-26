# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import MyTestTwoUserLever
from common._mytest import assert_one
from common.params import *
from common.logger import logger
from common._mytest import query_account_position_get
from common._mytest import account_info
from common.AccountTest.AccountUtil import crashPrice
from common.AccountTest.AccountUtil import openStockCost
from common.AccountTest.AccountUtil import unRealLoss
from common.AccountTest.AccountUtil import employBalance
import time
from common.jsonparser import JMESPathExtractor
from common._mytest import market_info_get

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_create_url = names.sda_order_create_url
sda_order_get_open_url = names.sda_order_get_open_url
sda_order_cancel_url = names.sda_order_cancel_url

sda_get_url = names.sda_get_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url
sda_account_positions_get_url = names.sda_account_positions_get_url

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan


class TestCase(MyTestTwoUserLever):
    """
    爆仓测试类
    """
    def test_01(self):
        """
        限价多单1单，杠杆5倍，限价空单1单，杠杆1倍，完全成交，验证合约状态、用户余额
        """
        logger.info("用例编号：119-1---限价多单1单，杠杆50倍，限价空单1单，杠杆1倍，完全成交，验证保证金、开仓手续费、预估爆仓价")
        deal_num = 10*100000000
        lever = 50

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(stock_price_dict["stockPrice"])
        stock_unit = int(stock_price_dict["tradeUnit"])

        deal_price = int(int(now_stock_price) * 0.95)
        # deal_price = 18*100000000

        before_buy_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_buy_balance = before_buy_dict["balance"]

        # 下一单多单、空单，完全成交
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=多单, order_price_type=限价, lever=lever, order_price=deal_price,order_num=deal_num
        ))
        buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))
        # time.sleep(3)
        sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=空单, order_price_type=限价, lever=lever, order_price=deal_price,order_num=deal_num
        ))
        sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
            self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
        ))

        # 计算仓位保证金
        buy_employ_balance = employBalance(price=deal_price, count=deal_num, unit=stock_unit, lever=lever)
        print(buy_employ_balance)
        # 计算开仓手续费
        open_stock_cost = openStockCost(price=deal_price, count=deal_num, doMore=True, unit=stock_unit,
                                        stockPrice=now_stock_price)

        # 计算未实现盈亏
        buy_real_less = int(unRealLoss(holdAvgPrice=deal_price, count=deal_num, unit=stock_unit, doMore=True,
                                    holdCharge=open_stock_cost, stock_price=now_stock_price))

        # 计算爆仓价
        buy_crash_price = crashPrice(holdAvgPrice=deal_price, holdCount=deal_num,
                                     totalBalance=self.sda_balance - open_stock_cost,
                                     unit=stock_unit, doMore=True)
        time.sleep(0.1)
        buy_position_get_dict = query_account_position_get(user=self.buyer, session=self.session, sync_key=sell_sync_id)
        buy_bust_price = int(buy_position_get_dict["sdaBustPrice"])  # 预估爆仓价
        buy_balance_position = int(buy_position_get_dict["currencyBalancePosition"])  # 仓位保证金
        buy_unrealized_PNL = int(buy_position_get_dict["unrealizedPNL"])  # 未实现盈亏

        balance_flag = assert_one(buy_balance_position, buy_employ_balance)  # 检验保证金
        bust_flag = assert_one(buy_bust_price, buy_crash_price)  # 检验爆仓
        pnl_flag = assert_one(buy_unrealized_PNL, buy_real_less)  # 检验未实现盈亏
        self.assertListEqual([True, True, True], [bust_flag, pnl_flag, balance_flag])

    def test_02(self):
        """
        限价空单1单，50倍杠杆，限价多单1单，1倍杠杆，完全成交，验证合约状态、用户余额
        """
        logger.info("用例编号：119-2---限价空单1单，50倍杠杆，限价多单1单，1倍杠杆，完全成交，验证保证金、开仓手续费、预估爆仓价")
        deal_num = 200000000
        lever = 50

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(stock_price_dict["stockPrice"])
        stock_unit = int(stock_price_dict["tradeUnit"])

        deal_price = int(int(now_stock_price) * 0.95)
        print("deal_price", deal_price)

        # 交易前查询用户余额
        before_buy_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_buy_balance = before_buy_dict["balance"]

        # 下一单多单、空单，完全成交
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=空单, order_price_type=限价, lever=lever, order_price=deal_price,order_num=deal_num
        ))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))
        # time.sleep(3)
        sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=多单, order_price_type=限价, lever=lever, order_price=deal_price, order_num=deal_num
        ))
        sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
            self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
        ))

        # 计算仓位保证金
        buy_employ_balance = employBalance(price=deal_price, count=deal_num, unit=stock_unit, lever=lever)
        print("employ_balance", buy_employ_balance)

        # 计算开仓手续费
        open_stock_cost = openStockCost(price=deal_price, count=deal_num, doMore=False, unit=stock_unit,
                                        stockPrice=now_stock_price)
        print("open_stock_cost", open_stock_cost)
        # 计算未实现盈亏
        unreal_loss = int(unRealLoss(holdAvgPrice=deal_price, count=deal_num, unit=stock_unit, doMore=False,
                                 holdCharge=open_stock_cost, stock_price=now_stock_price))
        print("unrealloss", unreal_loss)
        # 计算爆仓价
        buy_crash_price = crashPrice(holdAvgPrice=deal_price, holdCount=deal_num,
                                     totalBalance=self.sda_balance - open_stock_cost,
                                     unit=stock_unit, doMore=False)
        time.sleep(0.1)
        buy_position_get_dict = query_account_position_get(user=self.buyer, session=self.session,
                                                           sync_key=sell_sync_id)
        buy_bust_price = int(buy_position_get_dict["sdaBustPrice"])  # 预估爆仓价
        buy_balance_position = int(buy_position_get_dict["currencyBalancePosition"])  # 仓位保证金
        buy_unrealized_PNL = int(buy_position_get_dict["unrealizedPNL"])  # 未实现盈亏

        balance_flag = assert_one(buy_balance_position, buy_employ_balance)  # 检验保证金
        bust_flag = assert_one(buy_bust_price, buy_crash_price)  # 检验爆仓
        pnl_flag = assert_one(buy_unrealized_PNL, unreal_loss)  # 检验未实现盈亏
        self.assertListEqual([True, True, True], [bust_flag, pnl_flag, balance_flag])


if __name__ == '__main__':
    unittest.main()
