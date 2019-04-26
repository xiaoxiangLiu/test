__author__ = '123'
# coding=utf-8
import unittest
import time
from common.tools import init_environment_213
from common.names import names
from common._mytest import MyTestOn
from common.logger import logger
from common._mytest import market_info_get
from common._mytest import assert_one
from common.jsonparser import JMESPathExtractor
from common.params import *
from common._mytest import account_info_sync
from common._mytest import account_info


base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_create_url = names.sda_order_create_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan

sda_order_cancel_url = names.sda_order_cancel_url


class TestCase(MyTestOn):
    """
    持仓成功状态，继续下委托。
    """
    def test_01(self):
        """
        限价多单持仓成功，下限价多单委托，验证余额，委托状态
        """
        logger.info("用例编号：32-1---多单持仓成功，下限价多单委托，下限价空单成交，验证余额，委托状态")
        range_num = 10
        price = 100000000
        buy_num = 100000000
        sell_num = buy_num * range_num

        # 下委托前查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        for i in range(range_num):
            # 下限价委托
            buy_order_resp = self.session.post(url=base+sda_order_create_url,
                                               data=get_sda_order_create_param(sda_id=sda_id,
                                                                               order_type=多单,
                                                                               order_price_type=限价,
                                                                               order_price=price,
                                                                               order_num=buy_num,))
            # time.sleep(0.1)
            logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, buy_order_resp.json()))

        sell_order_resp = self.session_54.post(url=base+sda_order_create_url,
                                               data=get_sda_order_create_param(sda_id=sda_id, order_type=空单,
                                                                               order_price_type=限价,
                                                                               order_price=price,
                                                                               order_num=sell_num))
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_order_resp.text)
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, sell_order_resp.json()))

        # 下委托后查询可用余额
        # time.sleep(2)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        flag = assert_one(int(before_balance), int(after_balance) + sell_num)
        self.assertTrue(flag)

    def test_02(self):
        """
        限价空单持仓成功，下空单委托
        """
        logger.info("用例编号：32-2---空单持仓成功，下限价空单委托，下限价多单成交，验证余额，委托状态")
        range_num = 10
        sell_num = 100000000
        buy_num = sell_num * range_num

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        price = int(int(now_stock_price) * 0.95)

        # 下委托前查询可用余额
        info_dict = account_info(user=self.seller, session=self.sell_session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下空单委托
        for i in range(range_num):

            sell_order_resp = self.sell_session.post(url=base+sda_order_create_url,
                                                     data=get_sda_order_create_param(sda_id=sda_id, order_type=空单,
                                                                                     order_price_type=限价,
                                                                                     order_price=price,
                                                                                     order_num=sell_num))
            # time.sleep(0.1)
            logger.info("接口：{0}----返回信息：{1}".format(sda_order_create_url, sell_order_resp.json()))

        buy_order_resp = self.session_53.post(url=base+sda_order_create_url,
                                              data=get_sda_order_create_param(sda_id=sda_id,
                                                                              order_type=多单,
                                                                              order_price_type=限价,
                                                                              order_price=price,
                                                                              order_num=buy_num))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, buy_order_resp.json()))
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_order_resp.text)

        # 下委托后查询可用余额
        # time.sleep(1)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.seller, session=self.sell_session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        flag = assert_one(int(before_balance), int(after_balance) + buy_num * price / 100000000)
        self.assertTrue(flag)

    def test_03(self):
        """
        限价多单持仓成功，下限价多单委托，验证余额，委托状态
        """
        logger.info("用例编号：32-3---限价多单持仓成功，下限价多单委托，下市价空单成交，验证余额，委托状态")
        range_num = 10
        price = 100000000
        buy_num = 100000000
        sell_num = buy_num * range_num

        # 下委托前查询可用余额
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        for i in range(range_num):
            # 下限价委托
            buy_order_resp = self.session.post(url=base+sda_order_create_url,
                                               data=get_sda_order_create_param(sda_id=sda_id,
                                                                               order_type=多单,
                                                                               order_price_type=限价,
                                                                               order_price=price,
                                                                               order_num=buy_num,))
            # time.sleep(0.1)
            logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, buy_order_resp.json()))

        sell_order_resp = self.session_54.post(url=base+sda_order_create_url,
                                               data=get_sda_order_create_param(sda_id=sda_id,
                                                                               order_type=空单,
                                                                               order_price_type=市价,
                                                                               order_price=price,
                                                                               order_num=sell_num))
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_order_resp.text)
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, sell_order_resp.json()))

        # 下委托后查询可用余额
        # time.sleep(2)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        flag = assert_one(int(before_balance), int(after_balance) + sell_num)
        self.assertTrue(flag)

    def test_04(self):
        """
        限价空单持仓成功，下空单委托
        """
        logger.info("用例编号：32-4---空单持仓成功，下限价空单委托，下限价多单成交，验证余额，委托状态")
        range_num = 10
        sell_num = 100000000
        buy_num = sell_num * range_num

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        price = int(int(now_stock_price) * 0.95)

        # 下委托前查询可用余额
        info_dict = account_info(user=self.seller, session=self.sell_session, sda_id=sda_id, price=1000000000)
        before_balance = info_dict["balance"]

        # 下空单委托
        for i in range(range_num):

            sell_order_resp = self.sell_session.post(url=base+sda_order_create_url,
                                                     data=get_sda_order_create_param(sda_id=sda_id,
                                                                                     order_type=空单,
                                                                                     order_price_type=限价,
                                                                                     order_price=price,
                                                                                     order_num=sell_num))
            # time.sleep(0.1)
            logger.info("接口：{0}----返回信息：{1}".format(sda_order_create_url, sell_order_resp.json()))

        buy_order_resp = self.session_53.post(url=base+sda_order_create_url,
                                              data=get_sda_order_create_param(sda_id=sda_id,
                                                                              order_type=多单,
                                                                              order_price_type=市价,
                                                                              order_price=price,
                                                                              order_num=buy_num))
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_order_resp.text)
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, buy_order_resp.json()))

        # 下委托后查询可用余额
        # time.sleep(2)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.seller, session=self.sell_session, sda_id=sda_id,
                                            price=1000000000)
        after_balance = after_info_dict["balance"]

        flag = assert_one(int(before_balance), int(after_balance) + buy_num * price / 100000000)
        self.assertTrue(flag)


if __name__ == '__main__':
    unittest.main()