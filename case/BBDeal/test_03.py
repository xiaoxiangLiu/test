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
        查询当前委托接口，验证接口返回状态、MSG、STATUS
        """
        logger.info("用例编号：3-1----查询当前委托接口，验证接口返回状态、MSG、STATUS")
        resp = self.session.post(url=base+query_present_order_url, data=get_query_present_order_param(currentPage=1,pageSize=15))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}----url：{1}-----访问接口状态：{2}".format(BUYER, query_present_order_url, resp.status_code))
        logger.info("查询当前委托返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "SUCCESS", "0"], [resp.status_code, msg, status])

    def test_02(self):
        """
        查询当前委托接口，currencyPage传参：""，验证接口返回状态、MSG、STATUS
        """
        logger.info("用例编号：3-2----查询当前委托接口，currencyPage传参：""，验证接口返回状态、MSG、STATUS")
        resp = self.session.post(url=base+query_present_order_url, data=get_query_present_order_param(currentPage="",pageSize=15))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}----url：{1}-----访问接口状态：{2}".format(BUYER, query_present_order_url, resp.status_code))
        logger.info("查询当前委托返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "SUCCESS", "0"], [resp.status_code, msg, status])

    def test_03(self):
        """
        查询当前委托接口，currencyPage传参：""，pageSize传参：""，验证接口返回状态、MSG、STATUS
        """
        logger.info("用例编号：3-3----查询当前委托接口，currencyPage传参：""，验证接口返回状态、MSG、STATUS")
        resp = self.session.post(url=base+query_present_order_url, data=get_query_present_order_param(currentPage="",pageSize=""))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}----url：{1}-----访问接口状态：{2}".format(BUYER, query_present_order_url, resp.status_code))
        logger.info("查询当前委托返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "SUCCESS", "0"], [resp.status_code, msg, status])

    def test_04(self):
        """
        查询当前委托接口，错误token，验证接口返回状态、MSG、STATUS
        """
        wrong_query_Present_Orde_data = {
            "languageType": 3,
            "currentPage": 1,
            "pageSize": 15,
            "timeStamp": "1538118050702",
            "token": "as65d465as4"
        }
        logger.info("用例编号：3-4----查询当前委托接口，错误token，验证接口返回状态、MSG、STATUS")
        resp = self.session.post(url=base+query_present_order_url, data=wrong_query_Present_Orde_data)
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}----url：{1}-----访问接口状态：{2}".format(BUYER, query_present_order_url, resp.status_code))
        logger.info("查询当前委托返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "令牌错误", None, "1"], [resp.status_code, msg, OBJECT, status])

    def test_05(self):
        """
        查询当前委托接口，pageSize参数传超出长度，currentPage参数超出长度。验证接口返回状态、MSG、STATUS
        """
        logger.info("用例编号：3-5---查询当前委托接口，languageType参数传超出长度，currentPage参数超出长度。验证接口返回状态、MSG、STATUS")
        resp = self.session.post(url=base+query_present_order_url, data=get_query_present_order_param(currentPage=10000, pageSize=15000))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        logger.info("用户：{0}-----url：{1}-----接口状态：{2}".format(BUYER, query_present_order_url, resp.status_code))
        logger.info("查询当前委托返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "SUCCESS", None, "0"], [resp.status_code, msg, OBJECT, status])

    def test_06(self):

        """
        查询当前委托接口，错误languageType参数,验证接口返回状态、MSG、STATUS、
        """
        logger.info("用例编号：3-6----查询当前委托接口，错误languageType参数-5000，验证接口返回状态、MSG、STATUS")
        resp = self.session.post(url=base+query_present_order_url, data=get_query_present_order_param(currentPage=1, pageSize=15))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        logger.info("用户：{0}----url：{1}-----接口状态：{2}".format(BUYER, query_present_order_url, resp.status_code))
        logger.info("查询当前委托返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "SUCCESS", None, "0"], [resp.status_code, msg, OBJECT, status])


if __name__ == '__main__':
    unittest.main()
