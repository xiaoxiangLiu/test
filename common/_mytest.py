__author__ = '123'
# coding=utf-8
import unittest
import requests
from common.tools import names
from common.tools import init_environment_213
from common.params import *
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
from common.AccountTest.Account import init
from common.AccountTest.AccountUtil import crashPrice
import time
import random

base, mysql_type, redis_type, sda_id = init_environment_213()

BUYER = names.user_41
SELLER = names.user_42
user_53 = names.user_48
user_54 = names.user_49

限价 = names.xianjiadan
市价 = names.shijiadan

login_url = names.login_url
logout_url = names.logout_url
sda_get_url = names.sda_get_url
sda_set_stock_price_url = names.sda_set_stock_price_url

headers = names.login_header
password = names.password

sda_order_create_url = names.sda_order_create_url
sda_order_get_open_url = names.sda_order_get_open_url
sda_order_cancel_url = names.sda_order_cancel_url

sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url
sda_account_positions_get_url = names.sda_account_positions_get_url
sda_order_get_history_url = names.sda_order_get_history_url
sda_account_info_url = names.sda_account_info_url
sda_sync_lock_url = names.sda_sync_lock_url


多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
stock_id = "81"
stock_price = 18.11
deal_price = 10000000000
buy_num = sell_num = 10000000000

UNIT = 100000000

def set_stock_price(stock_price,stock_id="81"):
    """
    改变股票价格
    :param stock_id:股票名词，小写字母
    :param stock_price: 股票价格
    :return:
    """
    stock_price_resp = requests.post(url=base+names.sda_set_stock_price_url,
                                     data=get_sda_set_stock_price(stock_id=stock_id,
                                                                  price=stock_price))

    logger.info("接口：{0}--状态：{1}--返回信息：{2}".format(names.sda_set_stock_price_url, stock_price_resp.status_code,
                                                  stock_price_resp.json()))
    stock_price_resp.close()


def sda_sync_lock(session, sync_id=None):
    """
    同步数据接口
    :param sync_id:同步使用的ID
    :return:
    """
    param = get_sda_sync_lock_param(sync_id=sync_id)
    # print(param)
    sync_resp = session.get(url=base+sda_sync_lock_url, params=param)
    return sync_resp.text


class MytestOnePlayer(unittest.TestCase):
    """
    一个登陆用户的测试类
    """

    def setUp(self):
        """
        测试前准备工作，登陆，清除测试环境
        """
        self.sda_balance = 999999900000000
        requests.post(url=base+sda_set_stock_price_url, data=get_sda_set_stock_price(stock_id=stock_id, price=18.11))
        logger.info("--------------------------------------------------------------------------------------------------")
        self.buyer = BUYER
        self.session = requests.session()
        login_resp = self.session.post(url=base+login_url, data=get_login_param(user=self.buyer, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(self.buyer, login_url, login_resp.status_code, login_status))
        self.cookies = self.session.cookies
        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)

        # 清除2个用户名下所有订单
        ConnectMysql(_type=mysql_type).sda_delete_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)

        # 2个用户更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=self.sda_balance)

    def tearDown(self):
        """
        退出登陆，清除测试数据
        """
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(self.buyer, logout_url, logout_resp.status_code, logout_status))

        self.session.close()

def sda_fund_balance(user, session,sda_id):
    """
    资金划转页面接口
    :param user: 用户名
    :param session: session
    :return:
    """
    fund_balance_resp = session.post(url=base+names.sda_fund_balance_url, data=get_sda_fund_balance_param())
    logger.info("用户：{0}---资金划转页面接口：{1}".format(user, fund_balance_resp.json()))
    fund_list = JMESPathExtractor().extract(query="LIST", body=fund_balance_resp.text)
    balance_dict = None
    for i in fund_list:
        if i["sdaId"] == sda_id:
            balance_dict = i

    return balance_dict


def sda_order_create(user, session, sda_id, order_type, order_price_type, lever=1, order_price="", order_num=""):
    """
    下单接口
    :param sda_id: 合约ID
    :param order_type: 订单类型
    :param order_price_type: 订单类型，限价、市价
    :param lever: 杠杆
    :param order_price: 订单价格
    :param order_num: 订单数量
    :return:
    """
    order_create_resp = session.post(url=base+names.sda_order_create_url,
                                     data=get_sda_order_create_param(sda_id=sda_id,
                                                                     order_type=order_type,
                                                                     order_price_type=order_price_type,
                                                                     lever=lever,
                                                                     order_price=order_price,
                                                                     order_num=order_num))
    logger.info("用户：{0}---下单类型：{1}---价格类型{2}---下单价格：{3}---下单数量：{4}--杠杆：{5}--接口返回：{6}".format(user,
                                                                                             order_type,
                                                                                             order_price_type,
                                                                                             order_price,
                                                                                             order_num,
                                                                                             lever,
                                                                                             order_create_resp.status_code))
    return JMESPathExtractor().extract(query="OBJECT", body=order_create_resp.text)


def sda_account_withdraw(user, session, sda_id, amount):
    """
    转出
    :param user: 用户名
    :param session: 用户session
    :param sda_id: 合约id
    :param amount: 转出数量
    :return:
    """
    withdraw_resp = session.post(url=base+names.sda_account_withdraw_url,
                                 data=get_sda_account_withdraw_param(sda_id=sda_id,amount=amount))
    logger.info("用户：{0}---转出：{1}---返回信息：{2}".format(user, amount, withdraw_resp.json()))
    # return JMESPathExtractor().extract(query="OBJECT", body=withdraw_resp.text)
    return withdraw_resp


