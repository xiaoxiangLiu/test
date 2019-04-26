__author__ = '123'
# coding=utf-8
from common.jsonparser import JMESPathExtractor
from common.run import query_user_balance_value
from common.base import Base
from common.logger import logger
from common.myTest import MyTest
from common.connectRedis import ConnectRedis
from common.connectMysql import ConnectMysql
from common.config import GetInit
from common.tools import count_balance
from common.tools import get_redis_name
import time

test_data = GetInit().get_test_data(file_name="test_40.yaml")
base_test_data = GetInit().get_test_data(file_name="base.yaml")
mysql_type = base_test_data.get("50_mysql_type")
redis_type = base_test_data.get("50_redis_type")

sell_price = 2000000000
buy_price = 1000000000
sell_num = 3000000000
buy_num = 1000000000

transtion_id = 10
main_currency_id = 5
target_currency_id = 2

BUYER = base_test_data.get("market_user_38")
SELLER = base_test_data.get("market_user_40")


class TestCase(MyTest):

    def test_01(self):
        """
        下买卖单，达不到成交价格，循环撤单，验证余额
        """
        ConnectRedis(_type=redis_type).clear_redis(name=get_redis_name(transtion_id=transtion_id))
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=2)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=2)

        logger.info("<<==========================================================================================================================>")

        logger.info("测试用例说明：".format(TestCase.test_01.__doc__))
        logger.info("买家账号：{0}--------卖家账号：{1}".format(BUYER, SELLER))
        logger.info("-----交易对ID：{0}-----主币ID：{1}-----目标币ID：{2}".format(transtion_id, main_currency_id, target_currency_id))
        # 下单前查询买卖双发的主币和目标币余额
        before_buy_main, before_buy_target, before_sell_main, before_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )

        logger.info("成交之前买家主币余额：{0}-----成交之前买家目标币余额：{1}".format(before_buy_main, before_buy_target))
        logger.info("成交之前卖家的主币余额：{0}------成交之前卖家的目标币余额{1}".format(before_sell_main, before_sell_target))

        logger.info("买入价格：{0}-----买入数量{1}".format(buy_price, buy_num))
        logger.info("卖出价格：{0}-----卖出数量{1}".format(sell_price, sell_num))

        self.buy_id_list = []

        # 下一个买单
        test_buyer = Base(user=BUYER)
        buy_order_id = test_buyer.OrderReservations(transtion_id=transtion_id, price=buy_price, num=buy_num, order_type=0)

        # 下一个卖单
        test_seller = Base(user=SELLER)
        sell_order_id = test_seller.SellOrder(transtion_id=transtion_id, price=sell_price, num=sell_num, order_type=0)
        time.sleep(5)
        for i in range(10):
            test_buyer.updateRevocationStatus(type=1, orderId=buy_order_id)
            time.sleep(5)
            test_seller.updateRevocationStatus(type=2, orderId=sell_order_id)

        after_buy_main, after_buy_target, after_sell_main, after_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )

        balance_dict = {
            "before_buy_main_balance": before_buy_main,
            "before_buy_target_balance": before_buy_target,
            "before_sell_main_balance": before_sell_main,
            "before_sell_target_balance": before_sell_target,
            "after_buy_main_balance": after_buy_main,
            "after_buy_target_balance": after_buy_target,
            "after_sell_main_balance": after_sell_main,
            "after_sell_target_balance": after_sell_target,
        }

        self.assertEqual(int(before_buy_main), int(after_buy_main))
        self.assertEqual(int(before_buy_target), int(after_buy_target))
        self.assertEqual(int(before_sell_main), int(after_sell_main))
        self.assertEqual(int(before_sell_target), int(after_sell_target))


if __name__ == '__main__':
    import unittest
    unittest.main()
