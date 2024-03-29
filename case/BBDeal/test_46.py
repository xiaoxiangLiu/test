__author__ = '123'
# coding=utf-8
from common.base import Base
from common.run import query_user_balance_value
from common.connectRedis import ConnectRedis
from common.connectMysql import ConnectMysql
from common.tools import count_balance
from common.logger import logger
from common.myTest import MyTest
from common.config import GetInit
import ddt
from common.tools import get_redis_name
from common.names import names
from common.tools import init_environment
from common.jsonparser import JMESPathExtractor
import time
base_url, mysql_type, redis_type = init_environment()

BUYER = names.market_user_38
SELLER = names.market_user_40
transtion_4 = GetInit().get_test_data(file_name="transtion_4.yaml")
transtion_11 = GetInit().get_test_data(file_name="transtion_11.yaml")
transtion_12 = GetInit().get_test_data(file_name="transtion_12.yaml")
transtion_10 = GetInit().get_test_data(file_name="transtion_10.yaml")
transtion_24 = GetInit().get_test_data(file_name="transtion_24.yaml")
transtion_25 = GetInit().get_test_data(file_name="transtion_25.yaml")
transtion_37 = GetInit().get_test_data(file_name="transtion_37.yaml")
# transtion_35 = GetInit().get_test_data(file_name="transtion_35.yaml")
transtion_36 = GetInit().get_test_data(file_name="transtion_36.yaml")
# transtion_33 = GetInit().get_test_data(file_name="transtion_33.yaml")
transtion_34 = GetInit().get_test_data(file_name="transtion_34.yaml")
# transtion_31 = GetInit().get_test_data(file_name="transtion_31.yaml")
transtion_32 = GetInit().get_test_data(file_name="transtion_32.yaml")
transtion_29 = GetInit().get_test_data(file_name="transtion_29.yaml")
transtion_30 = GetInit().get_test_data(file_name="transtion_30.yaml")
transtion_44 = GetInit().get_test_data(file_name="transtion_44.yaml")
transtion_45 = GetInit().get_test_data(file_name="transtion_45.yaml")
transtion_46 = GetInit().get_test_data(file_name="transtion_46.yaml")
transtion_47 = GetInit().get_test_data(file_name="transtion_47.yaml")
transtion_38 = GetInit().get_test_data(file_name="transtion_38.yaml")
transtion_39 = GetInit().get_test_data(file_name="transtion_39.yaml")
transtion_9 = GetInit().get_test_data(file_name="transtion_9.yaml")
transtion_56 = GetInit().get_test_data(file_name="transtion_56.yaml")
transtion_61 = GetInit().get_test_data(file_name="transtion_61.yaml")
transtion_60 = GetInit().get_test_data(file_name="transtion_60.yaml")

