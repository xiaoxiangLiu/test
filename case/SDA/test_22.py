__author__ = '123'
# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.params import *
from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
from common.jsonparser import JMESPathExtractor
from common._mytest import assert_list
from common._mytest import account_info_sync
from common._mytest import account_info
from common._mytest import assert_one
from common.logger import logger
from common._mytest import market_info_get
import time
import random


base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_create_url = names.sda_order_create_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan


class TestCase(MytestOnePlayer):
    """
    下单，下单数量大于可用余额
    """

    def test_01(self):
        """
        下限价多单单，下单数量大于可用余额
        """
        logger.info("用例编号：22-1---下限价多单，下单数量大于可用余额")
        sda_balance = 9000000000000
        price = 100000000
        num = sda_balance + 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=sda_balance)

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_balance = info_dict["balance"]

        # 下限价委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      order_price_type=限价,
                                                                                                      order_price=price,
                                                                                                      order_num=num,))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)
        # order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=order_resp.text)

        # 查询当前委托
        # get_open_dict = query_order_get_open(user=self.buyer, session=self.session, order_id=order_id)
        # order_quantity = get_open_dict["orderQuantity"]  # 委托数量
        # order_price = get_open_dict["orderPrice"]  # 委托价格
        # order_status = get_open_dict["orderStatus"]  # 委托状态

        # 查询下委托后的可用余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        flag_one = assert_one(int(before_balance), int(after_balance))
        flag_three = assert_list([200, "可建仓余额不足", "1"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True], [flag_one, flag_three])

    def test_02(self):
        """
        限价空单，下单数量小于可用余额数量，验证下单状态。
        """
        logger.info("用例编号：22-2---限价空单，下单数量小于可用余额数量，验证下单状态。")
        sda_balance = 9000000000000
        num = sda_balance + 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=sda_balance)

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        price = int(int(now_stock_price) * 0.95)

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_balance = info_dict["balance"]

        # 下限价委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=空单,
                                                                                                      order_price_type=限价,
                                                                                                      order_price=price,
                                                                                                      order_num=num,))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)
        # order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=order_resp.text)

        # 查询当前委托
        # get_open_dict = query_order_get_open(user=self.buyer, session=self.session, order_id=order_id)
        # order_quantity = get_open_dict["orderQuantity"]  # 委托数量
        # order_price = get_open_dict["orderPrice"]  # 委托价格
        # order_status = get_open_dict["orderStatus"]  # 委托状态

        # 查询下委托后的可用余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id)
        after_balance = after_info_dict["balance"]

        flag_one = assert_one(int(before_balance), int(after_balance))
        flag_three = assert_list([200, "该订单将会触发您所持仓位的强平", "1"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True], [flag_one, flag_three])

    def test_03(self):
        """
        市价多单，可用余额小于下单数量，验证下单是否成功。
        """
        logger.info("用例编号：22-3--市价多单，可用余额小于下单数量，验证下单是否成功。")
        sda_balance = 9000000000000
        price = 100000000
        num = sda_balance + 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=sda_balance)

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_balance = info_dict["balance"]

        # 下市价价委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      order_price_type=市价,
                                                                                                      order_num=num,))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)
        # order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=order_resp.text)

        # 查询当前委托
        # get_open_dict = query_order_get_open(user=self.buyer, session=self.session, order_id=order_id)
        # order_quantity = get_open_dict["orderQuantity"]  # 委托数量
        # order_price = get_open_dict["orderPrice"]  # 委托价格
        # order_status = get_open_dict["orderStatus"]  # 委托状态

        # 查询下委托后的可用余额
        # time.sleep(3)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        flag_one = assert_one(int(before_balance), int(after_balance))
        flag_three = assert_list([200, "可建仓余额不足", "1"], [order_resp.status_code, msg, status])
        self.assertTrue(flag_one)

    def test_04(self):
        """
        市价空单，可用余额小于下单数量，验证下单是否成功
        """
        logger.info("用例编号：20-4---市价空单，可用余额小于下单数量，验证下单是否成功")
        sda_balance = 9000000000000
        price = 100000000
        num = sda_balance + 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=sda_balance)

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_balance = info_dict["balance"]

        # 下市价价委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=空单,
                                                                                                      order_price_type=市价,
                                                                                                      order_num=num,))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)
        # order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=order_resp.text)

        # 查询当前委托
        # get_open_dict = query_order_get_open(user=self.buyer, session=self.session, order_id=order_id)
        # order_quantity = get_open_dict["orderQuantity"]  # 委托数量
        # order_price = get_open_dict["orderPrice"]  # 委托价格
        # order_status = get_open_dict["orderStatus"]  # 委托状态

        # 查询下委托后的可用余额
        # time.sleep(3)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        flag_one = assert_one(int(before_balance), int(after_balance))
        flag_three = assert_list([200, "可建仓余额不足", "1"], [order_resp.status_code, msg, status])
        self.assertTrue(flag_one)


if __name__ == '__main__':
    unittest.main()
