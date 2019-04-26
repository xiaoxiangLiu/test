__author__ = '123'
# coding=utf-8
import time
from common.jsonparser import JMESPathExtractor
from common.logger import logger
from common.connectMysql import ConnectMysql
from common.myTest import MyTest
from common.base import Base
from common.config import GetInit



user_buyer_mail = GetInit().GetData("user", "user_buyer_mail")
user_seller_mail = GetInit().GetData("user", "user_seller_mail")

class Run(MyTest):

    """
    <------------------------------------------------------------------------------------------------------------->
    使用的测试基础组件文件,提供
    """
    logger.info("测试类名称：{0}".format(__file__))

    def Run_Order(self, user, transtion_id, order_type=1, price=None, num=None):
        """
        下单后验证余额
        :param user: 接受参数buyer 和 seller，buyer使用38@qq.com，seller使用39@qq.com
        :param transtion_id: 交易对ID
        :param order_type: 订单类型,接受参数1、2、3、4， 1代表限价买单，2代表限价卖单， 3代表市价买单， 4代表市价卖单
        :param price: 单价
        :param num: 数量
        """
        # 根据交易对ID判断币ID
        currency_id = 0
        if transtion_id == 1 or transtion_id == 2 or transtion_id == 6:
            currency_id = 1
        elif transtion_id == 3 or transtion_id == 4 or transtion_id == 7:
            currency_id = 2
        elif transtion_id == 5 or transtion_id == 30:
            currency_id = 3
        else:
            print("您输入的transtion_id暂时没有使用")

        # ------------------------
        # 判断order_type，0 是 限价单， 1 是 市价单
        # buy_type 为1是买单， 为2是卖单
        buy_type = None
        _order_type = 0
        if order_type == 1:
            _order_type = 0
            buy_type = 1
        elif order_type == 2:
            _order_type = 0
            buy_type = 2
        elif order_type == 3:
            _order_type = 1
            buy_type = 1
        elif order_type == 4:
            _order_type = 1
            buy_type = 2

        # --------------------------------------
        # 判断交易对的价格、数量的最小位数
        price_min_num = 0
        num_min_num = 0
        if transtion_id == 1:
            price_min_num, num_min_num = 1000, 100000  # 交易对1价格最小位数5位，数量最小位数3位
        elif transtion_id == 7:
            price_min_num, num_min_num = 10, 100000000
        else:
            print("你输入的交易对没有记录价格和数量的最小位数")

        _price = int(price)
        _num = int(num)
        balance_value = _price * _num
        self.test_buyer = Base(user=user)
        self.before_deal_balance_value = self.test_buyer.User_balance_details(currency_id=currency_id)
        self.order_id = None
        logger.info("使用的交易对为:   {0}".format(transtion_id))
        logger.info("用户邮箱   ：{0}".format(user_buyer_mail))
        time.sleep(0.3)

        # 根据buy_type类型来判断是下买单还是卖单,1是买单，2是卖单
        if buy_type == 1:
            self.resp = self.test_buyer.OrderReservations(transtion_id=transtion_id, price=_price, num=_num, order_type=_order_type)
            assert self.resp.json()["MSG"] == "SUCCESS"
            self.order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=self.resp.text)

            logger.info("买入价格：{0}，买入数量：{1}".format(_price, _num))
            logger.info("下买单:  {0}".format(self.resp.json()))

        elif buy_type == 2:
            self.resp = self.test_buyer.SellOrder(transtion_id=transtion_id, price=_price, num=_num, order_type=_order_type)
            assert self.resp.json()["MSG"] == "SUCCESS"
            self.order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=self.resp.text)
            logger.info("卖出价格：{0}，卖出数量：{1}".format(_price, _num))
            logger.info("下卖单:  {0}".format(self.resp.json()))

        # 下单后余额
        self.after_order_balance_value = self.test_buyer.User_balance_details(currency_id=currency_id)
        logger.info("单价:{0}乘以数量:{1}除以100000000=={2}".format(_price, _num, balance_value/100000000))
        logger.info("下单之前余额:    {0}".format(self.before_deal_balance_value))
        logger.info("下单的ID：{0}".format(self.order_id))
        logger.info("下单之后余额：{0}".format(self.after_order_balance_value))

        self.assertEqual(int(self.before_deal_balance_value) - int(balance_value/100000000), int(self.after_order_balance_value))
        self.test_buyer.close()

    def Run_Transtion_Cancellations(self, user, transtion_id, order_type=1, price=None, num=None):
        """
        下单，撤单后验证余额
        :param user: 接受参数buyer 和 seller， buyer使用38@qq.com， seller使用39@qq.com
        :param transtion_id: 交易对ID
        :param order_type: 订单类型，接受参数1、2、3、4， 1代表限价买单，2代表限价卖单， 3代表市价买单， 4代表市价卖单
        """

        # 根据交易对ID判断币ID
        main_currency_id, target_currency_id = 0, 0

        if transtion_id == 1:
            main_currency_id, target_currency_id = 1, 2
        elif transtion_id == 7:
            main_currency_id, target_currency_id = 2, 6
        elif transtion_id == 4:
            main_currency_id, target_currency_id = 2, 1
        else:
            print("您输入的transtion_id暂时没有使用")

        # ------------------------
        # 判断order_type，0 是 限价单， 1 是 市价单
        # buy_type 为1是买单， 为2是卖单
        buy_type = None
        _order_type = 0
        if order_type == 1:
            _order_type = 0
            buy_type = 1
        elif order_type == 2:
            _order_type = 0
            buy_type = 2
        elif order_type == 3:
            _order_type = 1
            buy_type = 1
        elif order_type == 4:
            _order_type = 1
            buy_type = 2

        # --------------------------------------
        # 判断交易对的价格、数量的最小位数
        price_min_num = 0
        num_min_num = 0
        if transtion_id == 1:
            price_min_num, num_min_num = 1000, 100000  # 交易对1价格最小位数5位，数量最小位数3位
        elif transtion_id == 7:
            price_min_num, num_min_num = 10, 100000000
        else:
            print("你输入的交易对没有记录价格和数量的最小位数")

        _price = int(price)
        _num = int(num)
        balance_value = _price * _num
        self.test_buyer = Base(user=user)
        self.before_deal_main_currency_balance_value = self.test_buyer.User_balance_details(currency_id=main_currency_id)
        self.before_deal_target_currency_balance_value = self.test_buyer.User_balance_details(currency_id=target_currency_id)
        self.order_id = None
        logger.info("使用的交易对为:   {0}".format(transtion_id))
        logger.info("用户邮箱   ：{0}".format(user_buyer_mail))
        time.sleep(0.3)

        # 根据buy_type类型来判断是下买单还是卖单,1是买单，2是卖单
        if buy_type == 1:
            self.resp = self.test_buyer.OrderReservations(transtion_id=transtion_id, price=_price, num=_num, order_type=_order_type)
            self.order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=self.resp.text)
            logger.info("买入价格：{0}，买入数量：{1}".format(_price, _num))
            logger.info("下买单:  {0}".format(self.resp.json()))
            assert self.resp.json()["MSG"] == "SUCCESS"

        elif buy_type == 2:
            self.resp = self.test_buyer.SellOrder(transtion_id=transtion_id, price=_price, num=_num, order_type=_order_type)
            self.order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=self.resp.text)
            logger.info("卖出价格：{0}，卖出数量：{1}".format(_price, _num))
            logger.info("下卖单:  {0}".format(self.resp.json()))
            assert self.resp.json()["MSG"] == "SUCCESS"

        # 撤单
        time.sleep(4)
        self.test_buyer.updateRevocationStatus(type=buy_type, orderId=self.order_id)
        if buy_type == 1:
            order_status = ConnectMysql(_type=2).get_Order_Status(order_id=str(self.order_id), order_type=1)
            logger.info("撤单后买单ID为： {0}-------状态为{1}".format(self.order_id, order_status))
        elif buy_type == 2:
            order_status = ConnectMysql(_type=2).get_Order_Status(order_id=str(self.order_id), order_type=2)
            logger.info("撤单后卖单ID为： {0}-------状态为{1}".format(self.order_id, order_status))

        # 撤单后余额
        self.after_update_main_currency_balance_value = self.test_buyer.User_balance_details(currency_id=main_currency_id)
        self.after_update_target_currency_balance_value = self.test_buyer.User_balance_details(currency_id=target_currency_id)
        logger.info("下单之前主币余额:    {0}".format(self.before_deal_main_currency_balance_value))
        logger.info("下单之前目标币余额:    {0}".format(self.before_deal_target_currency_balance_value))
        logger.info("下单的ID：{0}".format(self.order_id))
        logger.info("撤单后主币余额：{0}".format(self.after_update_main_currency_balance_value))
        logger.info("撤单后目标币余额：{0}".format(self.after_update_target_currency_balance_value))

        self.assertEqual(int(self.before_deal_main_currency_balance_value), int(self.after_update_main_currency_balance_value))
        self.assertEqual(int(self.before_deal_target_currency_balance_value), int(self.after_update_target_currency_balance_value))
        self.test_buyer.close()

    def Run_Deal(self, transtion_id, order_sequence=1, buyer_order_num=1, seller_order_num=1, buyer_order_type=0,
                 seller_order_type=0, buy_price=1, buy_num=1, sell_price=1, sell_num=1):

        """
        验证成交前后余额
        :param transtion_id:交易对ID
        :param order_sequence: 下单顺序，默认为1， 为1则先下买单，为2则先下卖单
        :param buyer_order_num: 买单数量， 默认1单
        :param seller_order_num: 卖单数量， 默认1单
        :param buyer_order_type: 买单类型， 默认0， 0为限价单， 1为市价单
        :param seller_order_type:卖单类型， 默认0， 0为限价单， 1为市价单
        :param sell_price:卖单单价， 默认为1，
        :param sell_num:卖单数量， 默认为1
        :param buy_price:买单单价， 默认为1
        :param buy_num:买单数量， 默认为1
        :return:
        """
        # 根据交易对ID判断币ID
        # main_currency_id 主币ID，交易对中后面的币
        # target_currency_id 副币ID，交易对中前面的币

        main_currency_id, target_currency_id = 0, 0

        if transtion_id == 1:
            main_currency_id, target_currency_id = 1, 2
        elif transtion_id == 7:
            main_currency_id, target_currency_id = 2, 6
        else:
            print("您输入的transtion_id暂时没有使用")
        # ----------------------
        # 买单单价、数量，卖单单价、数量,，卖单卖出总额写入日志
        sell_balance_value = sell_price * sell_num
        logger.info("seller price :{0}   sell num：{1}    sell balance value： {2}".format(sell_price, sell_num, sell_balance_value))
        buy_balance_value = buy_price * buy_num
        logger.info("buyer price: {0}，  buyer num： {1}，    buyer balacne value： {2}".format(buy_price, buy_num, buy_balance_value))

        # 下卖单之前查询seller的主币余额和目标币余额
        self.test_seller = Base(user="seller")
        self.before_seller_order_main_currency_balance_value = self.test_seller.User_balance_details(currency_id=main_currency_id)
        self.before_seller_order_target_currency_balance_value = self.test_seller.User_balance_details(currency_id=target_currency_id)
        # 写入日志
        logger.info("user_id:{0}        币ID为{1}    下单之前余额: {2}".format(user_seller_mail,
                                                                       main_currency_id, self.before_seller_order_main_currency_balance_value))
        logger.info("user_id:{0}        币ID为;{1}   下单之前余额:  {2}".format(user_seller_mail,
                                                                        target_currency_id, self.before_seller_order_target_currency_balance_value))
        self.test_seller.close()

        # 下买单之前查询buyer的主币余额和目标币余额
        self.test_buyer = Base(user="buyer")
        self.before_buyer_order_main_currency_balance_value = self.test_buyer.User_balance_details(currency_id=main_currency_id)
        self.before_buyer_order_target_currency_balance_value = self.test_buyer.User_balance_details(currency_id=target_currency_id)
        # 写入日志
        logger.info("user_id:{0}        币ID为{1}    下单之前余额: {2}".format(user_buyer_mail,
                                                                       main_currency_id, self.before_buyer_order_main_currency_balance_value))
        logger.info("user_id:{0}        币ID为;{1}   下单之前余额:  {2}".format(user_buyer_mail,
                                                                        target_currency_id, self.before_buyer_order_target_currency_balance_value))
        self.test_buyer.close()
        time.sleep(0.3)

        # --------------------------------------------
        # 判断order_sequence 为1则先下买单，为2则先下卖单
        if order_sequence == 1:

            for i in range(buyer_order_num):  # 根据buyer_order_num来判断下几单
                with self.subTest():
                    # 下买单
                    self.test_buyer = Base(user="buyer")
                    self.buyer_resp = self.test_buyer.OrderReservations(transtion_id=transtion_id, price=buy_price, num=buy_num, order_type=buyer_order_type)
                    logger.debug("下买单： {0}".format(self.buyer_resp.json()))
                    self.buyer_resp.close()
                    assert self.buyer_resp.json()["MSG"] == "SUCCESS"

            for k in range(seller_order_num):  # 根据seller_order_num来判断下几单
                with self.subTest():
                    # 下卖单
                    self.test_seller = Base("seller")
                    self.sell_resp = self.test_seller.SellOrder(transtion_id=transtion_id, price=sell_price, num=sell_num, order_type=seller_order_type)
                    logger.debug("下卖单: {0}".format(self.sell_resp.json()))
                    self.sell_resp.close()
                    assert self.sell_resp.json()["MSG"] == "SUCCESS"

        # 判断下单顺序，如果为2则先下卖单再下买单
        elif order_sequence == 2:

            # 根据卖单数量下单
            for i in range(seller_order_num):
                with self.subTest():
                    # 下卖单
                    self.test_seller = Base("seller")
                    self.sell_resp = self.test_seller.SellOrder(transtion_id=transtion_id, price=sell_price, num=sell_num, order_type=seller_order_type)
                    logger.info("下卖单: {0}".format(self.sell_resp.json()))
                    assert self.sell_resp.json()["MSG"] == "SUCCESS"

            # 根据买单数量下单
            for k in range(buyer_order_num):
                with self.subTest():
                    # 下买单
                    self.test_buyer = Base(user="buyer")
                    self.buyer_resp = self.test_buyer.OrderReservations(transtion_id=transtion_id, price=buy_price, num=buy_num, order_type=buyer_order_type)
                    logger.debug("下买单： {0}".format(self.buyer_resp.json()))
                    self.buyer_resp.close()
                    assert self.buyer_resp.json()["MSG"] == "SUCCESS"

        else:
            print("您输入的下单顺序参数不对！")

        # 成交之后查询seller的主币余额和目标币余额
        self.test_seller = Base(user="seller")
        self.after_seller_order_main_currency_balance_value = self.test_seller.User_balance_details(currency_id=main_currency_id)
        self.after_seller_order_target_currency_balance_value = self.test_seller.User_balance_details(currency_id=target_currency_id)
        # 写入日志
        logger.info("user_id:{0}        币ID为{1}    成交之后余额: {2}".format(user_seller_mail,
                                                                       main_currency_id, self.after_seller_order_main_currency_balance_value))
        logger.info("user_id:{0}        币ID为;{1}   成交之后余额:  {2}".format(user_seller_mail,
                                                                        target_currency_id, self.after_seller_order_target_currency_balance_value))
        self.test_seller.close()

        # 成交之后查询buyer的主币余额和目标币余额
        self.test_buyer = Base(user="buyer")
        self.after_buyer_order_main_currency_balance_value = self.test_buyer.User_balance_details(currency_id=main_currency_id)
        self.after_buyer_order_target_currency_balance_value = self.test_buyer.User_balance_details(currency_id=target_currency_id)
        # 写入日志
        logger.info("user_id:{0}        币ID为{1}    成交之后余额: {2}".format(user_buyer_mail,
                                                                       main_currency_id, self.after_buyer_order_main_currency_balance_value))
        logger.info("user_id:{0}        币ID为;{1}   成交之后余额:  {2}".format(user_buyer_mail,
                                                                        target_currency_id, self.after_buyer_order_target_currency_balance_value))
        self.test_buyer.close()

        buy_balacne_value_count = buy_balance_value * buyer_order_num  # 计算下买单的总金额
        sell_balance_value_count = sell_balance_value * seller_order_num  # 计算下卖单总金额
        balance_value_count = 0
        commission_charge = 0  # 手续费初始为０
        if buy_balacne_value_count >= sell_balance_value_count:  # 如果买单总金额大于等于卖单总金额，那么按照买单总金额乘以千分之二计算手续费
            commission_charge = int(buy_balacne_value_count * 2/1000)
            balance_value_count = buy_balacne_value_count
            logger.debug("手续费为： {0}".format(commission_charge))
        elif buy_balacne_value_count <= sell_balance_value_count:  # 如果买单总金额小于等于卖单总金额，那么按照卖单总金额乘以千分之二计算手续费
            commission_charge = int(sell_balance_value_count * 2/1000)
            balance_value_count = sell_balance_value_count
            logger.debug("手续费： {0}".format(commission_charge))

        # -----------------------------------------------------
        # 验证成交之后的Buyer主币余额是否正确，成交之后的主币余额减去成交总金额  VS  成交之前的主币余额
        assert int(self.after_buyer_order_main_currency_balance_value) - balance_value_count == int(self.before_buyer_order_main_currency_balance_value)
        # 验证成交之后的buyer目标币余额是否正确，成交之后的目标币余额减去成交之前的目标币余额  VS  成交总金额减去手续费
        assert int(self.after_buyer_order_target_currency_balance_value) - int(self.before_buyer_order_target_currency_balance_value) == balance_value_count - commission_charge
        # 验证成交之后的Seller主币余额是否正确，成交之后的主币余额减去成交之前的主币余额  VS 成交总金额减去手续费
        assert int(self.after_seller_order_main_currency_balance_value) - int(self.before_seller_order_main_currency_balance_value) == balance_value_count - commission_charge
        # 验证成交之后的Seller目标币余额是否正确，成交之后的目标币金额减去成交总金额  VS 成交之前的目标币余额
        self.assertEqual(int(self.after_seller_order_target_currency_balance_value) - balance_value_count, int(self.before_seller_order_target_currency_balance_value))


if __name__ == '__main__':
    Run().Run_Transtion_Cancellations("buyer", 7, 1, 1000000, 10000000)