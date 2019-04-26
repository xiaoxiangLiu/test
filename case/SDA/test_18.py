__author__ = '123'
# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import MyTestTwoUser
from common._mytest import assert_one
from common._mytest import MyTestOn
from common.connectMysql import ConnectMysql
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.logger import logger
from common.connectRedis import ConnectRedis
import time

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


class TestCase(MyTestOn):
    """
    平仓测试类
    """
    def tet_01(self):
        """
        正常平仓
        """
        """
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        """

        # 下单前查询两个用户合约账户的余额
        buy_balance = self.session.post(url=base+sda_account_asset_detail_get_url, data=get_sda_account_asset_detail_get_param())
        sell_balance = self.sell_session.post(url=base+sda_account_asset_detail_get_url, data=get_sda_account_asset_detail_get_param())
        buy_balance_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].availableMargin",body=buy_balance.text)
        sell_balance_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].availableMargin", body=sell_balance.text)
        buy_entrust_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].entrustMargin", body=buy_balance.text)
        sell_entrust_value = JMESPathExtractor().extract(query="OBJECT.PNLList[0].entrustMargin", body=sell_balance.text)
        print(buy_entrust_value)
        print(sell_entrust_value)
        print(buy_balance_value)
        print(sell_balance_value)
        logger.info("用户：{0}---接口：{1}---状态：{2}---下单前可用保证金：{3}--委托保证金：{4}".format(self.buyer, sda_account_asset_detail_get_url,buy_balance.status_code, buy_balance_value, buy_entrust_value))
        logger.info("用户：{0}---接口：{1}---状态：{2}---下单前可用保证金：{3}--委托保证金：{4}".format(self.seller, sda_account_asset_detail_get_url, sell_balance.status_code, sell_balance_value, sell_entrust_value))

        # 买家平仓
        """
        buy_ping_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id,order_type=平多,order_price_type=限价,order_price=100000000,order_num=100000000
        ))
        print(buy_ping_resp.status_code)
        print(buy_ping_resp.json())
        """


if __name__ == '__main__':
    unittest.main()
