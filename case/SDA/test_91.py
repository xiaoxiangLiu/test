# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import assert_one
from common._mytest import MyTestOnTwo
from common.params import *
from common.logger import logger
from common._mytest import account_info
import time
from common._mytest import account_info_sync
from common.jsonparser import JMESPathExtractor

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
    持仓中，平仓完全成交类
    """
    def test_01(self):
        """
        多单持仓，平仓，53用户下多单与之成交。
        """
        logger.info("用例编号：60-1---多单持仓，限价平仓，53用户下限价多单与之成交，验证持仓数据")
        range_num = 10
        price = 20*100000000
        buy_num = 12*100000000
        first_num = 1*100000000
        add_first_num = 3*100000000
        add_first_price = 18*100000000
        all_price = 20*100000000

        # 平多单
        time.sleep(3)
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=平多, order_price_type=限价, order_price=price, order_num=first_num
        ))
        logger.info("接口：{0}----返回信息：{1}".format(sda_order_create_url, buy_resp.json()))

        # 53用户下多单。
        # time.sleep(1)
        buy_53_resp = self.session_53.post(url=base+sda_order_create_url,data=get_sda_order_create_param(
            sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=price, order_num=first_num
        ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, buy_53_resp.json()))

        # 第一次追仓
        # time.sleep(2)
        first_add_buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=add_first_price, order_num=add_first_num
        ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, first_add_buy_resp.json()))

        time.sleep(0.5)
        # 54用户下空单
        resp_54 = self.session_54.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=空单, order_price_type=限价, order_price=add_first_price, order_num=add_first_num
        ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, resp_54.json()))

        time.sleep(1)

        # 限价全平
        second_buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=平多, order_price_type=限价, order_price=all_price, order_num=buy_num
        ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, second_buy_resp.json()))

        # 53用户下单成交

        second_sell_resp = self.session_53.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=all_price, order_num=buy_num
        ))
        second_sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=second_sell_resp.text)
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, second_sell_resp.json()))
        # time.sleep(3)
        after_53_info_dict = account_info_sync(sync_id=second_sell_sync_id, user=self.user_53, session=self.session_53,
                                               sda_id=sda_id)
        after_53_account_balance = after_53_info_dict["balance"]

        after_info_dict = account_info_sync(sync_id=second_sell_sync_id, user=self.buyer, session=self.session,
                                            sda_id=sda_id)
        after_account_balance = after_info_dict["balance"]

        flag_51 = assert_one(int(after_account_balance), 10000002429755492)
        self.assertTrue(flag_51)

    def test_02(self):
        """
        空单持仓，平空与空单成交
        """
        logger.info("用例编号：60-2---空单持仓，平空与空单成交")
        range_num = 10
        price = 20*100000000
        buy_num = 12*100000000
        first_num = 1*100000000
        add_first_num = 3*100000000
        add_first_price = 18*100000000
        all_price = 20*100000000
        # 平空单
        time.sleep(1)
        sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=平空, order_price_type=限价, order_price=price, order_num=first_num
        ))
        logger.info("接口：{0}----返回信息：{1}".format(sda_order_create_url, sell_resp.json()))

        # 53用户下空单。
        # time.sleep(1)
        buy_53_resp = self.session_53.post(url=base+sda_order_create_url,data=get_sda_order_create_param(
            sda_id=sda_id, order_type=空单, order_price_type=限价, order_price=price, order_num=first_num
        ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, buy_53_resp.json()))

        # 第一次追仓
        # time.sleep(2)
        first_add_sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=空单, order_price_type=限价, order_price=add_first_price, order_num=add_first_num
        ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, first_add_sell_resp.json()))

        # time.sleep(1)
        # 54用户下空单
        resp_54 = self.session_54.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=add_first_price, order_num=add_first_num
        ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, resp_54.json()))

        time.sleep(1)

        # 限价全平
        second_sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=平空, order_price_type=限价, order_price=all_price, order_num=buy_num
        ))
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, second_sell_resp.json()))

        # 53用户下单成交

        second_sell_resp = self.session_53.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=空单, order_price_type=限价, order_price=all_price, order_num=buy_num
        ))
        second_sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=second_sell_resp.text)
        logger.info("接口：{0}---返回信息：{1}".format(sda_order_create_url, second_sell_resp.json()))
        # time.sleep(3)
        after_53_info_dict = account_info_sync(sync_id=second_sell_sync_id, user=self.user_53, session=self.session_53,
                                               sda_id=sda_id)
        after_53_account_balance = after_53_info_dict["balance"]

        after_info_dict = account_info_sync(sync_id=second_sell_sync_id, user=self.seller, session=self.sell_session,
                                            sda_id=sda_id)
        after_account_balance = after_info_dict["balance"]

        flag_51 = assert_one(int(after_account_balance), 9999997172644508)
        self.assertTrue(flag_51)


if __name__ == '__main__':
    unittest.main()