def market_info_get(user, session, sda_id):
    """
    根据用户和合约查询market_info
    :param user: 用户名
    :param session: 用户session
    :param sda_id: 合约ID
    :return:
    """
    market_resp = session.post(url=base+names.sda_market_info_get_url, data=get_sda_market_info_get_param(sda_id=sda_id))
    logger.info("用户：{0}---接口：{1}--接口状态：{2}---返回信息：{3}".format(user, names.sda_market_info_get_url, market_resp.status_code, market_resp.json()))
    market_dict = JMESPathExtractor().extract(query="OBJECT", body=market_resp.text)

    return market_dict

def account_info(user, session, sda_id, lever=1, sync_id=None, price=1000000000):
    """
    查询单个SDA合约账户信息
    :return:dict
    """
    # sync_status = sda_sync_lock(sync_id=sync_id, session=session)
    #if sync_status == "OK":
    info_resp = session.post(url=base+sda_account_info_url,
                             data=get_sda_account_info_param(sda_id=sda_id, lever=lever))
    logger.info("用户：{0}--接口：{1}---状态：{2}---返回信息：{3}".format(user, sda_account_info_url, info_resp.status_code, info_resp.json()))
    info_dict = JMESPathExtractor().extract(query="OBJECT", body=info_resp.text)

    return info_dict
    # else:
        # print("sync接口返回的状态不是OK")
        # logger.info("sync接口返回的状态不是OK")


def account_info_sync(user, session, sda_id, lever=1,sync_id=None, price=None):
    """
    查询单个SDA合约账户信息
    :return:dict
    """
    sync_status = sda_sync_lock(sync_id=sync_id, session=session)

    if sync_status == "OK":
        info_resp = session.post(url=base+sda_account_info_url,
                                 data=get_sda_account_info_param(sda_id=sda_id, lever=lever))
        logger.info("用户：{0}--接口：{1}---状态：{2}---返回信息：{3}".format(user, sda_account_info_url, info_resp.status_code, info_resp.json()))
        info_dict = JMESPathExtractor().extract(query="OBJECT", body=info_resp.text)
        # print("info_dict", info_dict)
        return info_dict
    else:
        print("sync接口返回的状态不是OK")
        logger.info("sync接口返回的状态不是OK")



def order_cancel(user, session, order_id, order_type):
    """
    撤单接口
    :param user: 用户名
    :param session: 用户session
    :param order_id: 订单ID
    :return:
    """
    cancel_resp = session.post(url=base+sda_order_cancel_url, data=get_sda_order_cancel_param(order_id=order_id, order_type=order_type))
    logger.info("用户：{0}---接口：{1}---状态：{2}---返回信息：{3}".format(user, sda_order_cancel_url, cancel_resp.status_code, cancel_resp.json()))
    cancel_dict = JMESPathExtractor().extract(query="OBJECT", body=cancel_resp.text)

    return cancel_dict


def query_account_position_get(user, session, sync_key=None):
    """
    查询当前持仓
    :param cookies: 传入用户cookies
    :param user: 用户名
    :return: 解析当前持仓返回的数据的dict
    """
    position_dict = None
    if sync_key == None:
        position_resp = session.post(url=base+sda_account_positions_get_url, data=get_sda_account_positions_get_param(sda_id=sda_id))
        logger.info("用户：{0}---接口：{1}--状态：{2}---返回信息：{3}".format(user, sda_account_positions_get_url, position_resp.status_code, position_resp.json()))
        _position_dict = JMESPathExtractor().extract(query="LIST", body=position_resp.text)
        for i in _position_dict:
            position_dict = i
    else:
        sync_resp = sda_sync_lock(session=session, sync_id=sync_key)
        if sync_resp == "OK":
            position_resp = session.post(url=base + sda_account_positions_get_url,
                                         data=get_sda_account_positions_get_param(sda_id=sda_id))
            logger.info("用户：{0}---接口：{1}--状态：{2}---返回信息：{3}".format(user, sda_account_positions_get_url,
                                                                    position_resp.status_code, position_resp.json()))
            _position_dict = JMESPathExtractor().extract(query="LIST", body=position_resp.text)
            for i in _position_dict:
                position_dict = i

        else:
            print("同步接口没有返回OK")
            logger.info("接口：{}---同步接口没有返回OK".format(sda_account_positions_get_url))

    return position_dict


def query_account_asset_detail_get(user, session):
    """
    查询账户详情接口
    :param user: 用户名
    :param session: 用户session
    :return:解析接口返回数据的DICT
    """
    detail_resp = session.post(url=base+sda_account_asset_detail_get_url, data=get_sda_account_asset_detail_get_param())
    detail_dict = JMESPathExtractor().extract(query="OBJECT.PNLList[0]", body=detail_resp.text)
    logger.info("用户：{0}---接口：{1}---状态：{2}--返回信息：{3}".format(user, sda_account_asset_detail_get_url, detail_resp.status_code, detail_resp.json()))

    return detail_dict


def query_order_get_history(user, session, sync_key=None):
    """
    查询历史委托
    :param user:用户名
    :param session: 用户session
    :return:dict
    """
    history_dict = None
    if sync_key == None:
        history_resp = session.post(url=base+sda_order_get_history_url, data=get_sda_order_get_history_param(sda_id=sda_id))
        logger.info("用户：{0}---接口：{1}---状态：{2}---返回信息：{3}".format(user, sda_order_get_history_url, history_resp.status_code, history_resp.json()))
        history_dict = JMESPathExtractor().extract(query="LIST", body=history_resp.text)
    else:
        sync_status = sda_sync_lock(session=session, sync_id=sync_key)
        if sync_status == "OK":
            history_resp = session.post(url=base + sda_order_get_history_url,
                                        data=get_sda_order_get_history_param(sda_id=sda_id))
            logger.info(
                "用户：{0}---接口：{1}---状态：{2}---返回信息：{3}".format(user, sda_order_get_history_url, history_resp.status_code,
                                                             history_resp.json()))
            history_dict = JMESPathExtractor().extract(query="LIST", body=history_resp.text)

    _i = None
    for i in history_dict:
        _i = i
    return _i


