__author__ = '123'
# coding=utf-8
from common.base import Base
from common.run import query_user_balance_value
from common.connectRedis import ConnectRedis
from common.connectMysql import ConnectMysql
from common.jsonparser import JMESPathExtractor
from common.logger import logger
from common.myTest import MyTest
from common.config import GetInit
import ddt
from common.tools import get_redis_name
from common.names import names
from common.tools import init_environment
import time
base_url, mysql_type, redis_type = init_environment()

BUYER = names.user_39
SELLER = names.market_user_40
transtion_4 = GetInit().get_test_data(file_name="transtion_4_half.yaml")
transtion_11 = GetInit().get_test_data(file_name="transtion_11_half.yaml")
transtion_12 = GetInit().get_test_data(file_name="transtion_12_half.yaml")
transtion_10 = GetInit().get_test_data(file_name="transtion_10_half.yaml")
transtion_24 = GetInit().get_test_data(file_name="transtion_24_half.yaml")
transtion_25 = GetInit().get_test_data(file_name="transtion_25_half.yaml")
transtion_37 = GetInit().get_test_data(file_name="transtion_37_half.yaml")
# transtion_35 = GetInit().get_test_data(file_name="transtion_35_half.yaml")
transtion_36 = GetInit().get_test_data(file_name="transtion_36_half.yaml")
# transtion_33 = GetInit().get_test_data(file_name="transtion_33_half.yaml")
transtion_34 = GetInit().get_test_data(file_name="transtion_34_half.yaml")
# transtion_31 = GetInit().get_test_data(file_name="transtion_31_half.yaml")
transtion_32 = GetInit().get_test_data(file_name="transtion_32_half.yaml")
transtion_29 = GetInit().get_test_data(file_name="transtion_29_half.yaml")
transtion_30 = GetInit().get_test_data(file_name="transtion_30_half.yaml")
transtion_44 = GetInit().get_test_data(file_name="transtion_44_half.yaml")
transtion_45 = GetInit().get_test_data(file_name="transtion_45_half.yaml")
transtion_46 = GetInit().get_test_data(file_name="transtion_46_half.yaml")
transtion_47 = GetInit().get_test_data(file_name="transtion_47_half.yaml")
transtion_38 = GetInit().get_test_data(file_name="transtion_38_half.yaml")
transtion_39 = GetInit().get_test_data(file_name="transtion_39_half.yaml")
transtion_9 = GetInit().get_test_data(file_name="transtion_9_half.yaml")
transtion_56 = GetInit().get_test_data(file_name="transtion_56_half.yaml")
transtion_61 = GetInit().get_test_data(file_name="transtion_61_half.yaml")
transtion_60 = GetInit().get_test_data(file_name="transtion_60_half.yaml")


