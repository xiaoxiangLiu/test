__author__ = '123'
# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import account_info_sync
from common._mytest import assert_one
from common._mytest import MyTestOn
from common.connectMysql import ConnectMysql
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.logger import logger
from common.connectRedis import ConnectRedis
import time
from common._mytest import account_info

base, mysql_type, redis_type, sda_id = init_environment_213()

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


class TestCase(MyTestOn):
    """
    持仓中，部分限价平仓
    """
    def test_01(self):
        """
        多单持仓中，部分限价平仓，验证持仓余额，平仓委托中状态，用户余额，手续费
        """
        logger.info("用例编号：51-1---多单持仓中，部分平仓，验证持仓余额，平仓委托中状态，用户余额，手续费")
        price = 120*100000000
        buy_num = 50*100000000

        # 平多单
        time.sleep(0.2)
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=平多, order_price_type=限价, order_price=price, order_num=buy_num
        ))
        buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
        logger.info("接口：{0}----返回信息：{1}".format(sda_order_create_url, buy_resp.json()))

        # 53用户下多单。
        # time.sleep(2)
        buy_53_resp = self.session_53.post(url=base+sda_order_create_url,data=get_sda_order_create_param(
            sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=price, order_num=buy_num
        ))
        sync_53_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_53_resp.text)
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, buy_53_resp.json()))

        # time.sleep(3)

        after_53_info_dict = account_info_sync(sync_id=sync_53_id, user=self.user_53, session=self.session_53,
                                               sda_id=sda_id)
        after_53_account_balance = after_53_info_dict["balance"]

        after_info_dict = account_info_sync(sync_id=buy_sync_id, user=self.buyer, session=self.session, sda_id=sda_id)
        after_account_balance = after_info_dict["balance"]

        flag_51 = assert_one(int(after_account_balance), 9999608847984539)
        flag_53 = assert_one(self.sda_balance - int(price * buy_num /100000000), int(after_53_account_balance))
        self.assertListEqual([True, True], [flag_51, flag_53])

    def test_02(self):
        """
        空单持仓中，部分限价平仓，验证持仓余额，平仓委托中状态，用户余额，手续费
        """
        logger.info("用例编号：51-2---空单持仓中，部分平仓，验证持仓余额，平仓委托中状态，用户余额，手续费")
        range_num = 10
        price = 120*100000000
        buy_num = 50*100000000

        # 平多单
        time.sleep(0.5)
        sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=平空, order_price_type=限价, order_price=price, order_num=buy_num
        ))
        sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
        logger.info("接口：{0}----返回信息：{1}".format(sda_order_create_url, sell_resp.json()))

        # 53用户下多单。
        # time.sleep(2)
        buy_53_resp = self.session_53.post(url=base+sda_order_create_url,data=get_sda_order_create_param(
            sda_id=sda_id, order_type=空单, order_price_type=限价, order_price=price, order_num=buy_num
        ))
        sync_53_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_53_resp.text)
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, buy_53_resp.json()))

        # time.sleep(3)

        after_53_info_dict = account_info_sync(sync_id=sync_53_id, user=self.user_53, session=self.session_53,
                                               sda_id=sda_id)
        after_53_account_balance = after_53_info_dict["balance"]

        after_info_dict = account_info_sync(sync_id=sell_sync_id, user=self.seller, session=self.sell_session,
                                            sda_id=sda_id)
        after_account_balance = after_info_dict["balance"]

        flag_51 = assert_one(int(after_account_balance), 9999386552015461)
        flag_53 = assert_one(self.sda_balance - int(price * buy_num / 100000000), int(after_53_account_balance))
        self.assertListEqual([True, True], [flag_51, flag_53])

    def test_03(self):
        """
        多单持仓中，部分限价平仓，验证持仓余额，平仓委托中状态，用户余额，手续费
        :return:
        """
        logger.info("用例编号：51-3---多单持仓中，部分限价平仓，市价多单与平多单成交，验证持仓余额，平仓委托中状态，用户余额，手续费")
        range_num = 10
        price = 120*100000000
        buy_num = 50*100000000

        # 平多单
        time.sleep(0.5)
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=平多, order_price_type=限价, order_price=price, order_num=buy_num
        ))
        buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
        logger.info("接口：{0}----返回信息：{1}".format(sda_order_create_url, buy_resp.json()))

        # 53用户下多单。
        # time.sleep(2)
        buy_53_resp = self.session_53.post(url=base+sda_order_create_url,data=get_sda_order_create_param(
            sda_id=sda_id, order_type=多单, order_price_type=市价, order_price=price, order_num=buy_num
        ))
        sync_53_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_53_resp.text)
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, buy_53_resp.json()))

        # time.sleep(3)

        after_53_info_dict = account_info_sync(sync_id=sync_53_id, user=self.user_53, session=self.session_53,
                                               sda_id=sda_id)
        after_53_account_balance = after_53_info_dict["balance"]

        after_info_dict = account_info_sync(sync_id=buy_sync_id, user=self.buyer, session=self.session, sda_id=sda_id)
        after_account_balance = after_info_dict["balance"]

        flag_51 = assert_one(int(after_account_balance), 9999608847984539)
        flag_53 = assert_one(self.sda_balance - int(price * buy_num / 100000000), int(after_53_account_balance))
        self.assertListEqual([True, True], [flag_51, flag_53])

    def test_04(self):
        """
        空单持仓中，部分限价平仓，验证持仓余额，平仓委托中状态，用户余额，手续费
        :return:
        """
        logger.info("用例编号：51-4---空单持仓中，部分限价平仓，市价空单与平空成交，验证持仓余额，平仓委托中状态，用户余额，手续费")

        range_num = 10
        price = 120*100000000
        buy_num = 50*100000000

        # 平空单
        time.sleep(0.5)
        sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=平空, order_price_type=限价, order_price=price, order_num=buy_num
        ))
        sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
        logger.info("接口：{0}----返回信息：{1}".format(sda_order_create_url, sell_resp.json()))

        # 53用户下多单。
        # time.sleep(2)
        buy_53_resp = self.session_53.post(url=base+sda_order_create_url,data=get_sda_order_create_param(
            sda_id=sda_id, order_type=空单, order_price_type=市价, order_price=price, order_num=buy_num
        ))
        sync_53_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_53_resp.text)
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, buy_53_resp.json()))

        # time.sleep(3)

        after_53_info_dict = account_info_sync(sync_id=sync_53_id, user=self.user_53, session=self.session_53,
                                               sda_id=sda_id)
        after_53_account_balance = after_53_info_dict["balance"]

        after_info_dict = account_info_sync(sync_id=sell_sync_id, user=self.seller, session=self.sell_session,
                                            sda_id=sda_id)
        after_account_balance = after_info_dict["balance"]

        flag_51 = assert_one(int(after_account_balance), 9999386552015461)
        flag_53 = assert_one(self.sda_balance - int(price * buy_num / 100000000), int(after_53_account_balance))
        self.assertListEqual([True, True], [flag_51, flag_53])


if __name__ == '__main__':
    unittest.main()
