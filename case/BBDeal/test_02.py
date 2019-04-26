__author__ = '123'
# coding=utf-8
import unittest
import requests
from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
from common.tools import get_redis_name
from common.names import names
from common.tools import init_environment
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.params import *
import time

base, mysql_type, redis_type = init_environment()
BUYER = names.user_39
SELLER = names.user_41
限价 = names.xianjiadan
市价 = names.shijiadan
买单 = names.buy_order
卖单 = names.sell_order
order_reservations_url = names.order_reservations_url
update_revocation_status_url = names.update_revocation_status_url
login_url = names.login_url
logout_url = names.logout_url
headers = names.login_header
password = names.password
transtion_id = 74
price = 20000
num = 500000000
transtion_id_list = names.transtion_id
balance_value = names.balance_value


class TestOrderReservations(unittest.TestCase):
    """
    下买单接口测试
    """
    @classmethod
    def setUpClass(cls):
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        cls.session = requests.session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def setUp(self):
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        login_resp = self.session.post(url=base + login_url, data=get_login_param(user=BUYER, user_password=password))
        login_status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}------登陆状态：{1}".format(BUYER, login_status))

    def tearDown(self):
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        logout_status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        logger.info("用户：{0}-------退出状态：{1}".format(BUYER, logout_status))

    def test_01(self):
        """
        正常下限价买单，验证返回接口状态、MSG、STATUS
        """
        logger.info("用例编号：2-1-----正常下限价买单，验证返回接口状态、MSG、STATUS")
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=2, order_status=1)
        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id=transtion_id))

        resp = self.session.post(url=base+order_reservations_url, data=get_order_reservations_param(transtion_id=transtion_id, order_type=限价, price=price, num=num))
        status = JMESPathExtractor().extract(query="MSG", body=resp.text)
        buy_num = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        buy_order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=resp.text)
        logger.info("用户：{0}----url：{1}-----接口状态：{2}-----下单状态：{3}".format(BUYER, order_reservations_url, resp.status_code, status))
        logger.info("下限价买单返回信息：{}".format(resp.json()))
        self.assertEqual([200, "SUCCESS", "0"], [resp.status_code, status, buy_num])
        time.sleep(6)
        self.session.post(url=base+update_revocation_status_url, data=get_update_revocation_status_param(_type=买单, order_id=buy_order_id))

    def test_02(self):
        """
        正常下市价买单，验证返回接口状态、MSG、STATUS
        """
        logger.info("用例编号：2-2-----正常下市价买单，验证返回接口状态、MSG、STATUS")
        resp = self.session.post(url=base+order_reservations_url, data=get_order_reservations_param(transtion_id=transtion_id, order_type=市价, price=price,num=num))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        buyer_order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=resp.text)
        logger.info("用户：{0}----url：{1}-----接口状态：{2}".format(BUYER, order_reservations_url, resp.status_code))
        logger.info("下市价买单返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "SUCCESS", "0"], [resp.status_code, msg, status])

    def test_03(self):
        """
        错误token下买单测试，验证接口状态、OBJECT、STATUS
        """
        wrong_param = {
            "transtionId": transtion_id,
            "orderType": 0,
            "buyerOrderPrice": price,
            "buyerOrderNum": num,
            "timeStamp": "1538118050702",
            "languageType": 3,
            "token": "ebf9a4df698f3c4da49d5b8",
        }
        logger.info("用例编号：2-3------错误token下买单测试，验证接口状态、OBJECT、STATUS")
        time.sleep(3)
        resp = self.session.post(url=base+order_reservations_url, data=wrong_param)
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}------url：{1}-----错误token{2}".format(BUYER, order_reservations_url, wrong_param))
        logger.info("限价买单返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "令牌错误", "1"], [resp.status_code, msg, status])

    def test_04(self):
        """
        正常市价买单，价格传入：""，验证接口返回状态、MSG、STATUS
        """
        logger.info("用例编号：2-4---正常市价买单不传买入价格，验证接口返回状态、MSG、STATUS")
        resp = self.session.post(url=base+order_reservations_url, data=get_order_reservations_param(transtion_id=transtion_id,order_type=市价,price="",num=num))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        buyer_order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=resp.text)
        logger.info("用户：{0}------url：{1}-----接口状态{2}".format(BUYER, order_reservations_url, resp.status_code))
        logger.info("市价买单接口返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "SUCCESS", "0"], [resp.status_code, msg, status])

    def test_05(self):
        """
        限价买单，买入价格传参：""，验证接口返回状态、MSG、STATUS、OBJECT
        """
        logger.info("用例编号：2-5---限价买单，买入价格传参：""，验证接口返回状态、MSG、STATUS、OBJECT")
        time.sleep(3)
        resp = self.session.post(url=base+order_reservations_url, data=get_order_reservations_param(transtion_id=transtion_id,order_type=限价,price="",num=num))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        buyer_order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=resp.text)
        logger.info("用户：{0}------url：{1}-----接口状态{2}".format(BUYER, order_reservations_url, resp.status_code))
        logger.info("限价买单接口返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "买入价格为空", "1"], [resp.status_code, msg, status])

    def test_06(self):
        """
        限价买单，买入数量传参：""，验证接口返回状态、MSG、STATUS、OBJECT
        """
        logger.info("用例编号：2-6---限价买单，买入数量传参：""，验证接口返回状态、MSG、STATUS、OBJECT")
        time.sleep(3)
        resp = self.session.post(url=base+order_reservations_url, data=get_order_reservations_param(transtion_id=transtion_id,order_type=限价,price=price,num=""))
        status = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        buyer_order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=resp.text)
        logger.info("用户：{0}------url：{1}-----接口状态{2}".format(BUYER, order_reservations_url, resp.status_code))
        logger.info("限价买单接口返回信息：{}".format(resp.json()))
        self.assertListEqual([200, "订单数量不能为空", "1"], [resp.status_code, msg, status])


if __name__ == '__main__':
    unittest.main()
