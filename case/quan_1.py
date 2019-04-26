from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
import unittest
from common.tools import init_environment_253
from common.names import names
from common.params import *
import random
import time
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common._mytest import market_info_get
import requests


base, mysql_type, redis_type, sda_id = init_environment_253()
order_create_url = names.sda_order_create_url
login_url = names.login_url
headers = names.login_header
password = names.password

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan


class QuanTest(object):
    """
    给量化账户喂单
    """
    def test_01(self):
        """
        分别喂多、空单，价格随机，数量随机
        :return:
        """
        self.sda_balance = 999999900000000
        self.buyer = "60@qq.com"
        self.seller = "61@qq.com"

        self.session = requests.session()
        login_resp = self.session.post(url=base+login_url, headers=headers, data=get_login_param(user=self.buyer,
                                                                                                 user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}----登陆状态：{3}".format(self.buyer, login_url, login_resp.status_code, login_status))
        self.cookies = self.session.cookies

        self.sell_session = requests.session()
        sell_login_resp = self.sell_session.post(url=base+login_url, headers=headers, data=get_login_param(user=self.seller,
                                                                                                           user_password=password))
        sell_login_status = JMESPathExtractor().extract(query="MSG", body=sell_login_resp.text)
        logger.info("用户：{0}----接口：{1}----接口状态：{2}-----登陆状态：{3}".format(
            self.seller, login_url, sell_login_resp.status_code, sell_login_status
        ))
        self.sell_cookies = self.sell_session.cookies

        self.user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)
        self.seller_id = JMESPathExtractor().extract(query="OBJECT.userId", body=sell_login_resp.text)

        # 2个用户更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.seller_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.seller_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.seller_id, sda_id=sda_id,
                                                               sda_balance=self.sda_balance)

        info_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(int(info_dict["stockPrice"]) / 1000000)

        for i in range(100):
            random_price = random.randint(now_stock_price - 100, now_stock_price + 100) * 1000000
            random_num = random.randint(1, 10) * 100000000
            print("price", random_price)
            print("num", random_num)
            buy_resp = self.session.post(url=base+order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                    order_type=多单,
                                                                                            order_price_type=限价,
                                                                                            order_price=random_price,
                                                                                            order_num=random_num,
                                                                                            ))
            time.sleep(0.1)
            order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=buy_resp.text)
            print("buy order id ：", order_id)
            sell_resp = self.sell_session.post(url=base+order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                          order_type=空单,
                                                                                              order_price_type=限价,
                                                                                              order_price=random_price,
                                                                                              order_num=random_num))
            sell_order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=sell_resp.text)
            print("sell order id ：", sell_order_id)


if __name__ == '__main__':
    QuanTest().test_01()