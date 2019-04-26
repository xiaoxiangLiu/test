__author__ = '123'
# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import MytestOnePlayer
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.connectMysql import ConnectMysql
from common.names import order_type
from common.connectRedis import ConnectRedis
from common._mytest import assert_list
from common._mytest import assert_one
from common._mytest import account_info
from common._mytest import account_info_sync
from common._mytest import market_info_get
from common.AccountTest.AccountUtil import stockValue


base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_create_url = names.sda_order_create_url
sda_order_get_open_url = names.sda_order_get_open_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url


class TestCase(MytestOnePlayer):
    """
    下单验证合约状态、用户余额
    """

    def test_01(self):
        """
        多单，验证合约状态、余额。
        """
        logger.info("用例编号：20-1---限价多单，验证合约、用户余额。")
        deal_price = 100000000
        deal_num = 100000000
        # 更新此合约ID下的所有合约状态为2
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=990000000000)

        # 查询当前合约的unit
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        # now_stock_price = int(stock_price_dict["stockPrice"])
        stock_unit = int(stock_price_dict["tradeUnit"])
        # print("now stock price", now_stock_price)

        # 下单前查询两个用户的余额
        account_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        buy_balance = account_dict["balance"]

        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=order_type.多单, order_price_type=order_type.限价, order_price=deal_price,
            order_num=deal_num
        ))
        buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=buy_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))

        # 计算委托价值

        stock_value = int(stockValue(price=deal_price, count=deal_num, unit=stock_unit))
        print("stock_value", stock_value)

        # 查询当前委托

        order_get_open_resp = self.session.post(url=base+sda_order_get_open_url,
                                                data=get_sda_order_get_open_param(sda_id=sda_id))
        get_order_id = JMESPathExtractor().extract(query="LIST[0].orderId", body=order_get_open_resp.text)
        order_num = JMESPathExtractor().extract(query="LIST[0].orderQuantity", body=order_get_open_resp.text)
        order_price = JMESPathExtractor().extract(query="LIST[0].orderPrice", body=order_get_open_resp.text)
        total_price = int(JMESPathExtractor().extract(query="LIST[0].totalPrice", body=order_get_open_resp.text))

        order_flag = assert_list([buy_order_id, deal_price, deal_num], [get_order_id, int(order_price), int(order_num)])
        total_price_flag = assert_one(stock_value, total_price)

        self.assertTrue(total_price_flag)
        self.assertTrue(order_flag)

        after_account_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id)
        after_account_balance = after_account_dict["balance"]

        flag = assert_one(int(buy_balance), int(after_account_balance) + deal_num)
        self.assertTrue(flag)

    def test_02(self):
        """
        空单，验证合约状态、余额。
        """
        logger.info("用例编号：20-2---限价空单，验证合约状态、余额。")

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        price = int(int(now_stock_price) * 0.95)

        deal_num = 100000000
        # 更新此合约ID下的所有合约状态为3
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=990000000000)

        # 下单前查询两个用户的余额
        account_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        buy_balance = account_dict["balance"]

        # 下空单
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id,order_type=order_type.空单,order_price_type=order_type.限价,order_price=price,order_num=deal_num
        ))
        buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=buy_resp.text)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))
        # 查询当前委托
        order_get_open_resp = self.session.post(url=base+sda_order_get_open_url, data=get_sda_order_get_open_param(
            sda_id=sda_id, order_id=buy_order_id))

        get_order_id = JMESPathExtractor().extract(query="LIST[0].orderId", body=order_get_open_resp.text)
        order_num = JMESPathExtractor().extract(query="LIST[0].orderQuantity", body=order_get_open_resp.text)
        order_price = JMESPathExtractor().extract(query="LIST[0].orderPrice", body=order_get_open_resp.text)

        # 查询用户余额，然后判断下单前后的用户余额
        after_account_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id)
        after_account_balance = after_account_dict["balance"]

        flag = assert_one(int(buy_balance), int(after_account_balance) + deal_num * price / 100000000)
        self.assertTrue(flag)

    def test_03(self):
        """
        用户可用保证金为0，多单，检查是否下单成功。
        """
        logger.info("用例编号：20-3--用户可用保证金为0，限价多单，检查是否下单成功。")
        deal_num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=0)

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        price = int(int(now_stock_price) * 0.95)

        # min_max = ConnectMysql(_type=mysql_type).sda_query_contract_min(sda_id=sda_id)
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=order_type.空单, order_price_type=order_type.限价, order_price=price,
            order_num=deal_num
        ))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)

        logger.info("用户：{0}--接口：{1}---状态：{2}---返回信息：{3}".format(self.buyer, sda_order_create_url, order_resp.status_code, order_resp.json()))
        flag = assert_list([200, "该订单将会触发您所持仓位的强平", "1"], [order_resp.status_code, msg, status])
        self.assertTrue(flag)

    def test_04(self):
        """
        用户可用保证金为0，空单，检查是否下单成功
        """
        logger.info("用例编号：20-4---用户可用保证金为0，限价空单，检查是否下单成功")

        deal_num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=0)

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = stock_price_dict["stockPrice"]

        price = int(int(now_stock_price) * 0.95)

        # min_max = ConnectMysql(_type=mysql_type).sda_query_contract_min(sda_id=sda_id)
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=order_type.空单, order_price_type=order_type.限价, order_price=price,
            order_num=deal_num
        ))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)

        logger.info("用户：{0}--接口：{1}---状态：{2}---返回信息：{3}".format(self.buyer, sda_order_create_url, order_resp.status_code, order_resp.json()))
        flag = assert_list([200, "该订单将会触发您所持仓位的强平", "1"], [order_resp.status_code, msg, status])
        self.assertTrue(flag)

    def test_05(self):
        """
        市价多单，用户余额为0，验证下单是否成功。
        :return:
        """
        logger.info("用例编号：20-5----市价多单，用户余额为0，验证下单是否成功。")
        deal_price = 100000000
        deal_num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=0)

        # min_max = ConnectMysql(_type=mysql_type).sda_query_contract_min(sda_id=sda_id)
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=order_type.空单, order_price_type=order_type.市价, order_num=deal_num
        ))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)

        logger.info("用户：{0}--接口：{1}---状态：{2}---返回信息：{3}".format(self.buyer, sda_order_create_url,
                                                                order_resp.status_code, order_resp.json()))
        flag = assert_list([200, "可建仓余额不足", "1"], [order_resp.status_code, msg, status])
        self.assertTrue(flag)

    def test_06(self):
        """
        时间空单，用户可用余额为0，验证是否下单成功。
        :return:
        """
        deal_price = 100000000
        deal_num = 100000000
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=0)

        # min_max = ConnectMysql(_type=mysql_type).sda_query_contract_min(sda_id=sda_id)
        order_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=order_type.空单, order_price_type=order_type.市价, order_num=deal_num
        ))
        msg = JMESPathExtractor().extract(query="MSG", body=order_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_resp.text)

        logger.info("用户：{0}--接口：{1}---状态：{2}---返回信息：{3}".format(self.buyer, sda_order_create_url, order_resp.status_code, order_resp.json()))
        flag = assert_list([200, "可建仓余额不足", "1"], [order_resp.status_code, msg, status])
        self.assertTrue(flag)


if __name__ == '__main__':
    unittest.main()