def query_order_get_open(user, session, order_id=None):
    """
    查询当前委托接口
    :return:解析的dict
    """
    order_get_open_resp = session.post(url=base+sda_order_get_open_url, data=get_sda_order_get_open_param(sda_id=sda_id, order_id=order_id))
    order_get_open_dict = JMESPathExtractor().extract(query="LIST", body=order_get_open_resp.text)
    logger.info("用户：{0}---接口：{1}---状态：{2}---返回信息：{3}".format(user, sda_order_get_open_url, order_get_open_resp.status_code, order_get_open_resp.json()))

    _value = None
    for i in order_get_open_dict:
        _value = i

    return _value


class MyTestTwoUserLever(unittest.TestCase):
    """
    两个用户的testcase类
    """
    def setUp(self):
        """
        登陆两个用户，获取cookies
        """
        requests.get(url=base+sda_set_stock_price_url, params=get_sda_set_stock_price(stock_id=stock_id, price=18.11))
        time.sleep(6)
        logger.info("--------------------------------------------------------------------------------------------------")
        self.sda_balance = 40*100000000
        self.buyer = BUYER
        self.seller = SELLER

        self.session = requests.session()
        login_resp = self.session.post(url=base+login_url, headers=headers, data=get_login_param(user=BUYER,
                                                                                                 user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(BUYER, login_url,
                                                                      login_resp.status_code, login_status))
        self.cookies = self.session.cookies

        self.sell_session = requests.session()
        sell_login_resp = self.sell_session.post(url=base+login_url, headers=headers, data=get_login_param(user=SELLER, user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}-----登陆状态：{3}".format(
            SELLER, login_url, sell_login_resp.status_code, sell_login_status
        ))
        self.sell_cookies = self.sell_session.cookies

        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)
        self.seller_id = JMESPathExtractor().extract(query="OBJECT.userId", body=sell_login_resp.text)

        # 清除2个用户名下所有订单
        ConnectMysql(_type=mysql_type).sda_delete_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)

        # 2个用户更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.seller_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.seller_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.seller_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

    def tearDown(self):
        """
        退出两个用户的登陆，关闭session
        """
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(BUYER, logout_url, logout_resp.status_code, logout_status))

        self.session.close()

        sell_logout_resp = self.sell_session.post(url=base+logout_url, data=get_user_logout_param())
        sell_logout_status = JMESPathExtractor().extract(query="MSG", body=sell_logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(
            SELLER, logout_url, sell_logout_resp.status_code, sell_logout_status
        ))

        self.sell_session.close()


class MyTestTwoUser(unittest.TestCase):
    """
    两个用户的类
    """
    def setUp(self):
        """
        登陆两个用户，获取cookies
        """
        requests.get(url=base+sda_set_stock_price_url, params=get_sda_set_stock_price(stock_id=stock_id, price=18.11))
        logger.info("--------------------------------------------------------------------------------------------------")
        self.sda_balance = 999999900000000
        self.buyer = BUYER
        self.seller = SELLER

        self.session = requests.session()
        login_resp = self.session.post(url=base+login_url, headers=headers, data=get_login_param(user=self.buyer,
                                                                                                 user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(BUYER, login_url, login_resp.status_code, login_status))
        self.cookies = self.session.cookies

        self.sell_session = requests.session()
        sell_login_resp = self.sell_session.post(url=base+login_url, headers=headers, data=get_login_param(user=self.seller,
                                                                                                           user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}-----登陆状态：{3}".format(
            SELLER, login_url, sell_login_resp.status_code, sell_login_status
        ))
        self.sell_cookies = self.sell_session.cookies

        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)
        self.seller_id = JMESPathExtractor().extract(query="OBJECT.userId", body=sell_login_resp.text)

        # 清除2个用户名下所有订单
        ConnectMysql(_type=mysql_type).sda_delete_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)

        # 2个用户更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.seller_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.seller_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.seller_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

    def tearDown(self):
        """
        退出两个用户的登陆，关闭session
        """
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(BUYER, logout_url, logout_resp.status_code, logout_status))

        self.session.close()

        sell_logout_resp = self.sell_session.post(url=base+logout_url, data=get_user_logout_param())
        sell_logout_status = JMESPathExtractor().extract(query="MSG", body=sell_logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(
            SELLER, logout_url, sell_logout_resp.status_code, sell_logout_status
        ))

        self.sell_session.close()