@ddt.ddt
class TestCase(MyTest):

    @ddt.data(
        transtion_10
    )
    @ddt.unpack
    def test_01(self, number,transtion_id, main_currency_id, target_currency_id, buy_price, buy_num, sell_price, sell_num):
        """
        编号：46-1
        限价买单，不收手续费，限价卖单，不收取手续费
        """
        logger.info("<<==========================================================================================================================>")

        logger.info("用例说明：  编号：46-1-%s，        限价买单，不收手续费，限价卖单，不收取手续费" % number)
        logger.info("买家账号：{0}--------卖家账号：{1}".format(BUYER, SELLER))
        logger.info("-----交易对ID：{0}-----主币ID：{1}-----目标币ID：{2}".format(transtion_id, main_currency_id, target_currency_id))
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=1)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=1)
        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id))

        buy_price, sell_price, buy_num, sell_num = int(buy_price), int(sell_price), int(buy_num), int(sell_num)

        before_buy_main, before_buy_target, before_sell_main, before_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )
        test_buyer = Base(user=BUYER)
        buy_order_id = test_buyer.OrderReservations(transtion_id=transtion_id, price=buy_price, num=buy_num, order_type=0)
        time.sleep(1)
        test_seller = Base(user=SELLER)
        sell_order_id = test_seller.SellOrder(transtion_id=transtion_id, price=sell_price, num=sell_num, order_type=0)
        test_buyer = Base(user=BUYER)
        buy_update_resp = test_buyer.updateRevocationStatus(type=1, orderId=buy_order_id)
        buy_assert_list = [JMESPathExtractor().extract(query="MSG", body=buy_update_resp.text), JMESPathExtractor().extract(query="STATUS", body=buy_update_resp.text)]

        test_seller = Base(user=SELLER)
        sell_update_resp = test_seller.updateRevocationStatus(type=2, orderId=sell_order_id)
        sell_assert_list = [JMESPathExtractor().extract(query="MSG", body=sell_update_resp.text), JMESPathExtractor().extract(query="STATUS", body=sell_update_resp.text)]

        after_buy_main, after_buy_target, after_sell_main, after_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id, transaction_id=transtion_id,
            order_id=sell_order_id
        )

        buy_order_status = ConnectMysql(_type=mysql_type).get_Order_Status(order_id=buy_order_id, order_type=1)
        sell_order_status = ConnectMysql(_type=mysql_type).get_Order_Status(order_id=sell_order_id, order_type=2)
        logger.info("交易后买单状态：{0}-----交易后卖单状态：{1}".format(buy_order_status, sell_order_status))

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
        self.assertListEqual(buy_assert_list, ["订单已被成交", "1"])
        self.assertListEqual(sell_assert_list, ["订单已被成交", "1"])
        flag_list = count_balance(free_type="all_free", deal_price=buy_price, deal_num=buy_num, **balance_dict)

        self.assertNotIn(False, flag_list)

    @ddt.data(
        transtion_10
    )
    @ddt.unpack
    def test_02(self, number,transtion_id, main_currency_id, target_currency_id, buy_price, buy_num, sell_price, sell_num):
        """
        编号：46-2
        限价卖单，不收手续费，限价买单，不收取手续费
        """
        logger.info("<<==========================================================================================================================>")

        logger.info("用例说明：  编号：46-2-%s，        限价卖单，不收手续费，限价买单，不收取手续费" % number)
        logger.info("买家账号：{0}--------卖家账号：{1}".format(BUYER, SELLER))
        logger.info("-----交易对ID：{0}-----主币ID：{1}-----目标币ID：{2}".format(transtion_id, main_currency_id, target_currency_id))
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=1)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=1)
        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id))

        buy_price, sell_price, buy_num, sell_num = int(buy_price), int(sell_price), int(buy_num), int(sell_num)

        before_buy_main, before_buy_target, before_sell_main, before_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )

        test_seller = Base(user=SELLER)
        sell_order_id = test_seller.SellOrder(transtion_id=transtion_id, price=sell_price, num=sell_num, order_type=0)
        time.sleep(1)
        test_buyer = Base(user=BUYER)
        buy_order_id = test_buyer.OrderReservations(transtion_id=transtion_id, price=buy_price, num=buy_num, order_type=0)
        test_buyer = Base(user=BUYER)
        buy_update_resp = test_buyer.updateRevocationStatus(type=1, orderId=buy_order_id)
        buy_assert_list = [JMESPathExtractor().extract(query="MSG", body=buy_update_resp.text), JMESPathExtractor().extract(query="STATUS", body=buy_update_resp.text)]

        test_seller = Base(user=SELLER)
        sell_update_resp = test_seller.updateRevocationStatus(type=2, orderId=sell_order_id)
        sell_assert_list = [JMESPathExtractor().extract(query="MSG", body=sell_update_resp.text), JMESPathExtractor().extract(query="STATUS", body=sell_update_resp.text)]

        after_buy_main, after_buy_target, after_sell_main, after_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id, transaction_id=transtion_id,
            order_id=buy_order_id
        )

        buy_order_status = ConnectMysql(_type=mysql_type).get_Order_Status(order_id=buy_order_id, order_type=1)
        sell_order_status = ConnectMysql(_type=mysql_type).get_Order_Status(order_id=sell_order_id, order_type=2)
        logger.info("交易后买单状态：{0}-----交易后卖单状态：{1}".format(buy_order_status, sell_order_status))

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
        self.assertListEqual(buy_assert_list, ["订单已被成交", "1"])
        self.assertListEqual(sell_assert_list, ["订单已被成交", "1"])
        flag_list = count_balance(free_type="all_free", deal_price=buy_price, deal_num=buy_num, **balance_dict)

        self.assertNotIn(False, flag_list)


if __name__ == '__main__':
    import unittest
    unittest.main()
