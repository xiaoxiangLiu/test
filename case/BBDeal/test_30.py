__author__ = '123'
# coding=utf-8
from common.run import query_user_balance_value
from common.base import Base
from common.myTest import MyTest
from common.logger import logger
from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
from common.config import GetInit
from common.tools import get_redis_name
from common.count import count_value_sell_first
from common.count import count_value_buy_first
import time, unittest
from common.tools import init_environment

test_data = GetInit().get_test_data(file_name="test_30.yaml")
base_test_data = GetInit().get_test_data(file_name="base.yaml")

base_url, mysql_type, redis_type = init_environment()
buy_price = test_data.get("buy_price")
buy_num = test_data.get("buy_num")
progre_buy_price = test_data.get("progre_buy_price")
progre_buy_num = test_data.get("progre_buy_num")
end_buy_price = test_data.get("end_buy_price")
end_buy_num = test_data.get("end_buy_num")
sell_price = test_data.get("sell_price")
sell_num = test_data.get("sell_num")
progre_sell_price = test_data.get("progre_sell_price")
progre_sell_num = test_data.get("progre_sell_num")
end_sell_price = test_data.get("end_sell_price")
end_sell_num = test_data.get("end_sell_num")


transtion_id = 10
main_currency_id = 5
target_currency_id = 2

BUYER = base_test_data.get("user_39")
SELLER = base_test_data.get("user_41")

