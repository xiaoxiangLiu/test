# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import assert_one
from common._mytest import MyTestOnTwo
from common.params import *
from common.logger import logger
import time
from common._mytest import account_info_sync
from common.jsonparser import JMESPathExtractor
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


class TestCase(MyTestOnTwo):
    """
    持仓中，市价部分平仓
    """
    def test_01(self):
        """
        多单持仓中，部分市价平仓，无对应委托成交，自动撤单，验证用户余额、委托状态
        """
        logger.info("用例编号：62-1---多单持仓中，部分市价平仓，无对应委托成交，自动撤单，验证用户余额、委托状态")
        range_num = 10
        price = 20*100000000
        buy_num = 5*100000000

        before_buy_account_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_buy_account_balance = before_buy_account_dict["balance"]

        # 市价平多单
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=平多, order_price_type=市价, order_price=price, order_num=buy_num
        ))
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
        logger.info("接口：{0}----返回信息：{1}".format(sda_order_create_url, buy_resp.json()))
        # time.sleep(2)
        after_buy_account_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session,
                                                   sda_id=sda_id)
        after_buy_account_balance = after_buy_account_dict["balance"]

        flag = assert_one(int(before_buy_account_balance), int(after_buy_account_balance))
        self.assertTrue(flag)

    def test_02(self):
        """
        空单持仓中，部分市价平仓，无对应委托成交，自动撤单，验证用户余额，委托状态
        """
        logger.info("用例编号：62-2---空单持仓中，部分市价平仓，无对应委托成交，自动撤单，验证用户余额，委托状态")
        range_num = 10
        price = 20*100000000
        buy_num = 5*100000000

        before_sell_account_dict = account_info(user=self.seller, session=self.sell_session, sda_id=sda_id)
        before_sell_account_balance = before_sell_account_dict["balance"]

        # 平多单
        sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=平空, order_price_type=市价, order_price=price, order_num=buy_num
        ))
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
        logger.info("接口：{0}----返回信息：{1}".format(sda_order_create_url, sell_resp.json()))
        # time.sleep(2)
        after_info_dict = account_info_sync(sync_id=sync_id, user=self.seller, session=self.sell_session, sda_id=sda_id)
        after_account_balance = after_info_dict["balance"]

        flag = assert_one(int(before_sell_account_balance), int(after_account_balance))
        self.assertTrue(flag)


if __name__ == '__main__':
    unittest.main()
