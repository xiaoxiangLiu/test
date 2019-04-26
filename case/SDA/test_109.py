__author__ = '123'
# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.connectMysql import ConnectMysql
from common._mytest import assert_one
from common.connectRedis import ConnectRedis
from common.logger import logger
from common.names import order_type
from common._mytest import account_info
from common._mytest import account_info_sync
from common._mytest import market_info_get
import time

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
    连续下N个订单，连续撤单，验证订单状态、用户余额
    """
    def test_01(self):
        """
        连续下N个多单，连续撤单，检查委托状态、用户余额
        """
        logger.info("用例编号：109-1---连续下N个多单，连续撤单，检查委托状态、用户余额")
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=99000000000000)

        deal_price = 100000000
        deal_num = 100000000
        lever = 100
        # 下委托前查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]
        cancel_num = None
        sync_id = None
        for i in range(100):
            # 下多单限价
            cancel_num = i
            buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                        order_type=order_type.多单,
                                                                                                        order_price_type=order_type.限价,
                                                                                                        lever=lever,
                                                                                                        order_price=deal_price,
                                                                                                        order_num=deal_num
                                                                                                        ))
            sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
            buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=buy_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
                self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
            ))

            # 撤单
            # time.sleep(1)
            cancel_resp = self.session.post(url=base+sda_order_cancel_url, data=get_sda_order_cancel_param(sda_id=sda_id, order_id=buy_order_id, order_type=多单))
            logger.info("撤单接口状态：{0}---返回信息：{1}".format(cancel_resp.status_code, cancel_resp.json()))
            logger.info("撤单次数：{}".format(i))
            # time.sleep(1)

        # 下委托后查询可用余额
        time.sleep(2)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        logger.info("撤单次数：{}".format(cancel_num))

        available_margin_flag = assert_one(int(before_balance), int(after_balance))
        self.assertTrue(available_margin_flag)

    def test_02(self):
        """
        连续下N个空单，连续撤单，验证订单状态、用户余额
        """
        logger.info("用例编号：109-2---连续下N个空单，连续撤单，验证订单状态、用户余额")
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=990000000000000)

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        price = int(int(now_stock_price) * 0.95)
        deal_num = 100000000
        lever = 50

        # 下委托前查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]
        cancel_num = None
        sync_id = None
        for i in range(100):
            # 下多单限价
            cancel_num = i
            buy_resp = self.session.post(url=base + sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                          order_type=order_type.空单,
                                                                                                          order_price_type=order_type.限价,
                                                                                                          lever=lever,
                                                                                                          order_price=price,
                                                                                                          order_num=deal_num
                                                                                                          ))
            sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
            buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=buy_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
                self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
            ))

            # 撤单
            # time.sleep(1)
            try:
                cancel_resp = self.session.post(url=base + sda_order_cancel_url,
                                                data=get_sda_order_cancel_param(sda_id=sda_id, order_id=buy_order_id,
                                                                                order_type=空单))
                logger.info("撤单接口状态：{0}---返回信息：{1}".format(cancel_resp.status_code, cancel_resp.json()))
                # time.sleep(1)
            except Exception as E:
                logger.info("撤单次数：{0}---失败信息：{1}".format(i, E))

        # 下委托后查询可用余额
        time.sleep(2)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        logger.info("撤单次数：{}".format(cancel_num))

        available_margin_flag = assert_one(int(before_balance), int(after_balance))
        self.assertTrue(available_margin_flag)


if __name__ == '__main__':
    unittest.main()