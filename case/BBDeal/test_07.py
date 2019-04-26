__author__ = '123'
# coding=utf-8
import unittest
import requests
import time
from common.names import names
from common.tools import init_environment
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.connectMysql import ConnectMysql
import random
import warnings

base, mysql_type, redis_type = init_environment()
BUYER = names.user_39
SELLER = names.user_41
限价 = names.xianjiadan
市价 = names.shijiadan
买单 = names.buy_order
卖单 = names.sell_order
login_url = names.login_url
logout_url = names.logout_url
order_reservations_url = names.order_reservations_url
sell_order_url = names.sell_order_url
update_revocation_status_url = names.update_revocation_status_url
get_user_balance_servlet_url = names.get_user_balance_servlet_url

headers = names.login_header
password = names.password

transtion_id = 23
price = 20000
num = 50000000


class TestUserBalanceDetails(unittest.TestCase):

    def setUp(self):
        self.session = requests.session()
        self.sell_session = requests.session()

        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        login_resp = self.session.post(url=base + login_url, data=get_login_param(user=BUYER, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}------登陆状态：{1}".format(SELLER, login_status))

        sell_login_resp = self.sell_session.post(url=base+login_url, data=get_login_param(user=SELLER, user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}------登陆状态：{1}".format(SELLER, sell_login_status))

        self.buy_cookie = self.session.cookies
        self.sell_cookie = self.session.cookies

    def tearDown(self):
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}-------退出状态：{1}".format(SELLER, logout_status))

        self.session.close()
        sell_logout_resp = self.sell_session.post(url=base+logout_url, data=get_user_logout_param())
        sell_logout_status = JMESPathExtractor().extract(query="MSG", body=sell_logout_resp.text)
        logger.info("用户：{0}-------退出状态：{1}".format(SELLER, sell_logout_status))
        self.sell_session.close()

    def test_01(self):
        """
        用户余额为0，下市价买单，随机金额，随机数量验证接口状态、MSG、STATUS
        """
        warnings.simplefilter("ignore", ResourceWarning)
        main_currency_id, target_currency_id = ConnectMysql(_type=mysql_type).query_main_target_currency(transtion_id=transtion_id)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=main_currency_id, balance_value=0)
        num_min, price_min = ConnectMysql(_type=mysql_type).query_currency_min(transtion_id=transtion_id)
        random_price = random.randrange(int(price_min), int(price_min) * 999999, int(price_min))
        random_num = random.randrange(int(num_min), int(num_min) * 999999, int(num_min))
        logger.info("用例编号：7-1---用户余额为0，下市价买单，验证接口状态、MSG、STATUS")
        resp = self.session.post(url=base+order_reservations_url, data=get_order_reservations_param(transtion_id=transtion_id, order_type=市价, price=random_price, num=random_num))
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        logger.info("用户：{0}----URL：{1}-----接口状态：{2}".format(BUYER, order_reservations_url, resp.status_code))
        logger.info("下市价买单返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "下单失败", "1"], [resp.status_code, msg, status])

    def test_02(self):
        """
        准备一个卖单，用户余额为0，下市价买单，随机数量，随机金额，买卖单达到完全成交条件，验证接口状态、MSG、STATUS
        """
        logger.info("用例编号：7-2---用户余额为0，下市价买单，随机金额，随机数量，验证接口状态、MSG、STATUS")

        main_currency_id, target_currency_id = ConnectMysql(_type=mysql_type).query_main_target_currency(transtion_id=transtion_id)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=main_currency_id, balance_value=0)
        num_min, price_min = ConnectMysql(_type=mysql_type).query_currency_min(transtion_id=transtion_id)
        random_price = random.randrange(int(price_min), int(price_min) * 999999, int(price_min))
        random_num = random.randrange(int(num_min), int(num_min) * 999999, int(num_min))

        # 下单前查询余额
        logger.info("成交单价：{0}-------成交数量：{1}".format(random_price, random_num))
        buy_main = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=BUYER, currency_id=main_currency_id))
        buy_main_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=buy_main.text)
        buy_target = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=BUYER, currency_id=target_currency_id))
        buy_target_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=buy_target.text)

        logger.info("用户：{0}----下单前币：{1}--余额：{2}----下单前币：{3}--余额：{4}".format(BUYER, main_currency_id, buy_main_balance, target_currency_id, buy_target_balance))

        sell_main = self.sell_session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=SELLER, currency_id=main_currency_id))
        sell_main_balancee = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=sell_main.text)
        sell_target = self.sell_session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=SELLER, currency_id=target_currency_id))
        sell_target_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=sell_target.text)

        logger.info("用户：{0}-----下单前币：{1}--余额：{2}----下单前币：{3}--余额：{4}".format(SELLER, main_currency_id, sell_main_balancee, target_currency_id, sell_target_balance))

        sell_resp = self.sell_session.post(url=base+sell_order_url, data=get_sell_order_param(transtion_id=transtion_id, order_type=限价, price=random_price, num=random_num))
        sell_order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=sell_resp.text)
        logger.info("用户：{0}-----限价卖单：{1}".format(SELLER, sell_resp.text))
        time.sleep(1)
        buy_resp = self.session.post(url=base+order_reservations_url, data=get_order_reservations_param(transtion_id=transtion_id, order_type=市价, price=random_price, num=random_num))
        logger.info("用户：{0}-----市价买单：{1}".format(BUYER, buy_resp.text))

        after_buy_main = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=BUYER, currency_id=main_currency_id))
        after_buy_main_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_buy_main.text)
        after_buy_target = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=BUYER, currency_id=target_currency_id))
        after_buy_target_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_buy_target.text)

        after_sell_main = self.sell_session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=SELLER, currency_id=main_currency_id))
        after_sell_main_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_sell_main.text)
        after_sell_target = self.sell_session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=SELLER, currency_id=target_currency_id))
        after_sell_target_balance = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_sell_target.text)

        sell_order_status = ConnectMysql(_type=mysql_type).get_Order_Status(order_id=sell_order_id, order_type=2)
        logger.info("完成测试后卖单ID：{0}-----卖单状态：{1}".format(sell_order_id, sell_order_status))

        logger.info("用户：{0}-----下单后币：{1}--余额：{2}---------下单后币：{3}--余额：{4}".format(BUYER, main_currency_id, after_buy_main_balance, target_currency_id, after_buy_target_balance))
        logger.info("用户：{0}-----下单后币：{1}--余额：{2}---------下单后币：{3}--余额：{4}".format(SELLER, main_currency_id, after_sell_main_balance, target_currency_id, after_sell_target_balance))
        time.sleep(3)
        self.sell_session.post(url=base+update_revocation_status_url, data=get_update_revocation_status_param(_type=卖单, order_id=sell_order_id))
        self.assertEqual(0, sell_order_status)
        self.assertEqual(int(buy_main_balance), int(after_buy_main_balance))
        self.assertEqual(int(buy_target_balance), int(after_buy_target_balance))
        self.assertEqual(int(sell_main_balancee), int(after_sell_main_balance))
        self.assertEqual(int(sell_target_balance), int(after_sell_target_balance) + random_num)

if __name__ == '__main__':
    unittest.main()
