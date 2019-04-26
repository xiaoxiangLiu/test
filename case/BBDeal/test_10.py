__author__ = '123'
# coding=utf-8
import unittest
import requests
from common.names import names
from common.tools import init_environment
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.params import *

base, mysql_type, redis_type = init_environment()
BUYER = names.user_39
SELLER = names.user_41
限价 = names.xianjiadan
市价 = names.shijiadan
买单 = names.buy_order
卖单 = names.sell_order
login_url = names.login_url
logout_url = names.logout_url
query_present_order_url = names.query_present_order_url
headers = names.login_header
password = names.password


class TestUserBalanceDetails(unittest.TestCase):

    def setUp(self):
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        self.session = requests.session()
        login_resp = self.session.post(url=base + login_url, data=get_login_param(user=BUYER, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}------登陆状态：{1}".format(BUYER, login_status))

    def tearDown(self):
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}-------退出状态：{1}".format(BUYER, logout_status))
        self.session.close()

    def test_01(self):
        """
        资讯接口
        """
        pass
