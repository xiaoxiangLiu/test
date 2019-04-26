import unittest
import warnings
from common.tools import init_environment_213
from common.names import names
from common._mytest import MyTestThreeUser
from common.AccountTest.AccountUtil import employBalance
from common._mytest import assert_one
from common._mytest import account_info_sync
from common._mytest import account_info
from common.params import *
from common.logger import logger
from common.AccountTest.AccountUtil import openStockCost
import time
from common.jsonparser import JMESPathExtractor
from common._mytest import market_info_get
from common.connectMysql import ConnectMysql
from common.AccountTest.AccountUtil import *
import random

base, mysql_type, redis_type, sda_id = init_environment_213()
eth_sda = "82"

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


class TestCase(MyTestThreeUser):
    """
    大数成交测试
    """
    def test_01(self):
        """
        大数成交测试
        :return:
        """
        warnings.simplefilter("ignore", ResourceWarning)
        lever = 100
        deal_num = 9999999900000
        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(stock_price_dict["stockPrice"])
        stock_unit = int(stock_price_dict["tradeUnit"])

        deal_price = int(int(now_stock_price) * 0.95)

        # 下一单多单、空单，完全成交
        buy_resp = self.session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      order_price_type=限价,
                                                                                                      lever=lever,
                                                                                                      order_price=deal_price,
                                                                                                      order_num=deal_num))
        buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))
        # time.sleep(3)
        sell_resp = self.sell_session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                            order_type=空单,
                                                                                                            order_price_type=限价,
                                                                                                            lever=lever,
                                                                                                            order_price=deal_price,
                                                                                                            order_num=deal_num))
        sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
            self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
        ))
        buy_info_dict = account_info_sync(user=self.buyer, session=self.session, sda_id=sda_id, sync_id=sell_sync_id)
        # print(buy_info_dict)
        after_buy_balance = int(buy_info_dict["balance"])

        sell_info_dict = account_info_sync(user=self.seller, session=self.sell_session, sda_id=sda_id,
                                           sync_id=sell_sync_id)
        after_sell_balance = int(sell_info_dict["balance"])
        # print("stock price", deal_price)
        # print("stock unit", stock_unit)
        # employ_balance = deal_price / 100000000 * deal_num
        # print("employ balance", employ_balance)
        employ_balance = int(employBalance(price=deal_price, count=deal_num, unit=stock_unit, lever=lever))
        # print("employ balance", employ_balance)
        buy_flag = assert_one(after_buy_balance, int(self.sda_balance - employ_balance))
        sell_flag = assert_one(after_sell_balance, int(self.sda_balance - employ_balance))
        self.assertListEqual([True, True], [buy_flag, sell_flag])

    def test_02(self):
        """
        大数成交测试
        :return:
        """
        warnings.simplefilter("ignore", ResourceWarning)
        lever = 100
        deal_num = 100000000
        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(stock_price_dict["stockPrice"])
        stock_unit = int(stock_price_dict["tradeUnit"])

        deal_price = int(int(now_stock_price) * 0.95)

        # 下一单多单、空单，完全成交
        buy_resp = self.session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      order_price_type=限价,
                                                                                                      lever=lever,
                                                                                                      order_price=now_stock_price,
                                                                                                      order_num=deal_num))
        buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))
        # time.sleep(3)
        sell_resp = self.sell_session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                            order_type=空单,
                                                                                                            order_price_type=限价,
                                                                                                            lever=lever,
                                                                                                            order_price=now_stock_price,
                                                                                                            order_num=deal_num))
        sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
            self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
        ))
        buy_info_dict = account_info_sync(user=self.buyer, session=self.session, sda_id=sda_id, sync_id=sell_sync_id)
        # print(buy_info_dict)
        after_buy_balance = int(buy_info_dict["balance"])

        sell_info_dict = account_info_sync(user=self.seller, session=self.sell_session, sda_id=sda_id,
                                           sync_id=sell_sync_id)
        after_sell_balance = int(sell_info_dict["balance"])
        print("stock price", now_stock_price)
        print("stock unit", stock_unit)
        employ_balance = int(employBalance(price=now_stock_price, count=deal_num, unit=stock_unit, lever=lever))
        print("employ balance", employ_balance)
        buy_flag = assert_one(after_buy_balance, int(self.sda_balance - employ_balance))
        sell_flag = assert_one(after_sell_balance, int(self.sda_balance - employ_balance))
        self.assertListEqual([True, True], [buy_flag, sell_flag])

    def tet_03(self):
        """
        大数运算测试
        :return:
        """
        warnings.simplefilter("ignore", ResourceWarning)
        lever = 100
        deal_num = 100000000
        buy_num = 9*100000000
        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(stock_price_dict["stockPrice"])
        stock_unit = int(stock_price_dict["tradeUnit"])

        deal_price = int(int(now_stock_price) * 0.95)

        # 下一单多单、空单，完全成交
        buy_resp = self.session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      order_price_type=限价,
                                                                                                      lever=lever,
                                                                                                      order_price=deal_price,
                                                                                                      order_num=buy_num))
        buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))
        before_deal_buy_balance_dict = account_info_sync(user=self.buyer, session=self.session, sda_id=sda_id,
                                                         sync_id=buy_sync_id)
        before_deal_buy_balance = before_deal_buy_balance_dict["balance"]
        before_buy_employ_balance = int(employBalance(price=deal_price, count=buy_num, unit=stock_unit, lever=lever))
        before_flag = assert_one(int(before_deal_buy_balance), int(self.sda_balance - before_buy_employ_balance))
        print("before flag", before_flag)
        self.assertTrue(True, before_flag)

        # time.sleep(3)
        sell_resp = self.sell_session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                            order_type=空单,
                                                                                                            order_price_type=市价,
                                                                                                            lever=lever,
                                                                                                            order_price=deal_price,
                                                                                                            order_num=deal_num))
        sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
            self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
        ))
        buy_info_dict = account_info_sync(user=self.buyer, session=self.session, sda_id=sda_id, sync_id=sell_sync_id)
        # print(buy_info_dict)
        after_buy_balance = int(buy_info_dict["balance"])

        sell_info_dict = account_info_sync(user=self.seller, session=self.sell_session, sda_id=sda_id,
                                           sync_id=sell_sync_id)
        after_sell_balance = int(sell_info_dict["balance"])
        # print("stock price", deal_price)
        # print("stock unit", stock_unit)
        buy_employ_balance = int(employBalance(price=deal_price, count=buy_num, unit=stock_unit, lever=lever))
        employ_balance = int(employBalance(price=deal_price, count=deal_num, unit=stock_unit, lever=lever))
        print("buy employ balance", buy_employ_balance)
        buy_flag = assert_one(after_buy_balance, int(self.sda_balance - buy_employ_balance))
        sell_flag = assert_one(after_sell_balance, int(self.sda_balance - employ_balance))
        self.assertListEqual([True, True], [buy_flag, sell_flag])

    def tet_04(self):
        """
        随机成交测试
        :return:
        """
        warnings.simplefilter("ignore", ResourceWarning)
        lever = 100
        # deal_num = 100000000
        # buy_num = 9*100000000
        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(stock_price_dict["stockPrice"])
        stock_unit = int(stock_price_dict["tradeUnit"])

        deal_price = int(int(now_stock_price) * 0.95)

        before_buy_info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_buy_balance = int(before_buy_info_dict["balance"])
        print("before buy balance", before_buy_balance)

        before_sell_info_dict = account_info(user=self.seller, session=self.sell_session, sda_id=sda_id)
        before_sell_balance = int(before_sell_info_dict["balance"])
        print("before sell balance", before_sell_balance)

        # random_price = random.randint(1, 99) * 100000000
        random_num = random.randint(1, 999999) * 100000000

        # 下一单多单、空单，完全成交
        for i in range(1000):
            buy_resp = self.session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                          order_type=多单,
                                                                                                          order_price_type=限价,
                                                                                                          lever=lever,
                                                                                                          order_price=now_stock_price,
                                                                                                          order_num=random_num))
            # buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
                self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
            ))
            # time.sleep(3)
            sell_resp = self.sell_session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                                order_type=空单,
                                                                                                                order_price_type=市价,
                                                                                                                lever=lever,
                                                                                                                order_price=now_stock_price,
                                                                                                                order_num=random_num))
            sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
                self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
            ))
            buy_info_dict = account_info_sync(user=self.buyer, session=self.session, sda_id=sda_id, sync_id=sell_sync_id)
            # print(buy_info_dict)
            after_buy_balance = int(buy_info_dict["balance"])

            sell_info_dict = account_info_sync(user=self.seller, session=self.sell_session, sda_id=sda_id,
                                               sync_id=sell_sync_id)
            after_sell_balance = int(sell_info_dict["balance"])
            # print("stock price", deal_price)
            # print("stock unit", stock_unit)
            buy_employ_balance = int(employBalance(price=now_stock_price, count=random_num, unit=stock_unit, lever=lever))
            employ_balance = int(employBalance(price=now_stock_price, count=random_num, unit=stock_unit, lever=lever))
            print("buy employ balance", buy_employ_balance)
            buy_flag = assert_one(after_buy_balance, int(before_buy_balance - buy_employ_balance))
            sell_flag = assert_one(after_sell_balance, int(before_sell_balance - employ_balance))
            self.assertListEqual([True, True], [buy_flag, sell_flag])

            # 平仓
            time.sleep(0.1)
            buy_resp = self.session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                          order_type=平多,
                                                                                                          order_price_type=限价,
                                                                                                          lever=lever,
                                                                                                          order_price=now_stock_price,
                                                                                                          order_num=random_num))
            # buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
                self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
            ))
            time.sleep(0.1)
            sell_resp = self.sell_session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                                order_type=平空,
                                                                                                                order_price_type=市价,
                                                                                                                lever=lever,
                                                                                                                order_price=now_stock_price,
                                                                                                                order_num=random_num))
            # sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
                self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
            ))


if __name__ == '__main__':
    unittest.main()