class MyTestTwoUserBigInt(unittest.TestCase):
    """
    两个用户的类
    """
    def setUp(self):
        """
        登陆两个用户，获取cookies
        """
        requests.get(url=base+sda_set_stock_price_url, params=get_sda_set_stock_price(stock_id=stock_id, price=18.11))
        logger.info("--------------------------------------------------------------------------------------------------")
        self.sda_balance = 90000000000*100000000
        self.buyer = BUYER
        self.seller = SELLER

        self.session = requests.session()
        login_resp = self.session.post(url=base+login_url, headers=headers, data=get_login_param(user=self.buyer,
                                                                                                 user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(BUYER, login_url, login_resp.status_code, login_status))
        self.cookies = self.session.cookies

        self.sell_session = requests.session()
        sell_login_resp = self.sell_session.post(url=base+login_url, headers=headers, data=get_login_param(user=self.seller,
                                                                                                           user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}-----登陆状态：{3}".format(
            SELLER, login_url, sell_login_resp.status_code, sell_login_status
        ))
        self.sell_cookies = self.sell_session.cookies

        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)
        self.seller_id = JMESPathExtractor().extract(query="OBJECT.userId", body=sell_login_resp.text)

        # 清除2个用户名下所有订单
        ConnectMysql(_type=mysql_type).sda_delete_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)

        # 2个用户更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.seller_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.seller_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.seller_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

    def tearDown(self):
        """
        退出两个用户的登陆，关闭session
        """
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(BUYER, logout_url, logout_resp.status_code, logout_status))

        self.session.close()

        sell_logout_resp = self.sell_session.post(url=base+logout_url, data=get_user_logout_param())
        sell_logout_status = JMESPathExtractor().extract(query="MSG", body=sell_logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(
            SELLER, logout_url, sell_logout_resp.status_code, sell_logout_status
        ))

        self.sell_session.close()

class MyTestTwoUserTest(unittest.TestCase):
    """
    两个用户的类
    """
    def setUp(self):
        """
        登陆两个用户，获取cookies
        """
        requests.get(url=base+sda_set_stock_price_url, params=get_sda_set_stock_price(stock_id=stock_id, price=18.11))
        logger.info("--------------------------------------------------------------------------------------------------")
        self.sda_balance = 999999900000000
        self.buyer = BUYER
        self.seller = SELLER

        self.session = requests.session()
        login_resp = self.session.post(url=base+login_url, headers=headers, data=get_login_param(user=BUYER, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(BUYER, login_url, login_resp.status_code, login_status))
        self.cookies = self.session.cookies

        self.sell_session = requests.session()
        sell_login_resp = self.sell_session.post(url=base+login_url, headers=headers, data=get_login_param(user=SELLER, user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}-----登陆状态：{3}".format(
            SELLER, login_url, sell_login_resp.status_code, sell_login_status
        ))
        self.sell_cookies = self.sell_session.cookies

        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)
        self.seller_id = JMESPathExtractor().extract(query="OBJECT.userId", body=sell_login_resp.text)

        # 清除2个用户名下所有订单
        ConnectMysql(_type=mysql_type).sda_delete_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)

        # 2个用户更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.seller_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.seller_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.seller_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

    def tearDown(self):
        """
        退出两个用户的登陆，关闭session
        """
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(BUYER, logout_url, logout_resp.status_code, logout_status))

        self.session.close()

        sell_logout_resp = self.sell_session.post(url=base+logout_url, data=get_user_logout_param())
        sell_logout_status = JMESPathExtractor().extract(query="MSG", body=sell_logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(
            SELLER, logout_url, sell_logout_resp.status_code, sell_logout_status
        ))

        self.sell_session.close()



class MyTestThreeUser(unittest.TestCase):
    """
    三个用户的类
    """
    def setUp(self):
        """
        登陆三个用户，获取cookies
        """
        requests.get(url=base+sda_set_stock_price_url, params=get_sda_set_stock_price(stock_id=stock_id, price=18.11))
        logger.info("--------------------------------------------------------------------------------------------------")
        self.sda_balance = 9999999900000000
        self.buyer = "60@qq.com"
        self.seller = "61@qq.com"
        self.three_user = "62@qq.com"

        self.session = requests.session()
        login_resp = self.session.post(url=base+login_url, headers=headers, data=get_login_param(user=self.buyer, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(BUYER, login_url, login_resp.status_code, login_status))
        self.cookies = self.session.cookies

        self.sell_session = requests.session()
        sell_login_resp = self.sell_session.post(url=base+login_url, headers=headers, data=get_login_param(user=self.seller, user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}-----登陆状态：{3}".format(
            SELLER, login_url, sell_login_resp.status_code, sell_login_status
        ))
        self.sell_cookies = self.sell_session.cookies

        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)
        self.seller_id = JMESPathExtractor().extract(query="OBJECT.userId", body=sell_login_resp.text)

        self.three_session = requests.session()
        three_login_resp = self.three_session.post(url=base+login_url, headers=headers,
                                                   data=get_login_param(user=self.three_user, user_password=password))
        three_login_status = JMESPathExtractor().extract(query="MSG", body=three_login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(self.three_user, login_url,
                                                                      three_login_resp.status_code, three_login_status))
        self.three_user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=three_login_resp.text)


        # 清除3个用户名下所有订单
        ConnectMysql(_type=mysql_type).sda_delete_order(sda_id=sda_id)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)

        # 3个用户更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.seller_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.seller_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.seller_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.three_user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.three_user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.three_user_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

    def tearDown(self):
        """
        退出两个用户的登陆，关闭session
        """
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(BUYER, logout_url, logout_resp.status_code, logout_status))

        self.session.close()

        sell_logout_resp = self.sell_session.post(url=base+logout_url, data=get_user_logout_param())
        sell_logout_status = JMESPathExtractor().extract(query="MSG", body=sell_logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(
            SELLER, logout_url, sell_logout_resp.status_code, sell_logout_status
        ))

        self.sell_session.close()



