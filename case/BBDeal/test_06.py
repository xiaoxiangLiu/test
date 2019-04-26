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
sell_order_url = names.sell_order_url
update_revocation_status_url = names.update_revocation_status_url
headers = names.login_header
password = names.password

transtion_id = 10
price = 200000000
num = 500000000


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
        正常下限价卖单，验证接口状态、STATUS
        """
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用例编号：6-1------正常下卖单，验证接口状态、STATUS")
        resp = self.session.post(url=base+sell_order_url, data=get_sell_order_param(transtion_id=transtion_id,order_type=限价, price=price,num=num))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        sell_order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=resp.text)
        MSG = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}---url：{1}----接口返回状态：{2}".format(SELLER, sell_order_url, status))
        logger.info("卖单类型：限价单-----交易对ID：{0}-----卖出价格：{1}-----卖出数量：{2}".format(transtion_id, price, num))
        logger.info("下卖单返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "SUCCESS", "0"], [resp.status_code, MSG, status])
        time.sleep(5)
        self.session.post(url=base+update_revocation_status_url, data=get_update_revocation_status_param(_type=2, order_id=sell_order_id))

    def test_02(self):
        """
        错误token下卖单。验证接口状态、MSG、STATUS
        """
        logger.info("用例编号：6-2------错误token下卖单。验证接口状态、MSG、STATUS")
        wrong_token_sell_order_param = {
            "transtionId": transtion_id,
            "orderType": 0,
            "sellerOrderPrice": price,
            "sellerOrderNum": num,
            "timeStamp": "1538118050702",
            "languageType": 3,
            "token": "a65ds465a4sd",
        }
        resp = self.session.post(url=base+sell_order_url, data=wrong_token_sell_order_param)
        sell_order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=resp.text)
        MSG = JMESPathExtractor().extract(query="MSG", body=resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        logger.info("用户：{0}---url：{1}----接口返回状态：{2}".format(SELLER, sell_order_url, status))
        logger.info("错误token的param：{}".format(wrong_token_sell_order_param))
        logger.info("下卖单返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "令牌错误", "1"], [resp.status_code, MSG, status])

    def test_03(self):
        """
        正常下市价卖单，验证接口状态、STATUS
        """
        logger.info("用例编号：6-3---正常下市价卖单，验证接口状态、STATUS")
        resp = self.session.post(url=base+sell_order_url, data=get_sell_order_param(transtion_id=transtion_id,order_type=市价,price="",num=num))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        sell_order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=resp.text)
        MSG = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}---url：{1}----接口返回状态：{2}".format(SELLER, sell_order_url, status))
        logger.info("卖单类型：市价单-----交易对ID：{0}-----卖出价格：{1}-----卖出数量：{2}".format(transtion_id, price, num))
        logger.info("下市价卖单返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "SUCCESS", "0"], [resp.status_code, MSG, status])

    def test_04(self):
        """
        下限价卖单，交易对为空，验证接口返回状态、MSG、STATUS、OBJECT
        """
        logger.info("用例编号：6-4----下限价卖单，交易对为空，验证接口返回状态、MSG、STATUS")
        resp = self.session.post(url=base+sell_order_url, data=get_sell_order_param(transtion_id="",order_type=限价,price=price,num=num))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)

        MSG = JMESPathExtractor().extract(query="MSG", body=resp.text)
        object = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        logger.info("用户：{0}---url：{1}----接口返回状态：{2}".format(SELLER, sell_order_url, status))
        logger.info("卖单类型：市价单-----交易对ID：{0}-----卖出价格：{1}-----卖出数量：{2}".format(transtion_id, price, num))
        logger.info("下市价卖单返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "暂未开放交易", None, "1"], [resp.status_code, MSG, object, status])

    def test_05(self):
        """
        下限价卖单，卖出数量为""，验证接口返回状态、MSG、STATUS、OBJECT
        """
        logger.info("用例编号：6-5------下限价卖单，卖出数量为空，验证接口返回状态、MSG、STATUS、OBJECT")
        resp = self.session.post(url=base+sell_order_url, data=get_sell_order_param(transtion_id=transtion_id,order_type=限价,price=price,num=""))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)

        MSG = JMESPathExtractor().extract(query="MSG", body=resp.text)
        object = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        logger.info("用户：{0}---url：{1}----接口返回状态：{2}".format(SELLER, sell_order_url, status))
        logger.info("卖单类型：市价单-----交易对ID：{0}-----卖出价格：{1}-----卖出数量：{2}".format(transtion_id, price, num))
        logger.info("下市价卖单返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "卖单数量不能为空", None, "1"], [resp.status_code, MSG, object, status])

    def test_06(self):
        """
        下限价卖单，卖出价格为空，验证接口返回状态、MSG、OBJECT、STATUS
        """
        logger.info("用例编号：6-6---下限价卖单，卖出价格为空，验证接口返回状态、MSG、OBJECT、STATUS")
        resp = self.session.post(url=base+sell_order_url, data=get_sell_order_param(transtion_id=transtion_id,order_type=限价,price="",num=num))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)

        MSG = JMESPathExtractor().extract(query="MSG", body=resp.text)
        object = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        logger.info("用户：{0}---url：{1}----接口返回状态：{2}".format(SELLER, sell_order_url, status))
        logger.info("卖单类型：市价单-----交易对ID：{0}-----卖出价格：{1}-----卖出数量：{2}".format(transtion_id, price, num))
        logger.info("下市价卖单返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "交易价格不能为空", None, "1"], [resp.status_code, MSG, object, status])

    def test_07(self):
        """
        下限价卖单，订单类型传3，验证接口返回状态、MSG、OBJECT、STATUS
        """
        logger.info("用例编号：6-7----下限价卖单，订单类型传3，验证接口返回状态、MSG、OBJECT、STATUS")
        resp = self.session.post(url=base+sell_order_url, data=get_sell_order_param(transtion_id=transtion_id,order_type=3,price=price,num=num))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)

        MSG = JMESPathExtractor().extract(query="MSG", body=resp.text)
        object = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        logger.info("用户：{0}---url：{1}----接口返回状态：{2}".format(SELLER, sell_order_url, status))
        logger.info("卖单类型：市价单-----交易对ID：{0}-----卖出价格：{1}-----卖出数量：{2}".format(transtion_id, price, num))
        logger.info("下市价卖单返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "订单类型不正确", None, "1"], [resp.status_code, MSG, object, status])


if __name__ == '__main__':
    unittest.main()
