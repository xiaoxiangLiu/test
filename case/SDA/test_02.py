__author__ = '123'
# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.params import *
from common.logger import logger
from common.connectMysql import ConnectMysql
from common.jsonparser import JMESPathExtractor
from common._mytest import assert_list
from common._mytest import account_info
from common._mytest import assert_one
from common._mytest import ConnectRedis
from common._mytest import account_info_sync
from common._mytest import sda_sync_lock
from common.myException import SyncException
import time
import random

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_account_deposit_url = names.sda_account_deposit_url
get_user_balance_servlet_url = names.get_user_balance_servlet_url
currency_id = 2


class TestCase(MytestOnePlayer):
    """
    资金划转接口测试类，
    """
    def test_01(self):
        """
        正常访问资金划转接口，验证接口状态、status、msg
        """
        amount = 100000000
        logger.info("用例编号：2-1---资金划转接口测试类，正常访问资金划转接口，验证接口状态、status、msg")
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=self.buyer, currency_id=currency_id, balance_value=90000000000)

        # 转入前查询bb账户余额
        before_bb_account_resp = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=self.buyer, currency_id=currency_id))
        before_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=before_bb_account_resp.text)
        logger.info("用户：{0}---币ID：{1}---转入前余额：{2}".format(self.buyer, currency_id, before_currency_balance))

        # 转入前查询合约账户余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_account_balance = info_dict["balance"]

        deposit_resp = self.session.post(url=base+sda_account_deposit_url, data=get_sda_account_deposit_param(sda_id=sda_id, amount=amount))
        logger.info("用户：{0}---接口：{1}---状态：{2}---正常划转返回信息：{3}".format(self.buyer, sda_account_deposit_url, deposit_resp.status_code, deposit_resp.json()))
        status = JMESPathExtractor().extract(query="STATUS", body=deposit_resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=deposit_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=deposit_resp.text)
        print("msg:", type(msg))
        time.sleep(2)
        # 转入后查询合约账户余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id)
        after_account_balance = after_info_dict["balance"]

        # 转入后查询BB账户余额
        # time.sleep(1)
        after_bb_account_resp = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(self.buyer, currency_id=currency_id))
        after_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_bb_account_resp.text)
        logger.info("用户：{0}--币ID：{1}--转入后余额：{2}".format(self.buyer, currency_id, after_currency_balance))
        # _object = JMESPathExtractor().extract(query="OBJECT", body=deposit_resp.text)
        print("before account balance", before_account_balance)
        print("amount:", amount)
        print("after account balance:", after_account_balance)
        flag = assert_list([200, "0"], [deposit_resp.status_code, status])
        flag_1 = assert_one(int(before_currency_balance) - int(amount), int(after_currency_balance))
        flag_2 = assert_one(int(before_account_balance) + int(amount), int(after_account_balance))
        self.assertListEqual([True, True, True], [flag, flag_1, flag_2])

    def test_02(self):
        """
        用户余额为0，划转资金，验证接口状态、STATUS、MSG
        """
        logger.info("用例编号：2-2--------资金划转接口测试类，用户余额为0，划转资金，验证接口状态、STATUS、MSG")
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=self.buyer, currency_id=currency_id, balance_value=0)
        deposit_resp = self.session.post(url=base+sda_account_deposit_url, data=get_sda_account_deposit_param(sda_id=sda_id, amount=100000000))

        logger.info("用户：{0}---接口：{1}---状态：{2}---正常划转返回信息：{3}".format(self.buyer, sda_account_deposit_url, deposit_resp.status_code, deposit_resp.json()))

        status = JMESPathExtractor().extract(query="STATUS", body=deposit_resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=deposit_resp.text)
        # _object = JMESPathExtractor().extract(query="OBJECT", body=deposit_resp.text)
        flag = assert_list([200, "1", "平台账户余额不足"], [deposit_resp.status_code, status, msg])
        self.assertTrue(flag)

    def test_03(self):
        """
        用户余额正常，超额划转资金，验证接口状态、STATUS、MSG
        """
        logger.info("用例编号：2-3------------资金划转接口测试类，用户余额正常，超额划转资金，验证接口状态、STATUS、MSG")
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=self.buyer, currency_id=currency_id,
                                                            balance_value=100000000000)
        deposit_resp = self.session.post(url=base+sda_account_deposit_url,
                                         data=get_sda_account_deposit_param(sda_id=sda_id, amount=200000000000))

        logger.info("用户：{0}---接口：{1}---状态：{2}---返回信息：{3}".format(self.buyer, sda_account_deposit_url, deposit_resp.status_code, deposit_resp.json()))

        status = JMESPathExtractor().extract(query="STATUS", body=deposit_resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=deposit_resp.text)
        # _object = JMESPathExtractor().extract(query="OBJECT", body=deposit_resp.text)
        flag = assert_list([200, "1", "平台账户余额不足"], [deposit_resp.status_code, status, msg])
        self.assertTrue(flag)

    def test_04(self):
        """
        多次转入查询余额
        """
        logger.info("用例编号：02-4-多次转入查询余额")

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=self.buyer, currency_id=currency_id, balance_value=900000000000000)

        # 转入前查询bb账户余额
        before_bb_account_resp = self.session.post(url=base+get_user_balance_servlet_url,
                                                   data=get_user_balance_servlet_param(user=self.buyer,
                                                                                       currency_id=currency_id))
        before_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue",
                                                              body=before_bb_account_resp.text)
        logger.info("用户：{0}---币ID：{1}---转入前余额：{2}".format(self.buyer, currency_id, before_currency_balance))

        # 转入前查询合约账户余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_account_balance = info_dict["balance"]
        sync_flag_list = []
        amount_list = []
        for i in range(200):
            amount = random.randint(1, 1000) * 100000000
            amount_list.append(amount)
            deposit_resp = self.session.post(url=base+sda_account_deposit_url, data=get_sda_account_deposit_param(sda_id=sda_id, amount=amount))
            logger.info("用户：{0}---接口：{1}---状态：{2}---正常划转返回信息：{3}".format(self.buyer, sda_account_deposit_url, deposit_resp.status_code, deposit_resp.json()))
            # status = JMESPathExtractor().extract(query="STATUS", body=deposit_resp.text)
            # msg = JMESPathExtractor().extract(query="MSG", body=deposit_resp.text)
            sync_id = JMESPathExtractor().extract(query="syncLockKey", body=deposit_resp.text)
            sync_flag = sda_sync_lock(session=self.session, sync_id=sync_id)
            sync_flag_list.append(sync_flag)
            logger.info("转入次数：{}".format(i))
            time.sleep(0.1)

        # time.sleep(2)
        # 转入后查询合约账户余额
        for i in sync_flag_list:
            if "OK" != i:
                raise SyncException("sync lock 返回的不是ok!")
        else:
            after_info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
            after_account_balance = after_info_dict["balance"]

        # 转入后查询BB账户余额
        # time.sleep(1)
        after_bb_account_resp = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(self.buyer, currency_id=currency_id))
        after_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_bb_account_resp.text)
        logger.info("用户：{0}--币ID：{1}--转入后余额：{2}".format(self.buyer, currency_id, after_currency_balance))
        # _object = JMESPathExtractor().extract(query="OBJECT", body=deposit_resp.text)

        # flag = assert_list([200, "0", "SUCCESS"], [deposit_resp.status_code, status, msg])
        logger.info("用户总转入数量：{}".format(sum(amount_list)))
        logger.info("转入之前总量：{}".format(before_account_balance))
        logger.info("转入之后的总量：{}".format(after_account_balance))
        flag_1 = assert_one(int(before_currency_balance) - int(sum(amount_list)), int(after_currency_balance))
        flag_2 = assert_one(int(before_account_balance) + int(sum(amount_list)), int(after_account_balance))
        self.assertListEqual([True, True], [flag_1, flag_2])


if __name__ == '__main__':
    unittest.main()
