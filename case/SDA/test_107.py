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
from common._mytest import account_info
from common._mytest import assert_one
from common.logger import logger
from common._mytest import account_info_sync


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
        市价多单5倍杠杆委托，正常下单。
        """
        logger.info("用例编号：107-1---市价多单5倍杠杆委托，正常下单。")
        price = 100000000
        num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=990000000000)

        # 下市价多单委托
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下市价委托单
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                      order_type=多单,
                                                                                                      order_price_type=市价,
                                                                                                      lever="5",
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

    def test_02(self):
        """
        市价多单10倍杠杆委托，正常下单。
        """
        logger.info("用例编号：107-2---市价多单10倍杠杆委托，正常下单。")
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
        order_resp = self.session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                        order_type=多单,
                                                                                                        order_price_type=市价,
                                                                                                        lever="10",
                                                                                                        order_num=num, ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, order_resp.json()))
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

    def test_03(self):
        """
        市价多单20倍杠杆委托，正常下单。
        """
        logger.info("用例编号：107-3---市价多单20倍杠杆委托，正常下单。")
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
        order_resp = self.session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                        order_type=多单,
                                                                                                        order_price_type=市价,
                                                                                                        lever="20",
                                                                                                        order_num=num, ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, order_resp.json()))
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
        市价多单50倍杠杆委托，正常下单。
        """
        logger.info("用例编号：107-4---市价多单50倍杠杆委托，正常下单。")
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
        order_resp = self.session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                        order_type=多单,
                                                                                                        order_price_type=市价,
                                                                                                        lever="10",
                                                                                                        order_num=num, ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, order_resp.json()))
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

    def test_05(self):
        """
        市价多单100倍杠杆委托，正常下单。
        """
        logger.info("用例编号：107-2---市价多单100倍杠杆委托，正常下单。")
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
        order_resp = self.session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                        order_type=多单,
                                                                                                        order_price_type=市价,
                                                                                                        lever="100",
                                                                                                        order_num=num, ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, order_resp.json()))
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


if __name__ == '__main__':
    unittest.main()