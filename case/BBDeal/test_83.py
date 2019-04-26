__author__ = '123'
# coding=utf-8
import unittest
import random
from common.tools import mySetUp
from common.base_ import Base
from common.names import names
from common.tools import init_environment
from common.connectMysql import ConnectMysql
from common.logger import logger
from common.myTest import MyTest
from common.jsonparser import JMESPathExtractor
import warnings
import ddt
import time

base, mysql_type, redis_type = init_environment()
BUYER = names.user_39
SELLER = names.user_41
限价 = names.xianjiadan
市价 = names.shijiadan
买单 = names.buy_order
卖单 = names.sell_order
transtion_id_list = names.transtion_id
balance_value = names.balance_value


@ddt.ddt
class TestCase(MyTest):

    @ddt.data(
        10
    )
    def test_01(self, transtion_id):
        """
        循环100次下限价买单，撤单，检验撤单后余额、冻结金额
        """
        for i in range(1):
            with self.subTest():
                logger.info("<<==========================================================================================================================>")

                logger.info("编号：83--1--ID：{0}--------循环下限价买单、撤单100次检查用户余额".format(transtion_id))
                buyer = Base(user=BUYER)
                mySetUp(transtion_id=transtion_id, mysql_type=mysql_type,redis_type=redis_type,buyer=BUYER,seller=SELLER,balance_value=balance_value)
                warnings.simplefilter("ignore", ResourceWarning)
                before_buy_main_resp, before_buy_target_resp = buyer.query_user_main_target_balance(mysql_type, transtion_id)
                before_buy_main_balance_value = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=before_buy_main_resp.text)
                before_buy_main_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=before_buy_main_resp.text)
                num_min, price_min = ConnectMysql(mysql_type).query_currency_min(transtion_id)
                for k in range(20):
                    time.sleep(5)
                    logger.info("- - -- - -- - - -- - - -- - - - - - - - -- - - - - -- -- - - -- - - - - - -- - - -- - - - - - -- - - -- - -- -")
                    buy_price = random.randrange(int(price_min), int(price_min) * 999999, int(price_min))
                    buy_num = random.randrange(int(num_min), int(num_min) * 999999, int(num_min))

                    buy_order_text = buyer.OrderReservations(transtion_id=transtion_id, price=buy_price, num=buy_num, order_type=限价)
                    buy_order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=buy_order_text.text)
                    buy_order_status = ConnectMysql(mysql_type).get_Order_Status(order_id=buy_order_id, order_type=买单)

                    logger.info("买单状态：{}".format(buy_order_status))
                    time.sleep(5)
                    buyer.updateRevocationStatus(type=买单, orderId=buy_order_id)

                    update_buy_order_status = ConnectMysql(mysql_type).get_Order_Status(order_id=buy_order_id, order_type=买单)
                    logger.info("撤单后订单状态：{}".format(update_buy_order_status))

                after_buy_main_update_resp, after_buy_update_resp = buyer.query_user_main_target_balance(mysql_type, transtion_id)
                buyer.close()
                after_buy_main_update_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_buy_main_update_resp.text)
                after_buy_main_update_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=after_buy_main_update_resp.text)
                x = '{:.8f}'.format(float(before_buy_main_freezingAssets))
                y = '{:.8f}'.format(float(after_buy_main_update_freezingAssets))
                logger.info("循环下单撤单100次后主币余额：{0}------起始主币余额{1}".format(after_buy_main_update_balance, before_buy_main_balance_value))
                logger.info("循环下单撤单100次后主币冻结金额：{0}--------起始冻结金额{1}".format(y, x))
                self.assertEqual(int(before_buy_main_balance_value), int(after_buy_main_update_balance))

    @ddt.data(
        10
    )
    def test_02(self, transtion_id):
        """
        循环100次下限价卖单，撤单，检验撤单后余额、冻结金额
        """
        for i in range(1):
            with self.subTest():
                logger.info("<<==========================================================================================================================>")

                logger.info("编号：83--2--ID：{0}--------循环下限价卖单、撤单100次检查用户余额".format(transtion_id))
                seller = Base(user=SELLER)
                mySetUp(transtion_id=transtion_id, mysql_type=mysql_type,redis_type=redis_type,buyer=BUYER,seller=SELLER,balance_value=balance_value)
                warnings.simplefilter("ignore", ResourceWarning)
                before_sell_main_resp, before_sell_target_resp = seller.query_user_main_target_balance(mysql_type, transtion_id)
                before_sell_target_balance_value = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=before_sell_target_resp.text)
                before_sell_target_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=before_sell_target_resp.text)
                num_min, price_min = ConnectMysql(mysql_type).query_currency_min(transtion_id)
                for k in range(20):
                    time.sleep(5)
                    logger.info("- - -- - -- - - -- - - -- - - - - - - - -- - - - - -- -- - - -- - - - - - -- - - -- - - - - - -- - - -- - -- -")
                    sell_price = random.randrange(int(price_min), int(price_min) * 999999, int(price_min))
                    sell_num = random.randrange(int(num_min), int(num_min) * 999999, int(num_min))

                    sell_order_text = seller.SellOrder(transtion_id=transtion_id, price=sell_price, num=sell_num, order_type=限价)
                    sell_order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=sell_order_text.text)
                    sell_order_status = ConnectMysql(mysql_type).get_Order_Status(order_id=sell_order_id, order_type=卖单)

                    logger.info("买单状态：{}".format(sell_order_status))
                    time.sleep(5)
                    seller.updateRevocationStatus(type=卖单, orderId=sell_order_id)

                    update_sell_order_status = ConnectMysql(mysql_type).get_Order_Status(order_id=sell_order_id, order_type=卖单)
                    logger.info("撤单后订单状态：{}".format(update_sell_order_status))

                after_sell_main_update_resp, after_sell_update_resp = seller.query_user_main_target_balance(mysql_type, transtion_id)
                seller.close()
                after_sell_target_update_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_sell_update_resp.text)
                after_sell_target_update_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=after_sell_update_resp.text)
                x = '{:.8f}'.format(float(before_sell_target_freezingAssets))
                y = '{:.8f}'.format(float(after_sell_target_update_freezingAssets))
                logger.info("循环下单撤单100次后目标币余额：{0}------起始目标币余额{1}".format(after_sell_target_update_balance, before_sell_target_balance_value))
                logger.info("循环下单撤单100次后目标币冻结金额：{0}--------起始目标币冻结金额{1}".format(y, x))
                self.assertEqual(int(before_sell_target_balance_value), int(after_sell_target_update_balance))

    @ddt.data(
        10
    )
    def test_03(self, transtion_id):
        """
        循环100次下市价买单，检验撤单后余额、冻结金额
        """
        for i in range(1):
            with self.subTest():
                logger.info("<<==========================================================================================================================>")

                logger.info("编号：83--3--ID：{0}--------循环下限价买单、撤单100次检查用户余额".format(transtion_id))
                buyer = Base(user=BUYER)
                mySetUp(transtion_id=transtion_id, mysql_type=mysql_type,redis_type=redis_type,buyer=BUYER,seller=SELLER,balance_value=balance_value)
                warnings.simplefilter("ignore", ResourceWarning)
                before_buy_main_resp, before_buy_target_resp = buyer.query_user_main_target_balance(mysql_type, transtion_id)
                before_buy_main_balance_value = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=before_buy_main_resp.text)
                before_buy_main_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=before_buy_main_resp.text)
                num_min, price_min = ConnectMysql(mysql_type).query_currency_min(transtion_id)
                for k in range(50):
                    time.sleep(5)
                    logger.info("- - -- - -- - - -- - - -- - - - - - - - -- - - - - -- -- - - -- - - - - - -- - - -- - - - - - -- - - -- - -- -")
                    buy_price = random.randrange(int(price_min), int(price_min) * 999999, int(price_min))
                    buy_num = random.randrange(int(num_min), int(num_min) * 999999, int(num_min))

                    buy_order_text = buyer.OrderReservations(transtion_id=transtion_id, price=buy_price, num=buy_num, order_type=市价)
                    buy_order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=buy_order_text.text)
                    buy_order_status = ConnectMysql(mysql_type).get_Order_Status(order_id=buy_order_id, order_type=买单)
                    logger.info("买单状态：{}".format(buy_order_status))
                    time.sleep(5)
                after_buy_main_update_resp, after_buy_update_resp = buyer.query_user_main_target_balance(mysql_type, transtion_id)
                buyer.close()
                after_buy_main_update_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_buy_main_update_resp.text)
                after_buy_main_update_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=after_buy_main_update_resp.text)
                x = '{:.8f}'.format(float(before_buy_main_freezingAssets))
                y = '{:.8f}'.format(float(after_buy_main_update_freezingAssets))
                logger.info("循环下单撤单100次后主币余额：{0}------起始主币余额{1}".format(after_buy_main_update_balance, before_buy_main_balance_value))
                logger.info("循环下单撤单100次后主币冻结金额：{0}--------起始冻结金额{1}".format(y, x))
                self.assertEqual(int(before_buy_main_balance_value), int(after_buy_main_update_balance))


if __name__ == '__main__':
    unittest.main()