class MyTestCrash(unittest.TestCase):
    """
    四个用户，同时持仓成功，另外登陆两个用户，爆仓测试类准备工作
    """
    def setUp(self):
        """
        四个用户，分别下多单、空单，持仓成功。另外登陆两个用户
        """
        logger.info("--------------------------------------------------------------------------------------------------")

        self.buyer = BUYER
        self.seller = SELLER
        self.user_53 = user_53
        self.user_54 = user_54

        self.session_53 = requests.session()
        login_53_resp = self.session_53.post(url=base+login_url, data=get_login_param(user=self.user_53, user_password=password))
        login_53_status = JMESPathExtractor().extract(query="MSG", body=login_53_resp.text)
        logger.info("用户：{0}---接口：{1}----接口状态：{2}---登陆状态：{3}".format(self.user_53, login_url, login_53_resp.status_code, login_53_status))

        self.user_53_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_53_resp.text)

        self.session_54 = requests.session()
        login_54_resp = self.session_54.post(url=base+login_url, data=get_login_param(user=self.user_54, user_password=password))
        login_54_status = JMESPathExtractor().extract(query="MSG", body=login_54_resp.text)
        logger.info("用户：{0}---接口：{1}----接口状态：{2}---登陆状态：{3}".format(self.user_54, login_url, login_54_resp.status_code, login_54_status))

        self.user_54_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_54_resp.text)

        self.session = requests.session()
        login_resp = self.session.post(url=base+login_url, data=get_login_param(user=BUYER, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(BUYER, login_url, login_resp.status_code, login_status))

        self.cookies = self.session.cookies
        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)

        self.sell_session = requests.session()
        sell_login_resp = self.sell_session.post(url=base+login_url, data=get_login_param(user=SELLER, user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}-----登陆状态：{3}".format(
            SELLER, login_url, sell_login_resp.status_code, sell_login_status
        ))
        self.sell_cookies = self.sell_session.cookies
        self.seller_id = JMESPathExtractor().extract(query="OBJECT.userId", body=sell_login_resp.text)

        # 获取股票价格
        self.crash_num = 2 * UNIT
        requests.post(url=base+sda_set_stock_price_url, data=get_sda_set_stock_price(stock_id=stock_id, price=18.11))
        market_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        stock_price = int(market_dict["stockPrice"])
        self.unit = int(market_dict["tradeUnit"])
        self.empty_price = int(stock_price * random.uniform(1.0, 1.1))
        self.sda_balance = int(self.crash_num * self.empty_price / 100000000)  # 更新用户余额正好够下单
        print("stock price:", stock_price)
        print("empty price:", self.empty_price)

        print("user balance:", self.sda_balance)

        # 4个用户更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.seller_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.seller_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.seller_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_53_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_53_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_53_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_54_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_54_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_54_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        # 清除4个用户名下所有订单
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.seller_id,
                                                                              contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.seller_id,
                                                                             contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_53_id,
                                                                              contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_53_id,
                                                                             contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id,
                                                                              contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id,
                                                                             contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_54_id,
                                                                              contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_54_id,
                                                                             contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)

        # time.sleep(1)
        self.buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                         order_type=多单,
                                                                                                         order_price_type=限价,
                                                                                                         order_price=self.empty_price,
                                                                                                         order_num=buy_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(self.buyer, sda_order_create_url, self.buy_resp.status_code, self.buy_resp.json()))
        self.buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=self.buy_resp.text)

        # time.sleep(5)
        self.sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                               order_type=空单,
                                                                                                               order_price_type=限价,
                                                                                                               order_price=self.empty_price,
                                                                                                               order_num=sell_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(self.seller, sda_order_create_url, self.sell_resp.status_code, self.sell_resp.json()))
        self.sell_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=self.sell_resp.text)

        buy_detail_dict = query_account_asset_detail_get(user=self.buyer, session=self.session)
        self.before_buy_available = buy_detail_dict["entrustMargin"]
        self.before_buy_entrust_balance = buy_detail_dict["entrustMargin"]

        sell_detail_dict = query_account_asset_detail_get(user=self.seller, session=self.sell_session)
        self.before_sell_entrust_balance = sell_detail_dict["entrustMargin"]
        self.before_sell_available = sell_detail_dict["entrustMargin"]
        # time.sleep(1)

        # 生成此订单的爆仓价
        self.crash_price = crashPrice(holdAvgPrice=self.empty_price, totalBalance=self.sda_balance,
                                      holdCount=self.crash_num, unit=self.unit, doMore=False)

    def tearDown(self):
        """
        退出四个用户的登陆，关闭session
        """
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(BUYER, logout_url, logout_resp.status_code, logout_status))

        self.session.close()

        sell_logout_resp = self.sell_session.post(url=base+logout_url, data=get_user_logout_param())
        sell_logout_status = JMESPathExtractor().extract(query="MSG", body=sell_logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(
            SELLER, logout_url, sell_logout_resp.status_code, sell_logout_status
        ))

        self.sell_session.close()

        self.session_53.close()
        self.session_54.close()


