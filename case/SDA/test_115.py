# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import MyTestTwoUser
from common._mytest import assert_one
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.logger import logger
from common._mytest import market_info_get
from common._mytest import account_info_sync
from common._mytest import query_account_position_get
from common._mytest import assert_list
import time
import ddt

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_create_url = names.sda_order_create_url
sda_order_get_open_url = names.sda_order_get_open_url
sda_order_cancel_url = names.sda_order_cancel_url

sda_get_url = names.sda_get_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan


@ddt.ddt
class TestCase(MyTestTwoUser):
    """
    部分成交杠杆测试类
    """
    @ddt.unpack
    @ddt.data(
        [5, 10],
        [20, 100],
        [50, 50],
        [20, 50],
    )
    def test_01(self, lever, lever_two):
        """
        多单1单，空单1单，多单完全成交，市价空单部分成交，市价单撤回。验证合约状态、用户余额
        """
        logger.info("用例编号：115-1--多单1单，空单1单，多单完全成交，市价空单部分成交，市价单撤回。验证合约状态、用户余额")
        sell_num = 100000000
        buy_num = 200000000

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        deal_price = int(int(now_stock_price) * 0.95)

        # 下一单多单、空单，部分成交
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                    order_type=多单,
                                                                                                    order_price_type=限价,
                                                                                                    lever=lever,
                                                                                                    order_price=deal_price,
                                                                                                    order_num=sell_num
                                                                                                    ))

        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))
        # time.sleep(3)
        sell_resp = self.sell_session.post(url=base+sda_order_create_url,
                                           data=get_sda_order_create_param(sda_id=sda_id, order_type=空单,
                                                                           order_price_type=市价, order_price=deal_price,
                                                                           lever=lever_two, order_num=buy_num))
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
        sell_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=sell_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
            self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
        ))

        # time.sleep(2)
        info_dict = account_info_sync(sync_id=sync_id, user=self.seller, session=self.sell_session, sda_id=sda_id)
        after_sell_balance = info_dict["balance"]

        buy_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id)
        after_buy_balance = buy_info_dict["balance"]

        # 计算保证金
        # buy_currency_balance = make_currency_balance(num=deal_num, price=deal_price)
        # sell_currency_balance = make_currency_balance(num=deal_num, price=deal_price)
        # 检验持仓均价，持仓量，保证金
        sell_flag = assert_one(int(self.sda_balance - sell_num * deal_price / lever_two / 100000000),
                               int(after_sell_balance))
        buy_flag = assert_one(int(self.sda_balance - sell_num * deal_price / lever / 100000000),
                              int(after_buy_balance))
        self.assertListEqual([True, True], [sell_flag, buy_flag])


if __name__ == '__main__':
    unittest.main()