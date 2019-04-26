__author__ = '123'
# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import MyTestTwoUser
from common._mytest import assert_one
from common._mytest import account_info_sync
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.logger import logger
from common._mytest import market_info_get
import time
from common._mytest import account_info

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
    多个订单和多个订单成交，验证余额，订单状态
    """
    def test_01(self):
        """
        多个限价多单、多个限价空单，验证订单状态、用户余额
        """
        logger.info("用例编号：46-1---多个限价多单、多个限价空单，验证订单状态、用户余额")
        deal_num = 100000000
        random_num = 5

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        price = int(int(now_stock_price) * 0.95)

        # 下单前查询两个用户的可用余额
        before_buy_account_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_buy_account_balance = before_buy_account_dict["balance"]

        before_sell_account_dict = account_info(user=self.seller, session=self.sell_session, sda_id=sda_id)
        before_sell_account_balance = before_sell_account_dict["balance"]

        buy_sync_id = None
        for i in range(random_num):
            # 循环下多单
            buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=price, order_num=deal_num
            ))
            buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
                self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
            ))
            # time.sleep(1)

        sell_sync_id = None
        for v in range(random_num):
            # 循环下5个空单
            sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=空单, order_price_type=限价, order_price=price, order_num=deal_num
            ))
            sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
                self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
            ))
            # time.sleep(1)

        # time.sleep(2)

        # 下单结束后查询两个用户可用余额
        after_buy_account_dict = account_info_sync(sync_id=buy_sync_id, user=self.buyer, session=self.session,
                                                   sda_id=sda_id)
        after_buy_account_balance = after_buy_account_dict["balance"]

        after_sell_account_dict = account_info_sync(sync_id=sell_sync_id, user=self.seller, session=self.sell_session,
                                                    sda_id=sda_id)
        after_sell_account_balance = after_sell_account_dict["balance"]

        buy_flag = assert_one(self.sda_balance, int(after_buy_account_balance) +
                              int(random_num * deal_num * price / 100000000))
        sell_flag = assert_one(self.sda_balance, int(after_sell_account_balance) +
                               int(random_num * deal_num * price / 100000000))
        self.assertListEqual([True, True], [buy_flag, sell_flag])

    def test_02(self):
        """
        多个限价空单、多个限价多单，验证订单状态、用户余额
        """
        logger.info("用例编号：46-2---多个限价空单、多个限价多单，验证订单状态、用户余额")
        deal_num = 100000000
        random_num = 5

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        price = int(int(now_stock_price) * 0.95)

        # 下单前查询两个用户的可用余额
        before_buy_account_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_buy_account_balance = before_buy_account_dict["balance"]

        before_sell_account_dict = account_info(user=self.seller, session=self.sell_session, sda_id=sda_id)
        before_sell_account_balance = before_sell_account_dict["balance"]

        buy_sync_id = None
        for i in range(random_num):
            # 循环下多单
            buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=空单, order_price_type=限价, order_price=price, order_num=deal_num
            ))
            buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
                self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
            ))
            # time.sleep(1)

        sell_sync_id = None
        for v in range(random_num):
            # 循环下5个空单
            sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=price, order_num=deal_num
            ))
            sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
                self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
            ))
            # time.sleep(1)

        # time.sleep(2)

        # 下单结束后查询两个用户可用余额
        after_buy_account_dict = account_info_sync(sync_id=buy_sync_id, user=self.buyer, session=self.session,
                                                   sda_id=sda_id)
        after_buy_account_balance = after_buy_account_dict["balance"]

        after_sell_account_dict = account_info_sync(sync_id=sell_sync_id, user=self.seller, session=self.sell_session,
                                                    sda_id=sda_id)
        after_sell_account_balance = after_sell_account_dict["balance"]

        buy_flag = assert_one(self.sda_balance, int(after_buy_account_balance) +
                              int(random_num * deal_num * price / 100000000))
        sell_flag = assert_one(self.sda_balance, int(after_sell_account_balance) +
                               int(random_num * deal_num * price / 100000000))
        self.assertListEqual([True, True], [buy_flag, sell_flag])

    def test_03(self):
        """
        多个限价多单、多个市价空单，验证订单状态、用户余额
        """
        logger.info("用例编号：46-3---多个限价多单、多个市价空单，验证订单状态、用户余额")
        deal_price = 100000000
        deal_num = 100000000
        random_num = 5

        # 下单前查询两个用户的可用余额
        before_buy_account_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_buy_account_balance = before_buy_account_dict["balance"]

        before_sell_account_dict = account_info(user=self.seller, session=self.sell_session, sda_id=sda_id)
        before_sell_account_balance = before_sell_account_dict["balance"]

        buy_sync_id = None
        for i in range(random_num):
            # 循环下多单
            buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=deal_price, order_num=deal_num
            ))
            buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
                self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
            ))
            # time.sleep(1)

        sell_sync_id = None
        for v in range(random_num):
            # 循环下5个空单
            sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=空单, order_price_type=市价, order_num=deal_num
            ))
            sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
                self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
            ))
            time.sleep(1)

        # time.sleep(2)

        # 下单结束后查询两个用户可用余额
        after_buy_account_dict = account_info_sync(sync_id=buy_sync_id, user=self.buyer, session=self.session,
                                                   sda_id=sda_id)
        after_buy_account_balance = after_buy_account_dict["balance"]

        after_sell_account_dict = account_info_sync(sync_id=sell_sync_id, user=self.seller, session=self.sell_session,
                                                    sda_id=sda_id)
        after_sell_account_balance = after_sell_account_dict["balance"]

        buy_flag = assert_one(self.sda_balance, int(after_buy_account_balance) + int(random_num * 100000000))
        sell_flag = assert_one(self.sda_balance, int(after_sell_account_balance) + int(random_num * 100000000))
        self.assertListEqual([True, True], [buy_flag, sell_flag])

    def test_04(self):
        """
        多个限价空单、多个市价多单，验证订单状态、用户余额
        """
        logger.info("用例编号：46-4----多个限价空单、多个市价多单，验证订单状态、用户余额")
        deal_num = 100000000
        random_num = 5

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        price = int(int(now_stock_price) * 0.95)

        # 下单前查询两个用户的可用余额
        before_buy_account_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_buy_account_balance = before_buy_account_dict["balance"]

        before_sell_account_dict = account_info(user=self.seller, session=self.sell_session, sda_id=sda_id)
        before_sell_account_balance = before_sell_account_dict["balance"]

        buy_sync_id = None
        for i in range(random_num):
            # 循环下多单
            buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=空单, order_price_type=限价, order_price=price, order_num=deal_num
            ))
            buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
                self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
            ))
            # time.sleep(1)

        sell_sync_id = None
        for v in range(random_num):
            # 循环下5个空单
            sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
                sda_id=sda_id, order_type=多单, order_price_type=市价, order_price=price, order_num=deal_num
            ))
            sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
                self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
            ))
            # time.sleep(1)

        # time.sleep(2)

        # 下单结束后查询两个用户可用余额
        after_buy_account_dict = account_info_sync(sync_id=buy_sync_id, user=self.buyer, session=self.session,
                                                   sda_id=sda_id)
        after_buy_account_balance = after_buy_account_dict["balance"]

        after_sell_account_dict = account_info_sync(sync_id=sell_sync_id, user=self.seller, session=self.sell_session,
                                                    sda_id=sda_id)
        after_sell_account_balance = after_sell_account_dict["balance"]

        buy_flag = assert_one(self.sda_balance, int(after_buy_account_balance) +
                              int(random_num * deal_num * price / 100000000))
        sell_flag = assert_one(self.sda_balance, int(after_sell_account_balance) +
                               int(random_num * deal_num * price / 100000000))
        self.assertListEqual([True, True], [buy_flag, sell_flag])


if __name__ == '__main__':
    unittest.main()
