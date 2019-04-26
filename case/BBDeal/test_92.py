__author__ = '123'
# coding=utf-8
from common.tools import get_redis_name
from common.jsonparser import JMESPathExtractor
import requests
from common.connectRedis import ConnectRedis
from common.connectMysql import ConnectMysql
from common.logger import logger
from common.myTest import MyTest
from common.config import GetInit
from common.names import names
from common.params import *
import ddt
from common.run import query_user_balance_value
from common.tools import init_environment

test_data = GetInit().get_test_data(file_name="base.yaml")
user_password = test_data.get("password")
base_url, mysql_type, redis_type = init_environment()
login_header = names.login_header
BUYER = names.user_39
SELLER = names.user_41

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
    def test_01(self, number, transtion_id, main_currency_id, target_currency_id, buy_price, buy_num, sell_price, sell_num):

        logger.info("<<==========================================================================================================================>")

        logger.info("用例说明：  编号：92-1-%s，         大于限价买单数量下单" % number)
        logger.info("买家账号：{0}--------卖家账号：{1}".format(BUYER, SELLER))
        logger.info("-----交易对ID：{0}-----主币ID：{1}-----目标币ID：{2}".format(transtion_id, main_currency_id, target_currency_id))
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=1)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=1)
        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id))

        price_min, num_min = ConnectMysql(_type=mysql_type).query_currency_min(transtion_id=transtion_id)

        buy_price, sell_price, buy_num, sell_num = int(buy_price), int(sell_price), int(buy_num), int(sell_num)

        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=main_currency_id, balance_value=9900000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=target_currency_id, balance_value=9900000000000000)

        before_buy_main, before_buy_target, before_sell_main, before_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )
        login_url = base_url + test_data.get("login_url")
        buy_url = base_url + test_data.get("order_reservations_url")
        session = requests.session()
        session.post(url=login_url, headers=login_header, data=get_login_param(user=BUYER, user_password=user_password))
        resp = session.post(url=buy_url, data=get_order_reservations_param(transtion_id, 0, buy_price, int(num_min) + 1))
        session.close()
        logger.info("下买单信息：{}".format(resp.json()))
        after_buy_main, after_buy_target, after_sell_main, after_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id, transaction_id=transtion_id,
        )
        assert_word = JMESPathExtractor().extract(query="MSG", body=resp.text)
        assert_status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        assert_list = [assert_word, assert_status]
        self.assertEqual(before_buy_main, after_buy_main)
        self.assertEqual(before_buy_target, after_buy_target)
        self.assertListEqual(assert_list, ["最小交易单位不对", "1"])

    @ddt.data(
        transtion_10
    )
    @ddt.unpack
    def test_02(self, number, transtion_id, main_currency_id, target_currency_id, buy_price, buy_num, sell_price, sell_num):

        logger.info("<<==========================================================================================================================>")

        logger.info("用例说明：  编号：92-2-%s，         大于限价卖单数量下单" % number)
        logger.info("买家账号：{0}--------卖家账号：{1}".format(BUYER, SELLER))
        logger.info("-----交易对ID：{0}-----主币ID：{1}-----目标币ID：{2}".format(transtion_id, main_currency_id, target_currency_id))
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=1)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=1)
        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id))

        price_min, num_min = ConnectMysql(_type=mysql_type).query_currency_min(transtion_id=transtion_id)

        buy_price, sell_price, buy_num, sell_num = int(buy_price), int(sell_price), int(buy_num), int(sell_num)

        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=main_currency_id, balance_value=9900000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=target_currency_id, balance_value=9900000000000000)

        before_buy_main, before_buy_target, before_sell_main, before_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )
        login_url = base_url + test_data.get("login_url")
        sell_url = base_url + test_data.get("sell_order_url")
        session = requests.session()
        session.post(url=login_url, headers=login_header, data=get_login_param(user=SELLER, user_password=user_password))
        resp = session.post(url=sell_url, data=get_sell_order_param(transtion_id, 0, sell_price, int(num_min) + 1))
        session.close()
        logger.info("下卖单信息：{}".format(resp.json()))
        after_buy_main, after_buy_target, after_sell_main, after_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id, transaction_id=transtion_id,
        )
        assert_word = JMESPathExtractor().extract(query="MSG", body=resp.text)
        assert_status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        assert_list = [assert_word, assert_status]
        self.assertEqual(before_buy_main, after_buy_main)
        self.assertEqual(before_buy_target, after_buy_target)
        self.assertListEqual(assert_list, ["最小交易单位不正确", "1"])

    @ddt.unpack
    @ddt.data(
        transtion_10
    )
    def test_03(self, number, transtion_id, main_currency_id, target_currency_id, buy_price, buy_num, sell_price, sell_num):

        logger.info("<<==========================================================================================================================>")

        logger.info("用例说明：  编号：92-3-%s，         大于市价买单数量下单" % number)
        logger.info("买家账号：{0}--------卖家账号：{1}".format(BUYER, SELLER))
        logger.info("-----交易对ID：{0}-----主币ID：{1}-----目标币ID：{2}".format(transtion_id, main_currency_id, target_currency_id))
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=1)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=1)
        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id))

        price_min, num_min = ConnectMysql(_type=mysql_type).query_currency_min(transtion_id=transtion_id)

        buy_price, sell_price, buy_num, sell_num = int(buy_price), int(sell_price), int(buy_num), int(sell_num)

        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=main_currency_id, balance_value=9900000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=target_currency_id, balance_value=9900000000000000)

        before_buy_main, before_buy_target, before_sell_main, before_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )
        login_url = base_url + test_data.get("login_url")
        buy_url = base_url + test_data.get("order_reservations_url")
        session = requests.session()
        session.post(url=login_url, headers=login_header, data=get_login_param(user=BUYER, user_password=user_password))
        resp = session.post(url=buy_url, data=get_order_reservations_param(transtion_id, 1, buy_price, int(num_min) + 1))
        session.close()
        logger.info("下买单信息：{}".format(resp.json()))
        after_buy_main, after_buy_target, after_sell_main, after_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id, transaction_id=transtion_id,
        )
        assert_word = JMESPathExtractor().extract(query="MSG", body=resp.text)
        assert_status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        assert_list = [assert_word, assert_status]
        self.assertEqual(before_buy_main, after_buy_main)
        self.assertEqual(before_buy_target, after_buy_target)
        self.assertListEqual(assert_list, ["最小交易单位不对", "1"])

    @ddt.unpack
    @ddt.data(
        transtion_10
    )
    def test_04(self, number, transtion_id, main_currency_id, target_currency_id, buy_price, buy_num, sell_price, sell_num):

        logger.info("<<==========================================================================================================================>")

        logger.info("用例说明：  编号：92-4-%s，         大于市价卖单数量下单" % number)
        logger.info("买家账号：{0}--------卖家账号：{1}".format(BUYER, SELLER))
        logger.info("-----交易对ID：{0}-----主币ID：{1}-----目标币ID：{2}".format(transtion_id, main_currency_id, target_currency_id))
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=1)
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=1)
        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id))

        price_min, num_min = ConnectMysql(_type=mysql_type).query_currency_min(transtion_id=transtion_id)

        buy_price, sell_price, buy_num, sell_num = int(buy_price), int(sell_price), int(buy_num), int(sell_num)

        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=main_currency_id, balance_value=9900000000000000)
        ConnectMysql(_type=mysql_type).update_balance_value(user_mail=BUYER, currency_id=target_currency_id, balance_value=9900000000000000)

        before_buy_main, before_buy_target, before_sell_main, before_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id
        )
        login_url = base_url + test_data.get("login_url")
        sell_url = base_url + test_data.get("sell_order_url")
        session = requests.session()
        session.post(url=login_url, headers=login_header, data=get_login_param(user=SELLER, user_password=user_password))
        resp = session.post(url=sell_url, data=get_sell_order_param(transtion_id, 1, sell_price, int(num_min) + 1))
        session.close()
        logger.info("下卖单信息：{}".format(resp.json()))
        after_buy_main, after_buy_target, after_sell_main, after_sell_target = query_user_balance_value(
            buyer=BUYER, seller=SELLER, main_currency_id=main_currency_id, target_currency_id=target_currency_id, transaction_id=transtion_id,
        )
        assert_word = JMESPathExtractor().extract(query="MSG", body=resp.text)
        assert_status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        assert_list = [assert_word, assert_status]
        self.assertEqual(before_buy_main, after_buy_main)
        self.assertEqual(before_buy_target, after_buy_target)
        self.assertListEqual(assert_list, ["最小交易单位不正确", "1"])


if __name__ == '__main__':
    import unittest
    unittest.main()