class MyTestOn(unittest.TestCase):
    """
    四个用户，同时持仓成功，另外登陆两个用户
    """
    def setUp(self):
        """
        四个用户，分别下多单、空单，持仓成功。另外登陆两个用户
        """
        self.sda_balance = 9999999900000000
        requests.post(url=base+sda_set_stock_price_url, data=get_sda_set_stock_price(stock_id=stock_id, price=18.11))
        logger.info("--------------------------------------------------------------------------------------------------")

        self.buyer = BUYER
        self.seller = SELLER
        self.user_53 = user_53
        self.user_54 = user_54
        self.deal_price = deal_price
        self.deal_num = sell_num

        self.session_53 = requests.session()
        login_53_resp = self.session_53.post(url=base+login_url, data=get_login_param(user=self.user_53, user_password=password))
        login_53_status = JMESPathExtractor().extract(query="MSG", body=login_53_resp.text)
        logger.info("用户：{0}---接口：{1}----接口状态：{2}---登陆状态：{3}".format(self.user_53, login_url, login_53_resp.status_code, login_53_status))

        self.user_53_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_53_resp.text)

        self.session_54 = requests.session()
        login_54_resp = self.session_54.post(url=base+login_url, data=get_login_param(user=self.user_54, user_password=password))
        login_54_status = JMESPathExtractor().extract(query="MSG", body=login_54_resp.text)
        logger.info("用户：{0}---接口：{1}----接口状态：{2}---登陆状态：{3}".format(self.user_54, login_url, login_54_resp.status_code, login_54_status))

        self.user_54_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_54_resp.text)

        self.session = requests.session()
        login_resp = self.session.post(url=base+login_url, data=get_login_param(user=BUYER, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(BUYER, login_url, login_resp.status_code, login_status))

        self.cookies = self.session.cookies
        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)

        self.sell_session = requests.session()
        sell_login_resp = self.sell_session.post(url=base+login_url, data=get_login_param(user=SELLER, user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}-----登陆状态：{3}".format(
            SELLER, login_url, sell_login_resp.status_code, sell_login_status
        ))
        self.sell_cookies = self.sell_session.cookies
        self.seller_id = JMESPathExtractor().extract(query="OBJECT.userId", body=sell_login_resp.text)

        # 4个用户更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id, sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.seller_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.seller_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.seller_id, sda_id=sda_id, sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_53_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_53_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_53_id, sda_id=sda_id, sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_54_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_54_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_54_id, sda_id=sda_id, sda_balance=self.sda_balance)

        # 清除4个用户名下所有订单
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.seller_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.seller_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_53_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_53_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_54_id, contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_54_id, contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)

        # time.sleep(1)
        self.buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                         order_type=多单,order_price_type=限价,order_price=deal_price,order_num=buy_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(self.buyer, sda_order_create_url, self.buy_resp.status_code, self.buy_resp.json()))
        self.buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=self.buy_resp.text)

        # time.sleep(5)
        self.sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(
            sda_id=sda_id, order_type=空单,order_price_type=限价,order_price=deal_price,order_num=sell_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(self.seller, sda_order_create_url, self.sell_resp.status_code, self.sell_resp.json()))
        self.sell_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=self.sell_resp.text)
        self.sync_key = JMESPathExtractor().extract(query="syncLockKey", body=self.sell_resp.text)

        buy_detail_dict = query_account_asset_detail_get(user=self.buyer, session=self.session)
        self.before_buy_available = buy_detail_dict["entrustMargin"]
        self.before_buy_entrust_balance = buy_detail_dict["entrustMargin"]

        sell_detail_dict = query_account_asset_detail_get(user=self.seller, session=self.sell_session)
        self.before_sell_entrust_balance = sell_detail_dict["entrustMargin"]
        self.before_sell_available = sell_detail_dict["entrustMargin"]
        # time.sleep(1)

    def tearDown(self):
        """
        退出四个用户的登陆，关闭session
        """
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(BUYER, logout_url, logout_resp.status_code, logout_status))

        self.session.close()

        sell_logout_resp = self.sell_session.post(url=base+logout_url, data=get_user_logout_param())
        sell_logout_status = JMESPathExtractor().extract(query="MSG", body=sell_logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(
            SELLER, logout_url, sell_logout_resp.status_code, sell_logout_status
        ))

        self.sell_session.close()

        self.session_53.close()
        self.session_54.close()



class MyTestOnLever(unittest.TestCase):
    """
    四个用户登陆，两个持仓，成交价格10
    """

    low_price = 18*100000000
    low_num = 10*100000000

    def setUp(self):
        """
        四个用户，分别下多单、空单，持仓成功。另外登陆两个用户
        """
        requests.post(url=base+sda_set_stock_price_url, data=get_sda_set_stock_price(stock_id=stock_id, price=18.11))
        self.sda_balance = 9999999900000000
        self.lever = 50

        logger.info(
            "--------------------------------------------------------------------------------------------------")

        self.buyer = BUYER
        self.seller = SELLER
        self.user_53 = user_53
        self.user_54 = user_54

        self.session_53 = requests.session()
        login_53_resp = self.session_53.post(url=base + login_url,
                                             data=get_login_param(user=self.user_53, user_password=password))
        login_53_status = JMESPathExtractor().extract(query="MSG", body=login_53_resp.text)
        logger.info("用户：{0}---接口：{1}----接口状态：{2}---登陆状态：{3}".format(self.user_53, login_url, login_53_resp.status_code,
                                                                    login_53_status))

        self.user_53_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_53_resp.text)

        self.session_54 = requests.session()
        login_54_resp = self.session_54.post(url=base + login_url,
                                             data=get_login_param(user=self.user_54, user_password=password))
        login_54_status = JMESPathExtractor().extract(query="MSG", body=login_54_resp.text)
        logger.info("用户：{0}---接口：{1}----接口状态：{2}---登陆状态：{3}".format(self.user_54, login_url, login_54_resp.status_code,
                                                                    login_54_status))

        self.user_54_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_54_resp.text)

        self.session = requests.session()
        login_resp = self.session.post(url=base + login_url, data=get_login_param(user=BUYER, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info(
            "用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(BUYER, login_url, login_resp.status_code, login_status))

        self.cookies = self.session.cookies
        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)

        self.sell_session = requests.session()
        sell_login_resp = self.sell_session.post(url=base + login_url,
                                                 data=get_login_param(user=SELLER, user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}-----登陆状态：{3}".format(
            SELLER, login_url, sell_login_resp.status_code, sell_login_status
        ))
        self.sell_cookies = self.sell_session.cookies
        self.seller_id = JMESPathExtractor().extract(query="OBJECT.userId", body=sell_login_resp.text)

        # 4个用户更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.seller_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.seller_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.seller_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_53_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_53_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_53_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_54_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_54_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_54_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        # 清除4个用户名下所有订单
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.seller_id,
                                                                              contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.seller_id, contract_id=sda_id,
                                                                             status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_53_id,
                                                                              contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_53_id,
                                                                             contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_54_id,
                                                                              contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_54_id,
                                                                             contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)

        # time.sleep(1)
        self.buy_resp = self.session.post(url=base + sda_order_create_url,
                                          data=get_sda_order_create_param(sda_id=sda_id, order_type=多单,
                                                                          order_price_type=限价,
                                                                          lever=self.lever,
                                                                          order_price=self.low_price,
                                                                          order_num=self.low_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(self.buyer, sda_order_create_url,
                                                                     self.buy_resp.status_code, self.buy_resp.json()))
        self.buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=self.buy_resp.text)

        # time.sleep(5)
        self.sell_resp = self.sell_session.post(url=base + sda_order_create_url,
                                                data=get_sda_order_create_param(sda_id=sda_id, order_type=空单,
                                                                                order_price_type=限价,
                                                                                lever=self.lever,
                                                                                order_price=self.low_price,
                                                                                order_num=self.low_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(self.seller, sda_order_create_url,
                                                                     self.sell_resp.status_code, self.sell_resp.json()))
        self.sell_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=self.sell_resp.text)

        buy_detail_dict = query_account_asset_detail_get(user=self.buyer, session=self.session)
        self.before_buy_available = buy_detail_dict["entrustMargin"]
        self.before_buy_entrust_balance = buy_detail_dict["entrustMargin"]

        sell_detail_dict = query_account_asset_detail_get(user=self.seller, session=self.sell_session)
        self.before_sell_entrust_balance = sell_detail_dict["entrustMargin"]
        self.before_sell_available = sell_detail_dict["entrustMargin"]
        # time.sleep(1)

    def tearDown(self):
        """
        退出四个用户的登陆，关闭session
        """
        logout_resp = self.session.post(url=base + logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(BUYER, logout_url, logout_resp.status_code,
                                                                      logout_status))

        self.session.close()

        sell_logout_resp = self.sell_session.post(url=base + logout_url, data=get_user_logout_param())
        sell_logout_status = JMESPathExtractor().extract(query="MSG", body=sell_logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(
            SELLER, logout_url, sell_logout_resp.status_code, sell_logout_status
        ))

        self.sell_session.close()

        self.session_53.close()
        self.session_54.close()


