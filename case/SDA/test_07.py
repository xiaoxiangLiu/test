__author__ = '123'
# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.connectMysql import ConnectMysql
from common._mytest import assert_list
from common._mytest import assert_one
from common.connectRedis import ConnectRedis
from common.logger import logger
from common.names import order_type
from common._mytest import account_info
from common._mytest import market_info_get
import time
from common._mytest import account_info_sync

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_cancel_url = names.sda_order_cancel_url
sda_order_create_url = names.sda_order_create_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url
sda_order_get_open_url = names.sda_order_get_open_url

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan


class TestCase(MytestOnePlayer):
    """
    撤单接口测试类
    """

    def test_01(self):
        """
        下限价多单，撤单，验证用户余额，委托保证金余额
        """
        logger.info("用例编号：7-1--下多单，撤单，验证用户余额，委托保证金余额，")
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=990000000000000)
        deal_price = 100000000
        deal_num = 100000000

        # 下委托前查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下多单限价
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id,order_type=order_type.多单,order_price_type=order_type.限价,order_price=deal_price,order_num=deal_num
        ))
        buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=buy_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))

        # 撤单
        time.sleep(1)
        cancel_resp = self.session.post(url=base+sda_order_cancel_url, data=get_sda_order_cancel_param(sda_id=sda_id, order_id=buy_order_id, order_type=多单))
        logger.info("撤单接口状态：{0}---返回信息：{1}".format(cancel_resp.status_code, cancel_resp.json()))
        cancel_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=cancel_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=cancel_resp.text)
        cancel_msg = JMESPathExtractor().extract(query="MSG", body=cancel_resp.text)

        # 下委托后查询可用余额
        time.sleep(1)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        order_id_flag = assert_list([buy_order_id, 200, "SUCCESS"], [cancel_order_id, cancel_resp.status_code, cancel_msg])
        available_margin_flag = assert_one(int(before_balance), int(after_balance) )
        self.assertListEqual([True, True], [available_margin_flag, order_id_flag])

    def test_02(self):
        """
        下限价空单，撤单，验证用户余额，委托保证金余额
        """
        logger.info("用例编号：7-2--下多单，撤单，验证用户余额，委托保证金余额，")
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=990000000000000)

        deal_num = 100000000

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        price = int(int(now_stock_price) * 0.95)

        # 下单前查询用户的余额
        buy_balance = self.session.post(url=base+sda_account_asset_detail_get_url, data=get_sda_account_asset_detail_get_param())
        buy_balance_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].availableMargin",body=buy_balance.text)
        buy_entrust_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].entrustMargin", body=buy_balance.text)
        logger.info("用户：{0}---接口：{1}---状态：{2}---下单前可用保证金：{3}--委托保证金：{4}".format(self.buyer, sda_account_asset_detail_get_url,buy_balance.status_code, buy_balance_value, buy_entrust_value))

        # 下限价空单委托
        time.sleep(1)
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id,order_type=order_type.空单,order_price_type=order_type.限价,order_price=price,order_num=deal_num
        ))
        buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=buy_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))

        # 撤单
        time.sleep(1)
        cancel_resp = self.session.post(url=base+sda_order_cancel_url, data=get_sda_order_cancel_param(sda_id=sda_id, order_id=buy_order_id, order_type=空单))
        logger.info("撤单接口状态：{0}---返回信息：{1}".format(cancel_resp.status_code, cancel_resp.json()))
        cancel_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=cancel_resp.text)
        cancel_msg = JMESPathExtractor().extract(query="MSG", body=cancel_resp.text)

        # 查询用户余额，然后判断下单前后的用户余额
        time.sleep(1)
        after_buy_balance = self.session.post(url=base+sda_account_asset_detail_get_url, data=get_sda_account_asset_detail_get_param())
        after_buy_balance_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].availableMargin",body=after_buy_balance.text)
        after_buy_entrust_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].entrustMargin", body=after_buy_balance.text)
        logger.info("用户：{0}---接口：{1}---状态：{2}---下单后可用保证金：{3}---下单后委托保证金：{4}".format(self.buyer, sda_account_asset_detail_get_url,after_buy_balance.status_code, after_buy_balance_value, after_buy_entrust_value))

        order_id_flag = assert_list([buy_order_id, 200, "SUCCESS"], [cancel_order_id, cancel_resp.status_code, cancel_msg])
        available_margin_flag = assert_one(int(buy_balance_value), int(after_buy_balance_value))
        entrust_margin_flag = assert_one(int(buy_entrust_value), int(after_buy_entrust_value))
        self.assertListEqual([True, True, True], [available_margin_flag, entrust_margin_flag, order_id_flag])


if __name__ == '__main__':
    unittest.main()