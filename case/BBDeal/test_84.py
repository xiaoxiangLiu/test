__author__ = '123'
# coding=utf-8
import unittest
import requests
import time
import ddt
import random
import re
import warnings
from common.connectMysql import ConnectMysql
from common.names import names
from common.tools import init_environment
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.tools import transform_freezing_assets
from common.connectRedis import ConnectRedis

base, mysql_type, redis_type = init_environment()
BUYER = names.user_39
SELLER = names.user_41
限价 = names.xianjiadan
市价 = names.shijiadan
买单 = names.buy_order
卖单 = names.sell_order
login_url = names.login_url
logout_url = names.logout_url
sell_order_url = names.sell_order_url
order_reservations_url = names.order_reservations_url
update_revocation_status_url = names.update_revocation_status_url
get_user_balance_servlet_url = names.get_user_balance_servlet_url
headers = names.login_header
password = names.password


@ddt.ddt
class TestCase(unittest.TestCase):
    """
    检验冻结金额。
    """

    def setUp(self):
        self.session = requests.session()
        self.sell_session = requests.session()

        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        login_resp = self.session.post(url=base + login_url, data=get_login_param(user=BUYER, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}------登陆状态：{1}".format(BUYER, login_status))

        sell_login_resp = self.sell_session.post(url=base+login_url, data=get_login_param(user=SELLER, user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}------登陆状态：{1}".format(SELLER, sell_login_status))
        self.buy_user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)
        self.sell_user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=sell_login_resp.text)
        self.buy_cookie = self.session.cookies
        self.sell_cookie = self.session.cookies

    def tearDown(self):
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}-------退出状态：{1}".format(BUYER, logout_status))

        self.session.close()
        sell_logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        sell_logout_status = JMESPathExtractor().extract(query="MSG", body=sell_logout_resp.text)
        logger.info("用户：{0}-------退出状态：{1}".format(SELLER, sell_logout_status))
        self.sell_session.close()

    @ddt.data(
        10
    )
    def test_01(self, transtion_id):
        """
        先下限价买单，再下限价卖单，部分成交，检验冻结余额
        """
        logger.info("用例编号：84-1--%s----先下限价买单，再下限价卖单，部分成交，检验冻结余额" % transtion_id)
        main_currency_id, target_currency_id = ConnectMysql(_type=mysql_type).query_main_target_currency(transtion_id=transtion_id)

        ConnectRedis(_type=redis_type).clear_user_freezing_assets(user_id=self.buy_user_id, currency_id=main_currency_id)
        ConnectRedis(_type=redis_type).clear_user_freezing_assets(user_id=self.sell_user_id, currency_id=target_currency_id)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=买单, order_status=1)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=卖单, order_status=1)
        time.sleep(0.1)
        num_min, price_min = ConnectMysql(_type=mysql_type).query_currency_min(transtion_id=transtion_id)

        random_num = random.randrange(int(num_min), int(num_min) * 9999999, int(num_min))
        random_price = random.randrange(int(price_min), int(price_min) * 9999999, int(price_min))
        sell_random_num = random.randrange(int(num_min), int(num_min) * 9999999, int(num_min))

        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=main_currency_id, balance_value=9900000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=target_currency_id, balance_value=9900000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=SELLER, currency_id=main_currency_id, balance_value=9900000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=SELLER, currency_id=target_currency_id, balance_value=9900000000000000)

        logger.info("交易对：{0}-------主币：{1}-----目标币：{2}".format(transtion_id, main_currency_id, target_currency_id))
        buy_main_resp = self.session.post(base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=BUYER, currency_id=main_currency_id))
        before_buy_main_freezing_value = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=buy_main_resp.text)
        buy_target_resp = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=BUYER, currency_id=target_currency_id))
        before_buy_target_freezing_value = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=buy_target_resp.text)
        before_buy_main_balance_value = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=buy_main_resp.text)

        before_x = transform_freezing_assets(before_buy_main_freezing_value)
        before_y = transform_freezing_assets(before_buy_target_freezing_value)

        sell_main_resp = self.sell_session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=SELLER, currency_id=target_currency_id))
        before_sell_main_freezing_value = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=sell_main_resp.text)
        sell_target_resp = self.sell_session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=SELLER, currency_id=target_currency_id))
        before_sell_target_freezing_value = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=sell_target_resp.text)
        before_a = transform_freezing_assets(before_sell_main_freezing_value)
        before_b = transform_freezing_assets(before_sell_target_freezing_value)

        before_sell_target_balance_value = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=sell_target_resp.text)

        logger.info("用户：{0}----下单前币：{1}--冻结金额：{2}-----下单前币：{3}---冻结金额：{4}".format(BUYER, main_currency_id, before_x, target_currency_id, before_y))
        logger.info("用户：{0}----下单前币：{1}--冻结金额：{2}-----下单前币：{3}---冻结金额：{4}".format(SELLER, main_currency_id, before_a, target_currency_id, before_b))
        logger.info("用户：{0}----下单前币：{1}--余额：{2}".format(BUYER, main_currency_id, before_buy_main_balance_value))
        logger.info("用户：{0}----下单前币：{1}--余额：{2}".format(SELLER, target_currency_id, before_sell_target_balance_value))

        buy_resp = self.session.post(url=base+order_reservations_url, data=get_order_reservations_param(transtion_id=transtion_id, order_type=限价,price=random_price, num=random_num))

        logger.info("URL：{0}-----访问状态：{1}".format(order_reservations_url, buy_resp.status_code))
        buy_status = JMESPathExtractor().extract(query="MSG", body=buy_resp.text)
        logger.info("下限价买单状态：{0}-----下单价格：{1}---------下单数量：{2}".format(buy_status, random_price, random_num))
        logger.info("买单返回信息：{}".format(buy_resp.json()))

        time.sleep(3)

        sell_resp = self.sell_session.post(url=base+sell_order_url, data=get_sell_order_param(transtion_id=transtion_id, order_type=限价, price=random_price, num=sell_random_num))

        logger.info("URL：{0}-----访问状态：{1}".format(sell_order_url, sell_resp.status_code))
        sell_status = JMESPathExtractor().extract(query="MSG", body=sell_resp.text)
        logger.info("下限价卖单状态：{0}-----下单价格：{1}-------下单数量：{2}".format(sell_status, random_price, sell_random_num))
        logger.info("卖单返回信息：{}".format(sell_resp.json()))

        time.sleep(1)
        after_buy_main = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=BUYER, currency_id=main_currency_id))
        after_buy_main_freezing_value = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=after_buy_main.text)
        after_buy_target = self.session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=BUYER, currency_id=target_currency_id))
        after_buy_target_freezing_value = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=after_buy_target.text)

        after_x = transform_freezing_assets(after_buy_main_freezing_value)
        after_y = transform_freezing_assets(after_buy_target_freezing_value)

        after_sell_main = self.sell_session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=SELLER, currency_id=main_currency_id))
        after_sell_main_freezing_value = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=after_sell_main.text)
        after_sell_target = self.sell_session.post(url=base+get_user_balance_servlet_url, data=get_user_balance_servlet_param(user=SELLER, currency_id=target_currency_id))
        after_sell_target_freezing_value = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=after_sell_target.text)

        after_a = transform_freezing_assets(after_sell_main_freezing_value)
        after_b = transform_freezing_assets(after_sell_target_freezing_value)

        after_buy_main_balance_value = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_buy_main.text)
        after_sell_target_balance_value = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=after_sell_target.text)
        print(BUYER, after_x, after_y)
        print(SELLER, after_a, after_b)
        logger.info("用户：{0}----下单后币：{1}--冻结金额：{2}----下单后币：{3}--冻结金额：{4}".format(BUYER, main_currency_id, after_x, target_currency_id, after_y))
        logger.info("用户：{0}----下单后币：{1}--冻结金额：{2}----下单后币：{3}--冻结金额：{4}".format(SELLER, main_currency_id, after_a, target_currency_id, after_b))
        logger.info("用户：{0}----下单后币：{1}---余额：{2}".format(BUYER, main_currency_id, after_buy_main_balance_value))
        logger.info("用户：{0}----下单后币：{1}---余额：{2}".format(SELLER, target_currency_id, after_sell_target_balance_value))

        if random_num > sell_random_num:
            self.assertEqual(int((random_num - sell_random_num) * random_price / 100000000), after_x)
            self.assertEqual(int(before_buy_main_balance_value), int(after_buy_main_balance_value) - int(random_price * random_num/100000000))
        elif random_num < sell_random_num:
            self.assertEqual(int(sell_random_num - random_num), after_b)
            self.assertEqual(int(before_sell_target_balance_value), int(after_sell_target_balance_value) + sell_random_num)


if __name__ == '__main__':
    unittest.main()
