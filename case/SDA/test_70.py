__author__ = '123'
# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import assert_one
from common.connectMysql import ConnectMysql
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.logger import logger
from common.connectRedis import ConnectRedis
from common._mytest import query_account_position_get
from common._mytest import account_info
from common._mytest import make_busted_price
from common._mytest import query_order_get_history
from common._mytest import MyTestCrash
from common._mytest import set_stock_price
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

currency_id = 5


class TestCase(MyTestCrash):
    """
    爆仓测试类
    """
    def tet_01(self):
        """
        空单爆仓测试，用户可用保证金为0，调整股价，引发用户爆仓。
        """
        logger.info("用例编号：70-1--空单爆仓测试，用户余额有可用保证金为，调整股价，引发用户爆仓。")

        # set股票价格到爆仓价
        set_stock_price(stock_price=self.crash_price)
        time.sleep(65)
        print(self.crash_price)

    def tet_02(self):
        """
        用户余额10，下单价格1，下单数量1，空单持仓，爆仓，验证历史委托中各项数据。
        """
        logger.info("用例编号：70-2--用户余额10，下单价格1，下单数量1，空单持仓，爆仓，验证历史委托中各项数据。")
        # 更新用户余额全额持仓，清除系统中原来的订单
        balance_value = 1000000000
        price = 100000000
        num = 100000000
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=self.buyer, currency_id=currency_id, balance_value=balance_value)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=self.seller, currency_id=currency_id, balance_value=balance_value)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)

        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=多单, order_price_type=限价, order_price=price, order_num=num
        ))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()))
        buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=buy_resp.text)

        sell_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=空单, order_price_type=限价, order_price=price, order_num=num
        ))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()))
        sell_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=sell_resp.text)

        # 查询多单当前持仓的保证金和账户风险率

        """
        buy_position_dict = query_account_position_get(user=self.buyer, session=self.session)
        buy_currency_balance = buy_position_dict["currencyBalancePosition"]  # 多单持仓的保证金
        buy_hazard_rate = buy_position_dict["sdaHazardRate"]  # 多单持仓的风险率
        """

        # 查询空单当前持仓的保证金和账户风险率
        sell_position_dict = query_account_position_get(user=self.seller, session=self.sell_session)
        sell_currency_balance = sell_position_dict["currencyBalancePosition"]  # 空单持仓的保证金
        sell_hazard_rate = sell_position_dict["sdaHazardRate"]  # 空单持仓的风险率

        # 调整股价到爆仓位
        unit = ConnectMysql(_type=mysql_type).query_sda_unit(sda_id=sda_id)
        busted_price = make_busted_price(price=price, balance_value=balance_value, num=num, unit=unit)

        # 查询历史委托中的orderStatus、委托数量、成交量、委托价格、成交价格。
        sell_history_dict = query_order_get_history(user=self.seller, session=self.sell_session)
        sell_order_status = sell_history_dict["orderStatus"]
        sell_order_quantity = sell_history_dict["orderQuantity"]
        sell_order_quantity_completed = sell_history_dict["orderQuantityCompleted"]
        sell_order_price = sell_history_dict["orderPrice"]
        sell_order_average_price = sell_history_dict["orderAveragePrice"]

        # 查询用户可用余额
        info_dict = account_info(user=self.seller, session=self.sell_session, sda_id=sda_id, price=100000000)
        balance = info_dict["balance"]

        # 验证历史委托中的orderStatus、委托数量、委托价格
        assert_one(sell_order_status, "3")
        assert_one(sell_order_quantity, balance_value)
        assert_one(sell_order_price, price)
        assert_one(balance, "0")


if __name__ == '__main__':
    unittest.main()


