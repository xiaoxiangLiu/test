__author__ = '123'
# coding=utf-8
from common.base import Base
from common.myTest import MyTest
from common.logger import logger
from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
from common.jsonparser import JMESPathExtractor
import time, unittest


class TestCase(MyTest):

    def test_01(self):
        """
        限价卖\买：while（余额足够）{A创建卖单，B买入}， 全部成交 手续费 == 2/1000
        交易对：BTC/USDT
        A卖单等差递增
        UserA_SellOrderPrice = 98
        UserA_SellOrderNum = 1,2,3,4,5
        B买单价格
        UserB_BuyOrderPrice = 100
        UserB_BuyOrderNum= 15
        """
        #  清除redis，mysql中btc/usdt的买卖单数据
        ConnectRedis().clear_redis(name=["1buy", "1sell"])
        ConnectMysql().update_order_status(transtion_id=1, order_type=1, order_status=2)
        ConnectMysql().update_order_status(transtion_id=1, order_type=2, order_status=2)

        self.test_buyer = Base(user="buyer")
        self.test_seller = Base(user="seller")

        logger.info("测试用例说明：".format(TestCase.setUp.__doc__))
        # 下单前查询买卖双发的主币和目标币余额
        self.before_deal_seller_main_balance_value = self.test_seller.User_balance_details(currency_id=1)
        self.before_deal_seller_deputy_balance_value = self.test_seller.User_balance_details(currency_id=2)
        self.before_deal_buyer_main_balance_value = self.test_buyer.User_balance_details(currency_id=1)
        self.before_deal_buyer_deputy_balance_value = self.test_buyer.User_balance_details(currency_id=2)

        logger.info("买入之前买家主币余额：{0}-----买入之前买家目标币余额：{1}".format(self.before_deal_buyer_main_balance_value, self.before_deal_buyer_deputy_balance_value))
        logger.info("买入之前卖家的主币余额：{0}------买入之前卖家的目标币余额{1}".format(self.before_deal_seller_main_balance_value, self.before_deal_seller_deputy_balance_value))

        self.buy_price, self.sell_price = 100, 98
        self.buy_num = 15
        self.sell_num = [1, 2, 3, 4, 5]
        self.sell_id_list = []

        for i in range(len(self.sell_num)):
            self.sell_resp = self.test_seller.SellOrder(transtion_id=1, price=self.sell_price, num=self.sell_num[i], order_type=0)
            self.sell_order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=self.sell_resp.text)
            self.sell_id_list.append(self.sell_order_id)
            time.sleep(1)
            logger.info("下卖单返回信息：{0}".format(self.sell_resp.json()))

        self.buy_resp = self.test_buyer.OrderReservations(transtion_id=1, price=self.buy_price, num=self.buy_num, order_type=0)
        buy_order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=self.buy_resp.text)
        logger.info("下买单返回信息：{0}".format(self.buy_resp.json()))

        for i in self.sell_id_list:
            order_status = ConnectMysql().get_Order_Status(order_id=i, order_type=2)
            logger.info("卖单Id：{0}----订单状态：{1}".format(i, order_status))

        logger.info("买单ID：{0}----订单状态：{1}".format(buy_order_id, ConnectMysql().get_Order_Status(order_id=buy_order_id, order_type=1)))

        self.after_deal_seller_main_balance_value = self.test_seller.User_balance_details(currency_id=1)
        self.after_deal_seller_deputy_balance_value = self.test_seller.User_balance_details(currency_id=2)
        self.after_deal_buyer_main_balance_value = self.test_buyer.User_balance_details(currency_id=1)
        self.after_deal_buyer_deputy_balance_value = self.test_buyer.User_balance_details(currency_id=2)

        logger.info("买入之后买家主币余额：{0}-------买入之后买家目标币余额：{1}".format(self.after_deal_buyer_main_balance_value, self.after_deal_buyer_deputy_balance_value))
        logger.info("买入之后卖家主币余额：{0}------买入之后卖家目标币余额：{1}".format(self.after_deal_seller_main_balance_value, self.after_deal_seller_deputy_balance_value))
        logger.info("成交金额：{0}".format(self.buy_num*self.sell_price))

if __name__ == '__main__':
    unittest.main()