class MyTestOnTwo(unittest.TestCase):
    """
    四个用户登陆，两个持仓，成交价格10
    """

    low_price = 18*100000000
    low_num = 10*100000000

    def setUp(self):
        """
        四个用户，分别下多单、空单，持仓成功。另外登陆两个用户
        """
        requests.post(url=base+sda_set_stock_price_url, data=get_sda_set_stock_price(stock_id=stock_id, price=18.11))
        self.sda_balance = 9999999900000000

        logger.info(
            "--------------------------------------------------------------------------------------------------")

        self.buyer = BUYER
        self.seller = SELLER
        self.user_53 = user_53
        self.user_54 = user_54

        self.session_53 = requests.session()
        login_53_resp = self.session_53.post(url=base + login_url,
                                             data=get_login_param(user=self.user_53, user_password=password))
        login_53_status = JMESPathExtractor().extract(query="MSG", body=login_53_resp.text)
        logger.info("用户：{0}---接口：{1}----接口状态：{2}---登陆状态：{3}".format(self.user_53, login_url, login_53_resp.status_code,
                                                                    login_53_status))

        self.user_53_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_53_resp.text)

        self.session_54 = requests.session()
        login_54_resp = self.session_54.post(url=base + login_url,
                                             data=get_login_param(user=self.user_54, user_password=password))
        login_54_status = JMESPathExtractor().extract(query="MSG", body=login_54_resp.text)
        logger.info("用户：{0}---接口：{1}----接口状态：{2}---登陆状态：{3}".format(self.user_54, login_url, login_54_resp.status_code,
                                                                    login_54_status))

        self.user_54_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_54_resp.text)

        self.session = requests.session()
        login_resp = self.session.post(url=base + login_url, data=get_login_param(user=BUYER, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info(
            "用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(BUYER, login_url, login_resp.status_code, login_status))

        self.cookies = self.session.cookies
        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)

        self.sell_session = requests.session()
        sell_login_resp = self.sell_session.post(url=base + login_url,
                                                 data=get_login_param(user=SELLER, user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}-----登陆状态：{3}".format(
            SELLER, login_url, sell_login_resp.status_code, sell_login_status
        ))
        self.sell_cookies = self.sell_session.cookies
        self.seller_id = JMESPathExtractor().extract(query="OBJECT.userId", body=sell_login_resp.text)

        # 4个用户更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.seller_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.seller_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.seller_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_53_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_53_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_53_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_54_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_54_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_54_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        # 清除4个用户名下所有订单
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.seller_id,
                                                                              contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.seller_id, contract_id=sda_id,
                                                                             status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_53_id,
                                                                              contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_53_id,
                                                                             contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_id, contract_id=sda_id,
                                                                              status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_id, contract_id=sda_id,
                                                                             status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_empty_close_multi_order(user_id=self.user_54_id,
                                                                              contract_id=sda_id, status=2)
        ConnectMysql(_type=mysql_type).sda_clear_open_multi_close_open_order(user_id=self.user_54_id,
                                                                             contract_id=sda_id, status=2)
        ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)

        # time.sleep(1)
        self.buy_resp = self.session.post(url=base + sda_order_create_url,
                                          data=get_sda_order_create_param(sda_id=sda_id, order_type=多单,
                                                                          order_price_type=限价,
                                                                          order_price=self.low_price,
                                                                          order_num=self.low_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(self.buyer, sda_order_create_url,
                                                                     self.buy_resp.status_code, self.buy_resp.json()))
        self.buy_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=self.buy_resp.text)

        # time.sleep(5)
        self.sell_resp = self.sell_session.post(url=base + sda_order_create_url,
                                                data=get_sda_order_create_param(sda_id=sda_id, order_type=空单,
                                                                                order_price_type=限价,
                                                                                order_price=self.low_price,
                                                                                order_num=self.low_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(self.seller, sda_order_create_url,
                                                                     self.sell_resp.status_code, self.sell_resp.json()))
        self.sell_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=self.sell_resp.text)

        buy_detail_dict = query_account_asset_detail_get(user=self.buyer, session=self.session)
        self.before_buy_available = buy_detail_dict["entrustMargin"]
        self.before_buy_entrust_balance = buy_detail_dict["entrustMargin"]

        sell_detail_dict = query_account_asset_detail_get(user=self.seller, session=self.sell_session)
        self.before_sell_entrust_balance = sell_detail_dict["entrustMargin"]
        self.before_sell_available = sell_detail_dict["entrustMargin"]
        # time.sleep(1)

    def tearDown(self):
        """
        退出四个用户的登陆，关闭session
        """
        logout_resp = self.session.post(url=base + logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(BUYER, logout_url, logout_resp.status_code,
                                                                      logout_status))

        self.session.close()

        sell_logout_resp = self.sell_session.post(url=base + logout_url, data=get_user_logout_param())
        sell_logout_status = JMESPathExtractor().extract(query="MSG", body=sell_logout_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----退出状态：{3}".format(
            SELLER, logout_url, sell_logout_resp.status_code, sell_logout_status
        ))

        self.sell_session.close()

        self.session_53.close()
        self.session_54.close()


