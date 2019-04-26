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
from common._mytest import query_order_get_open
from common._mytest import account_info
from common._mytest import assert_one
from common.logger import logger
from common._mytest import account_info_sync
from common._mytest import market_info_get
from common.AccountTest.AccountUtil import employBalance
from common._mytest import sda_sync_lock
from common.myException import SyncException
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
    下单接口测试类
    """
    def test_01(self):
        """
        限价多单委托，正常下单。
        """
        logger.info("用例编号：6-1---限价多单委托，正常下单。")
        price = 100000000
        num = 100000000
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(stock_price_dict["stockPrice"])
        stock_unit = int(stock_price_dict["tradeUnit"])

        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=990000000000)

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下限价委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      order_price_type=限价,
                                                                                                      order_price=price,
                                                                                                      order_num=num,))
        logger.info("下单：{}".format(order_resp.text))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)
        order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=order_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)

        # 查询当前委托
        # time.sleep(1)
        get_open_dict = query_order_get_open(user=self.buyer, session=self.session, order_id=order_id)
        order_quantity = get_open_dict["orderQuantity"]  # 委托数量
        order_price = get_open_dict["orderPrice"]  # 委托价格
        order_status = get_open_dict["orderStatus"]  # 委托状态

        # 查询下委托后的可用余额
        time.sleep(5)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        employ_balance = employBalance(price=price, count=num, unit=stock_unit, lever=1)

        flag_one = assert_one(int(before_balance), int(after_balance) + int(employ_balance))
        flag_two = assert_list([int(order_quantity), int(order_price), order_status], [num, price, "0"])
        flag_three = assert_list([200, "SUCCESS", "0"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True, True], [flag_one, flag_two, flag_three])

    def test_02(self):
        """
        限价空单委托，正常下单。
        """
        logger.info("用例编号：6-2----限价空单委托，正常下单。")

        num = 1000000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=990000000000)

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]
        stock_unit = int(stock_price_dict["tradeUnit"])
        price = int(int(now_stock_price) * 0.95)
        # 下委托前查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下限价空单委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=空单,
                                                                                                      order_price_type=限价,
                                                                                                      order_price=price,
                                                                                                      order_num=num,))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)
        order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=order_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)

        # 查询当前委托
        # time.sleep(1)
        get_open_dict = query_order_get_open(user=self.buyer, session=self.session, order_id=order_id)
        order_quantity = get_open_dict["orderQuantity"]  # 委托数量
        order_price = get_open_dict["orderPrice"]  # 委托价格
        order_status = get_open_dict["orderStatus"]  # 委托状态

        # 查询委托后可用余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]
        employ_balance = employBalance(price=price, count=num, unit=stock_unit, lever=1)
        flag_one = assert_one(int(before_balance), int(after_balance) + int(employ_balance))
        flag_two = assert_list([int(order_quantity), int(order_price), order_status], [num, price, "0"])
        flag_three = assert_list([200, "SUCCESS", "0"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True, True], [flag_one, flag_two, flag_three])

    def test_03(self):
        """
        市价多单委托，正常下单。
        """
        logger.info("用例编号：6-3---市价多单委托，正常下单。")
        price = 100000000
        num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=990000000000)

        # 下市价多单委托
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下市价委托单
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      order_price_type=市价,
                                                                                                      order_num=num,))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url,order_resp.json()))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)
        order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=order_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)

        # time.sleep(1)

        # 查询下委托后可用余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        one_flag = assert_one(int(before_balance), int(after_balance))
        list_flag = assert_list([200, "SUCCESS", "0"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True], [one_flag, list_flag])

    def test_04(self):
        """
        市价空单委托，正常下单。
        """
        logger.info("用例编号：6-4--市价空单委托，正常下单。")
        price = 100000000
        num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=990000000000)

        # 下委托前查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=空单,
                                                                                                      order_price_type=市价,
                                                                                                      order_price=price,
                                                                                                      order_num=num))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, order_resp.json()))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)
        order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=order_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)

        # 下委托后查询可用余额
        # time.sleep(1)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        one_flag = assert_one(int(before_balance), int(after_balance))
        list_flag = assert_list([200, "SUCCESS", "0"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True], [one_flag, list_flag])

    def test_05(self):
        """
        限价多单，循环多次下单，验证可用余额
        :return:
        """
        logger.info("用例编号：6-5--限价多单，循环多次下单，验证可用余额")
        price = 100000000
        sda_balance = 9999999900000000
        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]
        stock_unit = int(stock_price_dict["tradeUnit"])

        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=sda_balance)

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下单前查询用户的余额
        buy_balance = self.session.post(url=base + sda_account_asset_detail_get_url,
                                        data=get_sda_account_asset_detail_get_param())
        buy_balance_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].availableMargin",
                                                        body=buy_balance.text)
        buy_entrust_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].entrustMargin", body=buy_balance.text)
        logger.info(
            "用户：{0}---接口：{1}---状态：{2}---下单前可用保证金：{3}--委托保证金：{4}".format(self.buyer,
                                                                        sda_account_asset_detail_get_url,
                                                                        buy_balance.status_code, buy_balance_value,
                                                                        buy_entrust_value))

        # 下限价委托
        amount_list = []
        sync_flag_list = []
        employ_balance_list = []
        for i in range(200):
            amount = random.randint(1, 100) * 100000000
            amount_list.append(amount)
            order_resp = self.session.post(url=base + sda_order_create_url,
                                           data=get_sda_order_create_param(sda_id=sda_id, order_type=多单,
                                                                           order_price_type=限价, order_price=price,
                                                                           order_num=amount))
            sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)
            logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, order_resp.json()))
            sync_flag = sda_sync_lock(session=self.session, sync_id=sync_id)
            sync_flag_list.append(sync_flag)
            # time.sleep(0.1)
            # 计算每次下单所使用的保证金
            employ_balance = employBalance(price=price, count=amount, unit=stock_unit, lever=1)
            employ_balance_list.append(employ_balance)

        # 查询下委托后的可用余额
        # time.sleep(2)
        for v in sync_flag_list:
            if "OK" != v:
                raise SyncException("sync lock 异常")
        else:
            after_info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
            after_balance = after_info_dict["balance"]

        # 查询用户余额，然后判断下单前后的用户余额
        after_buy_balance = self.session.post(url=base + sda_account_asset_detail_get_url,
                                              data=get_sda_account_asset_detail_get_param())
        after_buy_balance_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].availableMargin",
                                                              body=after_buy_balance.text)
        after_buy_entrust_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].entrustMargin",
                                                              body=after_buy_balance.text)
        logger.info("用户：{0}---接口：{1}---状态：{2}---下单后可用保证金：{3}---下单后委托保证金：{4}".format(self.buyer,
                                                                                    sda_account_asset_detail_get_url,
                                                                                    after_buy_balance.status_code,
                                                                                    after_buy_balance_value,
                                                                                    after_buy_entrust_value))

        flag_one = assert_one(int(before_balance), int(after_balance) + sum(employ_balance_list))
        # flag_two = assert_one(int(buy_entrust_value), int(after_buy_entrust_value) + sum(amount_list))
        self.assertTrue(flag_one)

    def test_06(self):
        """
        限价空单，循环下单，验证可用余额、委托保证金
        :return:
        """
        logger.info("用例编号：6-6---限价空单，循环下单，验证可用余额、委托保证金")
        sda_balance = 9999999900000000
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
        stock_unit = int(stock_price_dict["tradeUnit"])
        price = int(int(now_stock_price) * 0.95)

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下限价委托
        amount_list = []
        sync_flag_list = []
        employ_balance_list = []
        for i in range(50):
            amount = random.randint(1, 100) * 100000000
            amount_list.append(amount)
            order_resp = self.session.post(url=base + sda_order_create_url,
                                           data=get_sda_order_create_param(sda_id=sda_id, order_type=空单,
                                                                           order_price_type=限价, order_price=price,
                                                                           order_num=amount, ))
            sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)
            sync_flag = sda_sync_lock(session=self.session, sync_id=sync_id)
            sync_flag_list.append(sync_flag)
            logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, order_resp.json()))
            # time.sleep(0.1)
            employ_balance = employBalance(price=price, count=amount, unit=stock_unit, lever=1)
            employ_balance_list.append(employ_balance)

        # 查询下委托后的可用余额
        # time.sleep(3)
        for v in sync_flag_list:
            if "OK" != v:
                raise SyncException("sync lock 异常")
        else:
            after_info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id,
                                                price=1000000000)
            after_balance = after_info_dict["balance"]

        flag_one = assert_one(int(before_balance), int(after_balance) + sum(employ_balance_list))
        self.assertTrue(flag_one)

    def test_07(self):
        """
        市价多单，循环下单，验证可用余额、委托保证金
        """
        logger.info("用例编号：6-7---市价多单，循环下单，验证可用余额、委托保证金")
        price = 100000000
        sda_balance = 9999999900000000
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

        # 下单前查询用户的余额
        buy_balance = self.session.post(url=base + sda_account_asset_detail_get_url,
                                        data=get_sda_account_asset_detail_get_param())
        buy_balance_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].availableMargin",
                                                        body=buy_balance.text)
        buy_entrust_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].entrustMargin", body=buy_balance.text)
        logger.info(
            "用户：{0}---接口：{1}---状态：{2}---下单前可用保证金：{3}--委托保证金：{4}".format(self.buyer,
                                                                        sda_account_asset_detail_get_url,
                                                                        buy_balance.status_code, buy_balance_value,
                                                                        buy_entrust_value))

        # 下市价价委托
        amount_list = []
        sync_flag_list = []
        for i in range(200):
            amount = random.randint(1, 100) * 100000000
            amount_list.append(amount)
            order_resp = self.session.post(url=base + sda_order_create_url,
                                           data=get_sda_order_create_param(sda_id=sda_id, order_type=多单,
                                                                           order_price_type=市价,
                                                                           order_num=amount, ))
            sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)
            sync_flag = sda_sync_lock(session=self.session, sync_id=sync_id)
            sync_flag_list.append(sync_flag)
            logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, order_resp.json()))
            # time.sleep(0.1)

        # 查询下委托后的可用余额
        # time.sleep(1)
        for v in sync_flag_list:
            if "OK" != v:
                raise SyncException("sync lock 异常")
        else:
            after_info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id,
                                                price=1000000000)
            after_balance = after_info_dict["balance"]

        # 查询用户余额，然后判断下单前后的用户余额
        after_buy_balance = self.session.post(url=base + sda_account_asset_detail_get_url,
                                              data=get_sda_account_asset_detail_get_param())
        after_buy_balance_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].availableMargin",
                                                              body=after_buy_balance.text)
        after_buy_entrust_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].entrustMargin",
                                                              body=after_buy_balance.text)
        logger.info("用户：{0}---接口：{1}---状态：{2}---下单后可用保证金：{3}---下单后委托保证金：{4}".format(self.buyer,
                                                                                    sda_account_asset_detail_get_url,
                                                                                    after_buy_balance.status_code,
                                                                                    after_buy_balance_value,
                                                                                    after_buy_entrust_value))

        flag_one = assert_one(int(before_balance), int(after_balance))
        # flag_two = assert_one(int(buy_entrust_value), int(after_buy_entrust_value))
        self.assertTrue(flag_one)

    def test_08(self):
        """
        市价空单，循环下单，验证可用余额、委托保证金
        """
        sda_balance = 9999999900000000
        logger.info("用例编号：6-8----时间空单，循环下单，验证可用余额、委托保证金")
        price = 100000000
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

        # 下单前查询用户的余额
        buy_balance = self.session.post(url=base + sda_account_asset_detail_get_url,
                                        data=get_sda_account_asset_detail_get_param())
        buy_balance_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].availableMargin",
                                                        body=buy_balance.text)
        buy_entrust_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].entrustMargin", body=buy_balance.text)
        logger.info(
            "用户：{0}---接口：{1}---状态：{2}---下单前可用保证金：{3}--委托保证金：{4}".format(self.buyer,
                                                                        sda_account_asset_detail_get_url,
                                                                        buy_balance.status_code, buy_balance_value,
                                                                        buy_entrust_value))

        # 下市价价委托
        sync_id = None
        amount_list = []
        sync_flag_list = []
        for i in range(500):
            amount = random.randint(1, 100) * 100000000
            amount_list.append(amount)
            order_resp = self.session.post(url=base + sda_order_create_url,
                                           data=get_sda_order_create_param(sda_id=sda_id, order_type=空单,
                                                                           order_price_type=市价,
                                                                           order_num=amount, ))
            sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)
            logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, order_resp.json()))
            sync_flag = sda_sync_lock(session=self.session, sync_id=sync_id)
            sync_flag_list.append(sync_flag)
            # time.sleep(0.1)

        # 查询下委托后的可用余额
        # time.sleep(1)
        for v in sync_flag_list:
            if "OK" != v:
                raise SyncException("sync lock 异常")
        else:
            after_info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id,
                                                price=1000000000)
            after_balance = after_info_dict["balance"]

        # 查询用户余额，然后判断下单前后的用户余额
        after_buy_balance = self.session.post(url=base + sda_account_asset_detail_get_url,
                                              data=get_sda_account_asset_detail_get_param())
        after_buy_balance_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].availableMargin",
                                                              body=after_buy_balance.text)
        after_buy_entrust_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].entrustMargin",
                                                              body=after_buy_balance.text)
        logger.info("用户：{0}---接口：{1}---状态：{2}---下单后可用保证金：{3}---下单后委托保证金：{4}".format(self.buyer,
                                                                                    sda_account_asset_detail_get_url,
                                                                                    after_buy_balance.status_code,
                                                                                    after_buy_balance_value,
                                                                                    after_buy_entrust_value))

        flag_one = assert_one(int(before_balance), int(after_balance))
        # flag_two = assert_one(int(buy_entrust_value), int(after_buy_entrust_value))
        self.assertTrue(flag_one)

    def tet_09(self):
        """
        限价平空单委托，正常下单。
        """
        logger.info("用例编号：6-9--限价平空单委托，正常下单。")
        price = 100000000
        num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=990000000000)

        # 下委托前查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=平空,
                                                                                                      order_price_type=限价,
                                                                                                      order_price=price,
                                                                                                      order_num=num))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, order_resp.json()))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)
        order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=order_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=order_resp.text)

        # 下委托后查询可用余额
        # time.sleep(1)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        one_flag = assert_one(int(before_balance), int(after_balance))
        list_flag = assert_list([200, "SUCCESS", "0"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True], [one_flag, list_flag])


if __name__ == '__main__':
    unittest.main()