class TestCase(MyTest):

    def test_01(self):
        """
        限价卖\限价买：while（余额足够）{A创建卖单，B买入}， 部分成交 手续费 == 2/1000
        B限价买单
        UserB_BuyOrderPrice = 200，250，300，350，400 ,    UserB_BuyOrderNum =  1, 2, 3, 4, 5
        A限价卖单等差递增
        UserA_SellOrderPrice = 200，250，300，350，400 ,   UserA_SellOrderNum = 1, 2, 3, 4, 6
        """

        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id))
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=1)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=1)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER,currency_id=main_currency_id, balance_value=99000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=target_currency_id, balance_value=99000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=SELLER, currency_id=main_currency_id, balance_value=99000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=SELLER, currency_id=target_currency_id, balance_value=99000000000000)
        logger.info("<<==========================================================================================================================>")

        logger.info("测试用例说明：{}".format(TestCase.test_01.__doc__))
        logger.info("买家账号：{0}--------卖家账号：{1}".format(BUYER, SELLER))
        logger.info("-----交易对ID：{0}-----主币ID：{1}-----目标币ID：{2}".format(transtion_id, main_currency_id, target_currency_id))

        before_buy_main, before_buy_target, before_sell_main, before_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )
        buy_order_id_list = []
        sell_order_id_list = []

        for i in range(len(buy_price)):
            # 下买单
            test_buyer = Base(user=BUYER)
            buy_order_id = test_buyer.OrderReservations(transtion_id=transtion_id, price=buy_price[i], num=buy_num[i], order_type=0)
            buy_order_id_list.append(buy_order_id)

        for v in range(len(sell_price)):
            # 下卖单
            test_seller = Base(user=SELLER)
            sell_order_id = test_seller.SellOrder(transtion_id=transtion_id, price=sell_price[v], num=sell_num[v], order_type=0)
            sell_order_id_list.append(sell_order_id)

        time.sleep(6)
        after_buy_main, after_buy_target, after_sell_main, after_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )

        time.sleep(3)

        for t in buy_order_id_list:
            test_buyer = Base(user=BUYER)
            test_buyer.updateRevocationStatus(type=1,orderId=t)

        for k in sell_order_id_list:
            test_seller = Base(user=SELLER)
            test_seller.updateRevocationStatus(type=2,orderId=k)

        buy_order_status_list = []
        sell_order_status_list = []

        for _id in buy_order_id_list:
            buy_order_status = ConnectMysql(_type=mysql_type).get_Order_Status(order_id=_id, order_type=1)
            buy_order_status_list.append(buy_order_status)
        for sell_id in sell_order_id_list:
            sell_order_status = ConnectMysql(_type=mysql_type).get_Order_Status(order_id=sell_id, order_type=2)
            sell_order_status_list.append(sell_order_status)
        logger.info("交易后买单状态：{0}-----交易后卖单状态：{1}".format(buy_order_status_list, sell_order_status_list))

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

        buy_value, deal_num, sell_value, sell_num_value = count_value_buy_first(buy_price, buy_num, sell_price, sell_num)

        self.assertEqual(int(after_buy_main), int(int(before_buy_main) - int(buy_value / 100000000)))
        self.assertEqual(int(after_buy_target), int(before_buy_target) + int(deal_num * (1-2/1000)))
        self.assertEqual(int(after_sell_main), int(before_sell_main) + int(sell_value / 100000000 * (1-2/1000)))
        self.assertEqual(int(after_sell_target), int(before_sell_target) - int(sell_num_value))

    def test_02(self):
        """
        限价卖\限价买：while（余额足够）{A创建卖单，B买入}， 部分成交 手续费 == 2/1000
        A限价卖单等差递增
        UserA_SellOrderPrice = 200，250，300，350，400 ,   UserA_SellOrderNum = 1, 2, 3, 4, 6
        B限价买单
        UserB_BuyOrderPrice = 200，250，300，350，400 ,    UserB_BuyOrderNum =  1, 2, 3, 4, 5
        """

        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id))
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=1)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=1)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER,currency_id=main_currency_id, balance_value=99000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=target_currency_id, balance_value=99000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=SELLER, currency_id=main_currency_id, balance_value=99000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=SELLER, currency_id=target_currency_id, balance_value=99000000000000)
        logger.info("<<==========================================================================================================================>")

        logger.info("测试用例说明：{}".format(TestCase.test_02.__doc__))
        logger.info("买家账号：{0}--------卖家账号：{1}".format(BUYER, SELLER))
        logger.info("-----交易对ID：{0}-----主币ID：{1}-----目标币ID：{2}".format(transtion_id, main_currency_id, target_currency_id))

        before_buy_main, before_buy_target, before_sell_main, before_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )
        buy_order_id_list = []
        sell_order_id_list = []

        for v in range(len(sell_price)):
            # 下卖单
            test_seller = Base(user=SELLER)
            sell_order_id = test_seller.SellOrder(transtion_id=transtion_id, price=sell_price[v], num=sell_num[v], order_type=0)
            sell_order_id_list.append(sell_order_id)

        for i in range(len(buy_price)):
            # 下买单
            test_buyer = Base(user=BUYER)
            buy_order_id = test_buyer.OrderReservations(transtion_id=transtion_id, price=buy_price[i], num=buy_num[i], order_type=0)
            buy_order_id_list.append(buy_order_id)

        time.sleep(6)
        after_buy_main, after_buy_target, after_sell_main, after_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )
        buy_order_status_list = []
        sell_order_status_list = []
        for _id in buy_order_id_list:
            buy_order_status = ConnectMysql(_type=mysql_type).get_Order_Status(order_id=_id, order_type=1)
            buy_order_status_list.append(buy_order_status)
        for sell_id in sell_order_id_list:
            sell_order_status = ConnectMysql(_type=mysql_type).get_Order_Status(order_id=sell_id, order_type=2)
            sell_order_status_list.append(sell_order_status)
        logger.info("交易后买单状态：{0}-----交易后卖单状态：{1}".format(buy_order_status_list, sell_order_status_list))

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

        buy_value, deal_num, sell_value, sell_num_value = count_value_sell_first(buy_price, buy_num, sell_price, sell_num)

        self.assertEqual(int(after_buy_main), int(int(before_buy_main) - int(buy_value/ 100000000)))
        self.assertEqual(int(after_buy_target), int(before_buy_target) + int(deal_num * (1-2/1000)))
        self.assertEqual(int(after_sell_main), int(before_sell_main) + int(sell_value / 100000000 * (1-2/1000)))
        self.assertEqual(int(after_sell_target), int(before_sell_target) - int(sell_num_value))


if __name__ == '__main__':
    unittest.main()