def change_stock_price(stock_name, stock_price):
    """
    改变股票价格
    :param stock_name: 股票名字，小写汉字
    :param stock_price: 股票价格
    :return: 无
    """
    url = "/SetStockPrice.do"
    param = {
        "stockPrice": stock_price,
        "stockId": stock_name,
    }
    try:
        resp = requests.post(url=base+url, data=param)
        logger.info("更新股票：{0}---价格为：{1}---返回信息：{2}".format(stock_name, stock_price, resp.json()))
        resp.close()
    except Exception as E:
        print("更新股票价格出错：", E)
        logger.info("更新股票：{0}---价格：{1}出现错误".format(stock_name, stock_price))


def assert_one(first=None, second=None, msg=None):
    flag = None
    if first == second:
        flag = True
    elif first != second:
        flag = False
    logger.info("第一个：{0}  等于  第二个：{1}--检验结果：{2}".format(first, second, flag))
    return flag


def assert_list(first=None, second=None, msg=None):
    """
    接受List，检验两个list是否相同，检验结果写入日志，如果相同返回True，如果不同返回False
    :param first: 第一个list
    :param second: 第二个lsit
    :param msg: 检验信息，用于写入日志，方便查找
    :return:True or False
    """
    flag = None
    if first == second:
        flag = True
    elif first != second:
        flag = False
    logger.info("第一个：{0}  等于  第二个：{1}--检验结果：{2}".format(first, second, flag))
    return flag


def make_stock_value(num,price):
    """
    计算仓位价值、委托价值公式
    :param num: 委托数量或者持仓数量，单位：张
    :param price: 委托价格或者持仓均价，
    :param unit: 最小交易单位，1张=N股
    :return:仓位价值、委托价值
    """
    unit = ConnectMysql(_type=mysql_type).query_sda_unit(sda_id=sda_id)
    _unit = int(unit)/100000000
    stock_value = int(num) * int(price)/100000000 * _unit
    return stock_value


def make_currency_balance(num, price):
    """
    计算保证金，
    :param num:持仓数量、委托数量
    :param price: 持仓均价、委托价格
    :return:委托保证金或者仓位保证金
    """

    def make_stock_value():
        """
        计算仓位价值、委托价值公式
        :return:仓位价值、委托价值
        """
        unit = ConnectMysql(_type=mysql_type).query_sda_unit(sda_id=sda_id)
        _unit = int(unit)/100000000
        stock_value = int(num) * int(price)/100000000 * _unit
        return stock_value

    level = ConnectMysql(_type=mysql_type).query_sda_level(sda_id=sda_id)
    currency_balance = None
    if isinstance(make_stock_value(), int):
        currency_balance = make_currency_balance() / int(level)
    return currency_balance


def make_money(now_price, deal_price, deal_num, unit):
    """
    计算资金费用。
    :param now_price:现货指数
    :param deal_price: 成交价
    :param deal_num: 成交数量
    :param unit: 交易单位
    :return:
    """
    money = abs(now_price - deal_price) / now_price * 0.01 *(deal_price*deal_num*unit)
    print(money)
    return money


def make_busted_price(price, balance_value, num, unit) -> int:
    """
    生成空单持仓爆仓价
    :param price: 持仓均价
    :param balance_value: 实际保证金
    :param num: 持仓量
    :param unit: 交易单位
    :return:爆仓价
    """
    busted_price = ((balance_value * 0.7) / (num * unit)) + price
    return int(busted_price)


def make_busted_order_price(price, balance_value, num, unit) -> int:
    """
    生成空单爆仓挂单价
    :param price: 持仓价
    :param balance_value: 保证金
    :param num: 持仓量
    :param unit: 交易单位
    :return:爆仓挂单价
    """
    busted_order_price = balance_value/(num*unit) + price
    return busted_order_price


if __name__ == '__main__':
    pass