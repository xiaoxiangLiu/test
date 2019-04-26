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

base, mysql_type, redis_type = init_environment()
BUYER = names.user_39
SELLER = names.user_41
限价 = names.xianjiadan
市价 = names.shijiadan
买单 = names.buy_order
卖单 = names.sell_order
login_url = names.login_url
logout_url = names.logout_url

query_transtion_pari_url = names.query_transtion_pari_url
headers = names.login_header
password = names.password

transtion_id = 23
price = 20000
num = 50000000


class TestUserBalanceDetails(unittest.TestCase):

    def setUp(self):
        self.session = requests.session()
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        login_resp = self.session.post(url=base + login_url, data=get_login_param(user=SELLER, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}------登陆状态：{1}".format(SELLER, login_status))

    def tearDown(self):
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}-------退出状态：{1}".format(SELLER, logout_status))
        self.session.close()

    def test_01(self):
        """
        查询交易对接口，正常访问，验证接口状态、MSG、STATUS、OBJECT
        """
        logger.info("用例编号：5-1---查询交易对接口，正常访问，验证接口状态、MSG、STATUS、OBJECT")
        resp = self.session.post(url=base+query_transtion_pari_url, data=get_query_transtion_pair_param())
        logger.info("用户：{0}----URL：{1}-----接口状态：{2}".format(BUYER, query_transtion_pari_url, resp.status_code))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("查询交易对接口返回信息：{}".format(resp.json()))

        self.assertListEqual([200, "SUCCESS", "0"], [resp.status_code, msg, status])

    def test_02(self):
        """
        查询交易对接口，错误token，验证接口状态、MSG、STATUS、OBJECT
        """
        logger.info("用例编号：5-2---查询交易对接口，错误token，验证接口状态、MSG、STATUS、OBJECT")
        wrong_param = {
            "timeStamp":"1542016948959",
            "languageType":3,
            "token":"a65s4",
        }
        resp = self.session.post(url=base+query_transtion_pari_url, data=wrong_param)
        logger.info("用户：{0}-----URL：{1}-----接口状态：{2}".format(BUYER, query_transtion_pari_url, resp.status_code))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("查询交易对接口返回信息：{}".format(resp.json()))
        try:
            self.assertListEqual([200, "令牌错误", "1"], [resp.status_code, msg, status])
            raise Exception
        except Exception as E:
            logger.info("用例断言异常：{}".format(E))


if __name__ == '__main__':
    unittest.main()