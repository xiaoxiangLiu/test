import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import query_account_position_get
from common.AccountTest.AccountUtil import positions_value
from common.AccountTest.AccountUtil import open_positions_value
from common._mytest import assert_list
from common._mytest import MyTestOn
from common._mytest import set_stock_price
from common._mytest import assert_one
from common.params import *
from common.logger import logger
from common._mytest import market_info_get
from common.jsonparser import JMESPathExtractor
from common._mytest import account_info_sync
import time

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_create_url = names.sda_order_create_url
sda_order_get_open_url = names.sda_order_get_open_url
sda_order_cancel_url = names.sda_order_cancel_url
positions_url = names.sda_account_positions_get_url

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
    验证持仓价值测试类
    """

    def test_01(self):
        """
        持仓后验证持仓价值是否返回
        :return:
        """
        logger.info("用例编号：202-1，验证持仓价值和开仓价值计算")
        market_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        print("now stock price", market_dict["stockPrice"])
        print("tradeUnit", market_dict["tradeUnit"])

        positions_dict = query_account_position_get(user=self.buyer, session=self.session, sync_key=self.sync_key)
        # print(positions_dict)
        print("sdaValuation", positions_dict["sdaValuation"])
        print("sdaOpeningValuation", positions_dict["sdaOpeningValuation"])

        buy_open_positions_value = open_positions_value(hold_price=self.deal_price, hold_num=self.deal_num,
                                                        trade_unit=int(market_dict["tradeUnit"]))
        print("buy_open_positions_value", buy_open_positions_value)
        buy_positions_value = positions_value(stock_price=int(market_dict["stockPrice"]), hold_num=self.deal_num,
                                              trade_unit=int(market_dict["tradeUnit"]))
        print("buy_positions_value", buy_positions_value)
        flag = assert_list([int(positions_dict["sdaValuation"]), int(positions_dict["sdaOpeningValuation"])],
                    [int(buy_positions_value), int(buy_open_positions_value)])

        self.assertEqual(flag, True)

    def test_02(self):
        """
        验证股价波动后持仓价值变化
        :return:
        """
        logger.info("用例编号：202-2，验证股价波动后持仓价值变化")
        # 修改股价并重新计算用户持仓价值
        after_stock_price = 22
        set_stock_price(stock_price=after_stock_price)
        market_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        print("now stock price", market_dict["stockPrice"])
        print("tradeUnit", market_dict["tradeUnit"])

        positions_dict = query_account_position_get(user=self.buyer, session=self.session, sync_key=self.sync_key)
        # print(positions_dict)
        print("sdaValuation", positions_dict["sdaValuation"])
        print("sdaOpeningValuation", positions_dict["sdaOpeningValuation"])
        before_positions_value = positions_dict["sdaValuation"]

        # 股价波动
        after_stock_price = 22
        set_stock_price(stock_price=after_stock_price)

        # 股价波动后查询用户持仓价值
        time.sleep(2)
        after_positions_dict = query_account_position_get(user=self.buyer, session=self.session, sync_key=self.sync_key)
        print("sdaValuation", after_positions_dict["sdaValuation"])
        print("sdaOpeningValuation", after_positions_dict["sdaOpeningValuation"])

        after_positions_value = positions_value(stock_price=after_stock_price * 100000000, hold_num=self.deal_num,
                                                trade_unit=int(market_dict["tradeUnit"]))
        after_open_positions_value = open_positions_value(hold_price=self.deal_price, hold_num=self.deal_num,
                                                          trade_unit=int(market_dict["tradeUnit"]))
        positions_flag = assert_one(int(after_positions_value), int(after_positions_dict["sdaValuation"]))
        open_positions_value_flag = assert_one(int(after_open_positions_value),
                                               int(after_positions_dict["sdaOpeningValuation"]))
        self.assertListEqual([True, True], [positions_flag, open_positions_value_flag])


if __name__ == '__main__':
    unittest.main()
