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
from common.connectRedis import ConnectRedis
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

                logger.info("编号：82--1--ID：{0}--------循环下限价买单、撤单100次检查用户余额、冻结金额".format(transtion_id))
                buyer = Base(user=BUYER)
                mySetUp(transtion_id=transtion_id, mysql_type=mysql_type,redis_type=redis_type,buyer=BUYER,seller=SELLER,balance_value=balance_value)
                # ConnectRedis(_type=redis_type, db=5).clear_user_freezing_assets(user_id=buyer.user_id)

                warnings.simplefilter("ignore", ResourceWarning)
                before_buy_main_resp, before_buy_target_resp = buyer.query_user_main_target_balance(mysql_type, transtion_id)
                before_buy_main_balance_value = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=before_buy_main_resp.text)
                before_buy_main_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=before_buy_main_resp.text)
                num_min, price_min = ConnectMysql(mysql_type).query_currency_min(transtion_id)
                for k in range(100):
                    time.sleep(3)
                    logger.info("- - -- - -- - - -- - - -- - - - - - - - -- - - - - -- -- - - -- - - - - - -- - - -- - - - - - -- - - -- - -- -")
                    buy_price = random.randrange(int(price_min), int(price_min) * 999999, int(price_min))
                    buy_num = random.randrange(int(num_min), int(num_min) * 999999, int(num_min))

                    buy_order_text = buyer.OrderReservations(transtion_id=transtion_id, price=buy_price, num=buy_num, order_type=限价)
                    buy_order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=buy_order_text.text)
                    try:
                        buy_order_status = ConnectMysql(mysql_type).get_Order_Status(order_id=buy_order_id, order_type=买单)
                        logger.info("买单状态：{}".format(buy_order_status))
                    except Exception as E:
                        logger.info("连接数据库查询订单状态异常：{}".format(E))
                    time.sleep(3)
                    after_buy_main_resp, after_buy_target_resp = buyer.query_user_main_target_balance(mysql_type=mysql_type, transtion_id=transtion_id)
                    after_buy_main_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_buy_main_resp.text)
                    after_buy_main_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets",body=after_buy_main_resp.text)
                    z = '{:.8f}'.format(float(after_buy_main_freezingAssets))
                    k = '{:.8f}'.format(float(before_buy_main_freezingAssets))
                    logger.info("    下买单前用户主币余额：{0}---------    下买单后用户主币余额：{1}".format(before_buy_main_balance_value, after_buy_main_balance))
                    logger.info("下买单前用户主币冻结金额：{0}---------下买单后用户主币冻结金额：{1}".format(k, z))
                    time.sleep(3)
                    buyer.updateRevocationStatus(type=买单, orderId=buy_order_id)

                    # update_buy_order_status = ConnectMysql(mysql_type).get_Order_Status(order_id=buy_order_id, order_type=买单)
                    # logger.info("撤单后订单状态：{}".format(update_buy_order_status))
                    after_update_buy_main_resp, after_update_buy_target_resp = buyer.query_user_main_target_balance(mysql_type=mysql_type, transtion_id=transtion_id)
                    after_update_buy_main_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_update_buy_main_resp.text)
                    after_update_buy_main_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets",body=after_update_buy_main_resp.text)
                    x = '{:.8f}'.format(float(after_update_buy_main_freezingAssets))
                    logger.info("撤单后用户主币金额：{0}------------------撤单后用户主币冻结金额：{1}".format(after_update_buy_main_balance,x))

                after_deal_buy_main_resp, after_deal_buy_resp = buyer.query_user_main_target_balance(mysql_type, transtion_id)
                buyer.close()
                after_buy_main_update_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_deal_buy_main_resp.text)
                after_buy_main_update_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=after_deal_buy_main_resp.text)
                x = '{:.8f}'.format(float(before_buy_main_freezingAssets))

                y = '{:.8f}'.format(float(after_buy_main_update_freezingAssets))

                logger.info("循环下单撤单100次后主币余额：{0}------起始主币余额{1}".format(after_buy_main_update_balance, before_buy_main_balance_value))
                logger.info("循环下单撤单100次后主币冻结金额：{0}--------起始冻结金额{1}".format(y, x))
                self.assertEqual(int(before_buy_main_balance_value), int(after_buy_main_update_balance))


if __name__ == '__main__':
    unittest.main()


