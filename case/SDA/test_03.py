__author__ = '123'
# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.params import *
from common.connectMysql import ConnectMysql
from common.jsonparser import JMESPathExtractor
from common.logger import logger
from common._mytest import account_info
from common._mytest import assert_one
from common._mytest import account_info_sync
from common._mytest import ConnectRedis
from common.myException import SyncException
from common._mytest import sda_sync_lock
import random
import time

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_account_withdraw_url = names.sda_account_withdraw_url
user_balance_servlet_url = names.get_user_balance_servlet_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url
get_user_balance_servlet_url = names.get_user_balance_servlet_url
currency_id = 2


class TestCase(MytestOnePlayer):
    """
    合约账户转到币币账户接口测试类
    """
    def test_01(self):
        """
        正常访问，验证接口状态、MSG、STATUS，验证bb账户余额，合约账户余额
        """
        logger.info("用例编号：3-1---合约账户转到币币账户接口测试类--正常访问，验证接口状态、MSG、STATUS，验证bb账户余额、合约账户余额")
        amount = 100000000
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=10000000000)

        # 转出前查询bb账户余额
        before_bb_account_resp = self.session.post(url=base+user_balance_servlet_url,
                                                   data=get_user_balance_servlet_param(user=self.buyer,
                                                                                       currency_id=currency_id))
        before_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue",
                                                              body=before_bb_account_resp.text)
        logger.info("用户：{0}---币ID：{1}---转入前余额：{2}".format(self.buyer, currency_id, before_currency_balance))

        # 转出前查询合约账户余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_account_balance = info_dict["balance"]

        # 转出
        withdraw_resp = self.session.post(url=base+sda_account_withdraw_url,
                                          data=get_sda_account_withdraw_param(sda_id=sda_id, amount=amount))
        msg = JMESPathExtractor().extract(query="MSG", body=withdraw_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=withdraw_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=withdraw_resp.text)
        logger.info("用户：{0}--接口：{1}---状态：{2}--转出金额：{3}--返回信息：{4}".format(self.buyer, sda_account_withdraw_url,withdraw_resp.status_code, amount, withdraw_resp.json()))

        # time.sleep(3)
        # 转出后查询合约账户余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id)
        after_account_balance = after_info_dict["balance"]

        # 转出后查询BB账户余额
        # time.sleep(1)
        after_bb_account_resp = self.session.post(url=base+user_balance_servlet_url, data=get_user_balance_servlet_param(self.buyer, currency_id=currency_id))
        after_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_bb_account_resp.text)
        logger.info("用户：{0}--币ID：{1}--转入后余额：{2}".format(self.buyer, currency_id, after_currency_balance))
        logger.info("转出金额：{}".format(amount))
        self.assertListEqual([200, "SUCCESS", "0"], [withdraw_resp.status_code, msg, status])
        self.assertEqual(int(before_currency_balance) + amount, int(after_currency_balance))
        self.assertEqual(int(before_account_balance) - int(amount), int(after_account_balance))

    def test_02(self):
        """
        合约账户余额不足，转出，验证接口状态、MSG、STATUS，验证bb账户余额，合约账户余额
        """
        logger.info("用例编号：3-2---合约账户转到币币账户接口测试类--合约账户余额不足，转出，验证接口状态、MSG、STATUS，验证bb账户余额、合约账户余额")
        amount = 100000000
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=0)

        before_bb_account_resp = self.session.post(url=base+user_balance_servlet_url, data=get_user_balance_servlet_param(user=self.buyer, currency_id=currency_id))
        before_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=before_bb_account_resp.text)
        logger.info("用户：{0}---币ID：{1}---转入前余额：{2}".format(self.buyer, currency_id, before_currency_balance))

        # 转出前查询合约账户余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_account_balance = info_dict["balance"]

        withdraw_resp = self.session.post(url=base+sda_account_withdraw_url, data=get_sda_account_withdraw_param(sda_id=sda_id, amount=amount))
        msg = JMESPathExtractor().extract(query="MSG", body=withdraw_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=withdraw_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=withdraw_resp.text)

        # 转出后查询合约账户余额
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id)
        after_account_balance = after_info_dict["balance"]

        # time.sleep(1)
        after_bb_account_resp = self.session.post(url=base+user_balance_servlet_url, data=get_user_balance_servlet_param(self.buyer, currency_id=currency_id))
        after_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_bb_account_resp.text)
        logger.info("用户：{0}--接口：{1}---状态：{2}--转出金额：{3}--返回信息：{4}".format(self.buyer, sda_account_withdraw_url,withdraw_resp.status_code, amount, withdraw_resp.json()))
        logger.info("用户：{0}--币ID：{1}--转入后余额：{2}".format(self.buyer, currency_id, after_currency_balance))

        self.assertListEqual([200, "账户余额不足", "2"], [withdraw_resp.status_code, msg, status])
        self.assertEqual(int(before_currency_balance), int(after_currency_balance))
        flag = assert_one(int(before_account_balance), int(after_account_balance))
        self.assertTrue(flag)

    def test_03(self):
        """
        合约账户余额充足，随机提现多次，验证接口状态、MSG、STATUS，验证bb账户，合约账户余额
        """
        logger.info("用例编号：3-3--合约账户转到币币账户接口测试类，合约账户余额充足，随机提现多次，验证接口状态、MSG、STATUS、验证Bb账户余额、合约账户余额")
        sda_balance = 999999900000000
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=sda_balance)

        # 转出前查询合约账户余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_account_balance = info_dict["balance"]

        # 转入前查询bb账户余额
        before_bb_account_resp = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=self.buyer, currency_id=currency_id))
        before_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=before_bb_account_resp.text)
        logger.info("用户：{0}---币ID：{1}---转入前余额：{2}".format(self.buyer, currency_id, before_currency_balance))

        amount_list = []
        sync_flag_list = []
        for i in range(100):  # 循环下1000次
            amount = random.randint(1, 1000) * 100000000
            amount_list.append(amount)
            withdraw_resp = self.session.post(url=base+sda_account_withdraw_url, data=get_sda_account_withdraw_param(sda_id=sda_id, amount=amount))
            logger.info("转出金额：{0}----接口返回信息：{1}".format(amount, withdraw_resp.json()))
            # msg = JMESPathExtractor().extract(query="MSG", body=withdraw_resp.text)
            # status = JMESPathExtractor().extract(query="STATUS", body=withdraw_resp.text)
            sync_id = JMESPathExtractor().extract(query="syncLockKey", body=withdraw_resp.text)
            sync_flag = sda_sync_lock(session=self.session, sync_id=sync_id)
            sync_flag_list.append(sync_flag)
            logger.info("转出次数：{}".format(i))
            # time.sleep(0.5)

        # 转出后查询合约账户余额
        for i in sync_flag_list:
            if "OK" != i:
                raise SyncException("sync lock 异常")
        else:
            after_info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
            after_account_balance = after_info_dict["balance"]

        # 转出后查询BB账户余额
        time.sleep(1)
        after_bb_account_resp = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(self.buyer, currency_id=currency_id))
        after_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_bb_account_resp.text)
        logger.info("用户：{0}--币ID：{1}--转入后余额：{2}".format(self.buyer, currency_id, after_currency_balance))
        logger.info("转出前余额：{}".format(before_account_balance))
        logger.info("转出后余额：{}".format(after_account_balance))
        logger.info("转出总量：{}".format(sum(amount_list)))
        logger.info("转出前BB账户余额：{}".format(before_currency_balance))
        logger.info("转出后BB账户余额：{}".format(after_currency_balance))
        logger.info("转出金额列表：{}".format(amount_list))
        bb_flag = assert_one(int(before_currency_balance), int(after_currency_balance) - sum(amount_list))
        sda_flag = assert_one(int(before_account_balance), int(after_account_balance) + sum(amount_list))
        self.assertListEqual([True, True], [bb_flag, sda_flag])

    def test_04(self):
        """
        合约账户余额正好等于转出数量，验证合约账户余额、BB账户余额
        :return:
        """
        logger.info("用例编号：3-4---合约账户余额正好等于转出数量，验证合约账户余额、BB账户余额")
        amount = random.randint(1, 1000) * 100000000
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=amount)

        # 转出前查询合约账户余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_account_balance = info_dict["balance"]

        # 转入前查询bb账户余额
        before_bb_account_resp = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=self.buyer, currency_id=currency_id))
        before_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=before_bb_account_resp.text)
        logger.info("用户：{0}---币ID：{1}---转入前余额：{2}".format(self.buyer, currency_id, before_currency_balance))

        withdraw_resp = self.session.post(url=base+sda_account_withdraw_url, data=get_sda_account_withdraw_param(sda_id=sda_id, amount=amount))
        logger.info("转出接口：{0}----返回信息：{1}".format(sda_account_withdraw_url, withdraw_resp.json()))
        msg = JMESPathExtractor().extract(query="MSG", body=withdraw_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=withdraw_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=withdraw_resp.text)

        # 转出后查询合约账户余额
        # time.sleep(0.5)
        after_info_dict = account_info_sync(sync_id=sync_id,user=self.buyer, session=self.session, sda_id=sda_id)
        after_account_balance = after_info_dict["balance"]

        # 转出后查询BB账户余额
        time.sleep(2)
        after_bb_account_resp = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(self.buyer, currency_id=currency_id))
        after_currency_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_bb_account_resp.text)
        logger.info("用户：{0}--币ID：{1}--转入后余额：{2}".format(self.buyer, currency_id, after_currency_balance))
        logger.info("转出数量：{}".format(amount))
        bb_flag = assert_one(int(before_currency_balance) + amount, int(after_currency_balance))
        sda_flag = assert_one(int(before_account_balance) - amount, int(after_account_balance))
        self.assertListEqual([True, True], [bb_flag, sda_flag])


if __name__ == '__main__':
    unittest.main()
