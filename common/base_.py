__author__ = '123'
# coding=utf-8
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.connectMysql import ConnectMysql
from common.config import GetInit
from common.params import *
from common.names import names
import time
import requests


base_url = names.url_50
login_headers = names.login_header
user_password = names.password


class Base(object):

    def __init__(self, user):

        self.user = user
        self.session = requests.session()

        login_url = names.login_url
        login_param = get_login_param(user=self.user, user_password=user_password)
        login_resp = self.session.post(url=base_url + login_url, headers=login_headers, data=login_param)
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)
        logger.info("base_url：{0}------用户：{1}-----url：{2}------登陆状态：{3}".format(base_url, self.user, login_url, login_status))

    def get_user_balance_servlet(self, currency_id, transaction_id=None, order_id=None):

        get_user_balance_servlet_url = base_url + names.get_user_balance_servlet_url
        param = get_user_balance_servlet_param(user=self.user, currency_id=currency_id, transactionId=transaction_id, orderId=order_id)
        user_balance_details = self.session.post(url=get_user_balance_servlet_url, data=param)
        user_balance_status = JMESPathExtractor().extract(query="MSG", body=user_balance_details.text)
        logger.info("用户：{0}-----url：{1}-------访问状态：{2}".format(self.user, names.get_user_balance_servlet_url, user_balance_status))
        currency_details = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=user_balance_details.text)
        return user_balance_details

    def User_balance_details(self, currency_id=None):

        """
        :param currency_id: int，币ID
        :return:response
        """
        user_Balance_url = base_url + names.user_balance_and_currency_type
        user_balance_detail_url = base_url + names.user_balance_details_url
        #  先查询用户所有交易对的余额，再查询单个币的余额
        user_balance_and_currency_type_param = get_user_balance_and_currency_type_param(user=self.user)
        self.session.post(url=user_Balance_url, data=user_balance_and_currency_type_param)
        #  -----------------------------------------------------------------
        user_balance_details_param = get_user_balance_details_param(user=self.user, currency_id=currency_id)
        user_balance_detail_resp = self.session.post(url=user_balance_detail_url, data=user_balance_details_param)
        currency_details = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=user_balance_detail_resp.text)
        currency_details_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=user_balance_detail_resp.text)
        self.session.close()
        return currency_details

    def OrderReservations(self, transtion_id=None, price=None, num=None, order_type=None):

        """
        下买单
        :param transtion_id: 交易对ID
        :param price: 价格
        :param num: 数量
        :param order_type:订单类型 ，0是限价单，1是市价单
        :return:order_id
        """

        order_reservations_url = base_url + names.order_reservations_url
        order_reservations_param = get_order_reservations_param(transtion_id=transtion_id, order_type=order_type, price=price, num=num)
        order_reservations_resp = self.session.post(url=order_reservations_url, data=order_reservations_param)
        order_reservations_status = JMESPathExtractor().extract(query="MSG", body=order_reservations_resp.text)
        order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=order_reservations_resp.text)
        if order_type == 0:
            logger.info("用户：{0}--买单类型：限价单--买入价格：{1}--买入数量：{2}--下单状态：{3}--订单ID：{4}".format(self.user,price,num,order_reservations_status,order_id))

        elif order_type == 1:
            logger.info("用户：{0}--买单类型：市价单--买入价格：{1}--买入数量：{2}--下单状态：{3}--订单ID：{4}".format(self.user,price,num,order_reservations_status,order_id))
        return order_reservations_resp

    def SellOrder(self, transtion_id=None, price=None, num=None, order_type=None):
        """
        下卖单
        :param transtion_id: 交易对ID
        :param price: 价格
        :param num: 数量
        :param order_type:订单类型 ，0是限价单，1是市价单
        :return:sell_order_id
        """
        sell_order_url = base_url + names.sell_order_url
        sell_order_param = get_sell_order_param(transtion_id=transtion_id, order_type=order_type, num=num, price=price)

        sell_order_resp = self.session.post(url=sell_order_url, data=sell_order_param)
        sell_order_status = JMESPathExtractor().extract(query="MSG", body=sell_order_resp.text)
        sell_order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=sell_order_resp.text)

        if order_type == 0:
            logger.info("用户：{0}-----卖单类型：限价单----卖出价格{1}-------卖出量{2}----下单状态：{3}---订单ID：{4}".format(self.user,price,num,sell_order_status,sell_order_id))

        if order_type == 1:
            logger.info("用户：{0}-----卖单类型：市价单----卖出价格{1}-------卖出量{2}----下单状态：{3}----订单ID：{4}".format(self.user,price,num,sell_order_status,sell_order_id))

        return sell_order_resp

    def updateRevocationStatus(self, type=None, orderId=None):

        """
        撤单接口
        :param lianghua:
        :param type:1买单，2卖单
        :param orderId:订单id
        :return:response
        """

        update_revocation_status_url = base_url + names.update_revocation_status_url
        update_revocation_status_param = get_update_revocation_status_param(order_id=orderId, _type=type)
        update_revocation_status_resp = self.session.post(url=update_revocation_status_url, data=update_revocation_status_param)
        if type == 1:
            logger.info("买单ID:{0}---------撤单返回信息：{1}".format(orderId, update_revocation_status_resp.json()))
        elif type == 2:
            logger.info("卖单ID:{0}---------撤单返回信息：{1}".format(orderId, update_revocation_status_resp.json()))
        return update_revocation_status_resp

    def queryPresentOrder(self, currentPage=1, pageSize=15):
        """
        查询当前委托
        :param currentPage:当前页数
        :param pageSize:当前页包含的数据数量
        :return:response
        """

        self.query_Present_Orde_url = base_url + base.get("query_present_order_url")
        from common.params import get_query_present_order_param
        query_present_order_param = get_query_present_order_param(currentPage=currentPage, pageSize=pageSize)
        query_present_order_param_resp = self.session.post(url=self.query_Present_Orde_url, data=query_present_order_param)
        self.session.close()
        return query_present_order_param_resp

    def queryCurrencyId(self, transtion_id):
        """
        根据交易对ID查询主币ID
        :param transtion_id: 交易对ID，Int类型
        :return:一个数组，第一个是主币ID，第二个是目标币ID
        """
        data = {
            "languageType": 3,
            "timeStamp": "1538118050702",
            "token": "",
        }
        token = get_token(path="air", **data)
        param = {
            "languageType": 3,
            "timeStamp": "1538118050702",
            "token": token,
        }

        url = base_url + "/queryTranstionPair.do"
        if transtion_id >= 2:
            transtion_id = transtion_id - 1
        self.resp = self.session.post(url=url, data=param)
        main_currency_id = JMESPathExtractor().extract(query="LIST["+str(transtion_id)+"].transtionCurrencyBase",
                                                       body=self.resp.text)
        target_currency_id = JMESPathExtractor().extract(query="LIST["+str(transtion_id)+"].transtionCurrencyTarget",
                                                         body=self.resp.text)
        print(JMESPathExtractor().extract(query="LIST["+str(transtion_id)+"].transtionCurrencyTag", body=self.resp.text))
        self.session.close()
        return [main_currency_id, target_currency_id]

    def query_user_main_target_balance(self, mysql_type, transtion_id):

        main_currency_id, target_currency_id = ConnectMysql(_type=mysql_type).query_main_target_currency(transtion_id)
        user_main_balance_resp = self.get_user_balance_servlet(currency_id=main_currency_id)
        time.sleep(0.2)
        user_target_balance_resp = self.get_user_balance_servlet(currency_id=target_currency_id)

        return user_main_balance_resp, user_target_balance_resp

    def close(self):
        self.session.close()

if __name__ == '__main__':
    player = Base(user="39@qq.com")
    resp = player.get_user_balance_servlet(currency_id=2)
    print(resp.json())