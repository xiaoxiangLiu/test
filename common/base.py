__author__ = '123'
# coding=utf-8
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.config import GetInit
from common.params import *
from common.HTTPclient import HTTPClient
import requests
from common.tools import init_environment
base_url, mysql_type, redis_type = init_environment()


base = GetInit().get_test_data(file_name="base.yaml")
user_password = base.get("password")


class Base(object):

    def __init__(self, user):

        self.user = user

        headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "android-6.0/Meizu(M5)",
        }
        login_url = base_url + base.get("login_url")
        param = get_login_param(user=self.user, user_password=user_password)
        self.r = requests.session()
        login_resp = self.r.post(url=login_url, headers=headers, data=param)
        self.cookies = login_resp.cookies
        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)

    def get_user_balance_servlet(self, currency_id, transaction_id=None, order_id=None):

        get_user_balance_servlet_url = base_url + base.get("get_user_balance_servlet_url")
        param = get_user_balance_servlet_param(user=self.user, currency_id=currency_id, transactionId=transaction_id, orderId=order_id)
        user_balance_details = self.r.post(url=get_user_balance_servlet_url, data=param)
        currency_details = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=user_balance_details.text)
        return currency_details

    def get_user_balance_servlet_2(self, currency_id, transaction_id=None, order_id=None):
        """
        :param currency_id:币ID
        :return:此币余额
        """
        currency_dict = {}
        if isinstance(currency_id, list):
            for i in currency_id:
                get_user_balance_servlet_url = base_url + base.get("get_user_balance_servlet_url")
                param = get_user_balance_servlet_param(user=self.user, currency_id=i, transactionId=transaction_id, orderId=order_id)
                user_balance_details = HTTPClient(url=get_user_balance_servlet_url, method="POST", cookies=self.cookies).send(data=param)
                _currency_details = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=user_balance_details.text)
                currency_dict.update({i: _currency_details})
                return currency_dict
        elif isinstance(currency_id, int) or isinstance(currency_id, str):
            get_user_balance_servlet_url = base_url + base.get("get_user_balance_servlet_url")
            param = get_user_balance_servlet_param(user=self.user, currency_id=currency_id, transactionId=transaction_id, orderId=order_id)
            user_balance_details = HTTPClient(url=get_user_balance_servlet_url, method="POST", cookies=self.cookies).send(data=param)
            currency_details = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=user_balance_details.text)
            return currency_details

    def User_balance_details(self, currency_id=None):

        """
        :param currency_id: int，币ID
        :return:response
        """
        user_Balance_url = base_url + base.get("user_balance_and_currency_type")
        user_balance_detail_url = base_url + base.get("user_balance_details_url")
        #  先查询用户所有交易对的余额，再查询单个币的余额
        user_balance_and_currency_type_param = get_user_balance_and_currency_type_param(user=self.user)
        self.r.post(url=user_Balance_url, data=user_balance_and_currency_type_param)
        #  -----------------------------------------------------------------
        user_balance_details_param = get_user_balance_details_param(user=self.user, currency_id=currency_id)
        user_balance_detail_resp = self.r.post(url=user_balance_detail_url, data=user_balance_details_param)
        currency_details = JMESPathExtractor().extract(query="OBJECT.balanceValue", body=user_balance_detail_resp.text)
        currency_details_freezingAssets = JMESPathExtractor().extract(query="OBJECT.freezingAssets", body=user_balance_detail_resp.text)
        self.r.close()
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

        order_reservations_url = base_url + base.get("order_reservations_url")
        order_reservations_param = get_order_reservations_param(transtion_id=transtion_id, order_type=order_type, price=price, num=num)
        logger.info("买入价格：{0}-------买入数量：{1}".format(price, num))
        order_reservations_resp = self.r.post(url=order_reservations_url, data=order_reservations_param)
        logger.info("下买单信息：{}".format(order_reservations_resp.json()))
        order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=order_reservations_resp.text)
        self.r.close()
        return order_id

    def SellOrder(self, transtion_id=None, price=None, num=None, order_type=None):
        """
        下卖单
        :param transtion_id: 交易对ID
        :param price: 价格
        :param num: 数量
        :param order_type:订单类型 ，0是限价单，1是市价单
        :return:sell_order_id
        """
        sell_order_url = base_url + base.get("sell_order_url")
        sell_order_param = get_sell_order_param(transtion_id, order_type, num=num, price=price)
        logger.info("卖出价格：{0}-------卖出数量：{1}".format(price, num))
        sell_order_resp = self.r.post(url=sell_order_url, data=sell_order_param)

        if order_type == 0:
            logger.info("卖单类型：限价单-----下卖单信息：{}".format(sell_order_resp.json()))
        if order_type == 1:
            logger.info("卖单类型：市价单------下卖单信息：{}".format(sell_order_resp.json()))

        sell_order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=sell_order_resp.text)
        self.r.close()
        return sell_order_id

    def updateRevocationStatus(self, type=None, orderId=None):

        """
        撤单接口
        :param lianghua:
        :param type:1买单，2卖单
        :param orderId:订单id
        :return:response
        """

        update_revocation_status_url = base_url + base.get("update_revocation_status_url")
        update_revocation_status_param = get_update_revocation_status_param(order_id=orderId, _type=type)
        update_revocation_status_resp =self.r.post(url=update_revocation_status_url, data=update_revocation_status_param)
        if type == 1:
            logger.info("买单ID:{0}---------撤单返回信息：{1}".format(orderId, update_revocation_status_resp.json()))
        elif type == 2:
            logger.info("卖单ID:{0}---------撤单返回信息：{1}".format(orderId, update_revocation_status_resp.json()))
        self.r.close()
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
        query_present_order_param_resp = self.r.post(url=self.query_Present_Orde_url, data=query_present_order_param)
        self.r.close()
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
        self.resp = self.r.post(url=url, data=param)
        main_currency_id = JMESPathExtractor().extract(query="LIST["+str(transtion_id)+"].transtionCurrencyBase",
                                                       body=self.resp.text)
        target_currency_id = JMESPathExtractor().extract(query="LIST["+str(transtion_id)+"].transtionCurrencyTarget",
                                                         body=self.resp.text)
        print(JMESPathExtractor().extract(query="LIST["+str(transtion_id)+"].transtionCurrencyTag", body=self.resp.text))
        self.r.close()
        return [main_currency_id, target_currency_id]

    def close(self):
        self.r.close()


if __name__ == '__main__':
    test_buyer = Base(user="39@qq.com")
    print(test_buyer.get_user_balance_servlet(currency_id=2))
