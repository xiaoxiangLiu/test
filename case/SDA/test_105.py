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
    杠杆下单接口测试类
    """
    def test_01(self):
        """
        限价多单5倍杠杆委托，正常下单。
        """
        logger.info("用例编号：105-1---限价多单委托，5倍杠杆，正常下单。")
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

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下限价委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      lever="5",
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

        # 查询下委托后的可用余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        after_balance = after_info_dict["balance"]
        print("price * num", price*num/5/100000000)
        flag_one = assert_one(int(before_balance), int(after_balance) + int(price * num / 5 / 100000000))
        flag_two = assert_list([int(order_quantity), int(order_price), order_status], [num, price, "0"])
        flag_three = assert_list([200, "SUCCESS", "0"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True, True], [flag_one, flag_two, flag_three])

    def test_02(self):
        """
        限价多单，10倍杠杆，正常下单
        :return:
        """
        logger.info("用例编号：105-2---限价多单委托，10倍杠杆，正常下单。")
        price = 100000000
        num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=990000000000)

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下限价委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      lever="10",
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

        # 查询下委托后的可用余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        after_balance = after_info_dict["balance"]

        flag_one = assert_one(int(before_balance), int(after_balance) + int(price * num / 10 / 100000000))
        flag_two = assert_list([int(order_quantity), int(order_price), order_status], [num, price, "0"])
        flag_three = assert_list([200, "SUCCESS", "0"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True, True], [flag_one, flag_two, flag_three])

    def test_03(self):
        """
        限价多单，20倍杠杆下单，
        :return:
        """
        logger.info("用例编号：105-3---限价多单委托，20倍杠杆，正常下单。")
        price = 100000000
        num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=990000000000)

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下限价委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      lever="20",
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

        # 查询下委托后的可用余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        after_balance = after_info_dict["balance"]

        flag_one = assert_one(int(before_balance), int(after_balance) + int(price * num / 20 / 100000000))
        flag_two = assert_list([int(order_quantity), int(order_price), order_status], [num, price, "0"])
        flag_three = assert_list([200, "SUCCESS", "0"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True, True], [flag_one, flag_two, flag_three])

    def test_04(self):
        """
        限价多单，50倍杠杆下单
        :return:
        """
        logger.info("用例编号：105-4---限价多单委托，50倍杠杆，正常下单。")
        price = 100000000
        num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=990000000000)

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下限价委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      lever="50",
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

        # 查询下委托后的可用余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        after_balance = after_info_dict["balance"]

        flag_one = assert_one(int(before_balance), int(after_balance) + int(price * num / 50 / 100000000))
        flag_two = assert_list([int(order_quantity), int(order_price), order_status], [num, price, "0"])
        flag_three = assert_list([200, "SUCCESS", "0"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True, True], [flag_one, flag_two, flag_three])

    def test_05(self):
        """
        限价多单，100倍杠杆下单。
        :return:
        """
        logger.info("用例编号：105-5---限价多单委托，100倍杠杆，正常下单。")
        price = 100000000
        num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=990000000000)

        # 查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下限价委托
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      lever="100",
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

        # 查询下委托后的可用余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        after_balance = after_info_dict["balance"]

        flag_one = assert_one(int(before_balance), int(after_balance) + int(price * num / 100 / 100000000))
        flag_two = assert_list([int(order_quantity), int(order_price), order_status], [num, price, "0"])
        flag_three = assert_list([200, "SUCCESS", "0"], [order_resp.status_code, msg, status])
        self.assertListEqual([True, True, True], [flag_one, flag_two, flag_three])


if __name__ == '__main__':
    unittest.main()