@ddt.ddt
class TestCase(MyTest):

    @ddt.data(
        transtion_10
    )
    @ddt.unpack
    def test_01(self, number, transtion_id, main_currency_id, target_currency_id, buy_price, buy_num, sell_price, sell_num):
        """
        编号：57-1
        限价买单，收手续费，限价卖单，不收取手续费，部分成交，
        """
        logger.info("<<==========================================================================================================================>")

        logger.info("用例说明：编号：57-1-%s  限价买单，收手续费，限价卖单，不收取手续费，部分成交，"%number)
        logger.info("买家账号：{0}--------卖家账号：{1}".format(BUYER, SELLER))
        logger.info("-----交易对ID：{0}-----主币ID：{1}-----目标币ID：{2}".format(transtion_id, main_currency_id, target_currency_id))
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=1)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=1)
        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id))
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=main_currency_id, balance_value=990000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=target_currency_id, balance_value=990000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=SELLER, currency_id=main_currency_id, balance_value=990000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=SELLER, currency_id=target_currency_id, balance_value=990000000000000)

        buy_price, sell_price, buy_num, sell_num = int(buy_price), int(sell_price), int(buy_num), int(sell_num)
        logger.info("买入价格：{0}----买入数量：{1}-----卖出价格：{2}-----卖出数量{3}".format(buy_price, buy_num, sell_price, sell_num))
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
        time.sleep(5)
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

        logger.info("交易前买家主币余额：{0}--------交易后买家主币余额：{1}".format(before_buy_main, after_buy_main))
        logger.info("交易前买家目标币余额：{0}--------交易后买家目标币余额：{1}".format(before_buy_target, after_buy_target))
        logger.info("交易前卖家主币余额：{0}--------交易后卖家主币余额：{1}".format(before_sell_main, after_sell_main))
        logger.info("交易前卖家目标币余额：{0}--------交易后卖家目标币余额：{1}".format(before_sell_target, after_sell_target))
        self.assertListEqual(buy_assert_list, ["SUCCESS", "0"])
        self.assertListEqual(sell_assert_list, ["订单已被成交", "1"])
        self.assertIn(int(before_buy_main) - int(after_buy_main) - int(buy_price * sell_num / 100000000), [0, 1])
        self.assertIn(int(after_buy_target) - int(before_buy_target) - int(sell_num * (1-2/1000)), [0, 1])
        self.assertIn(int(after_sell_main) - int(before_sell_main) - int(buy_price * sell_num / 100000000), [0, 1])
        self.assertIn(int(before_sell_target) - int(after_sell_target) - int(sell_num), [0 ,1])

    @ddt.data(
        transtion_10
    )
    @ddt.unpack
    def test_02(self, number, transtion_id, main_currency_id, target_currency_id, buy_price, buy_num, sell_price, sell_num):
        """
        编号： 57-2
        先限价卖单，不收取手续费，限价买单，收手续费，部分成交，
        """
        logger.info("<<==========================================================================================================================>")

        logger.info("用例说明：编号： 57-2-%s   先限价卖单，不收取手续费，限价买单，收手续费，部分成交，"%number)
        logger.info("-----交易对ID：{0}-----主币ID：{1}-----目标币ID：{2}".format(transtion_id, main_currency_id, transtion_id))
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=1)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=1)
        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id))
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=main_currency_id, balance_value=990000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=target_currency_id, balance_value=990000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=SELLER, currency_id=main_currency_id, balance_value=990000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=SELLER, currency_id=target_currency_id, balance_value=990000000000000)

        buy_price, sell_price, buy_num, sell_num = int(buy_price), int(sell_price), int(buy_num), int(sell_num)
        logger.info("买入价格：{0}----买入数量：{1}-----卖出价格：{2}-----卖出数量{3}".format(buy_price, buy_num, sell_price, sell_num))
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
        time.sleep(5)
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

        logger.info("交易前买家主币余额：{0}--------交易后买家主币余额：{1}".format(before_buy_main, after_buy_main))
        logger.info("交易前买家目标币余额：{0}--------交易后买家目标币余额：{1}".format(before_buy_target, after_buy_target))
        logger.info("交易前卖家主币余额：{0}--------交易后卖家主币余额：{1}".format(before_sell_main, after_sell_main))
        logger.info("交易前卖家目标币余额：{0}--------交易后卖家目标币余额：{1}".format(before_sell_target, after_sell_target))

        self.assertListEqual(buy_assert_list, ["SUCCESS", "0"])
        self.assertListEqual(sell_assert_list, ["订单已被成交", "1"])
        self.assertIn(int(before_buy_main) - int(after_buy_main) - int(buy_price * sell_num / 100000000), [0, 1])
        self.assertIn(int(after_buy_target) - int(before_buy_target) - int(sell_num * (1-2/1000)), [0, 1])
        self.assertIn(int(after_sell_main) - int(before_sell_main) - int(buy_price * sell_num / 100000000), [0, 1])
        self.assertIn(int(before_sell_target) - int(after_sell_target) - int(sell_num), [0, 1])

if __name__ == '__main__':
    import unittest
    unittest.main()