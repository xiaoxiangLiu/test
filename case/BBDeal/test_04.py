__author__ = '123'
# coding=utf-8
import unittest
import requests
from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
from common.names import names
from common.tools import init_environment
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.tools import get_redis_name
import time

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
order_reservations_url = names.order_reservations_url
update_revocation_status_url = names.update_revocation_status_url
headers = names.login_header
password = names.password

transtion_id = 23
price = 885536
num = 73047500000000

class TestCase(unittest.TestCase):

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
        撤单接口，下买单正常撤单，验证接口返回状态、STATS、MSG、OBJECT
        """
        logger.info("用例编号：4-1--撤单接口，下买单正常撤单，验证接口返回状态、STATS、MSG、OBJECT")
        buy_resp = self.session.post(url=base+order_reservations_url, data=get_order_reservations_param(transtion_id=transtion_id,order_type=限价,price=price,num=num))
        logger.info("用户：{0}-----url：{1}-----接口状态：{2}".format(BUYER, order_reservations_url, buy_resp.status_code))
        buy_order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=buy_resp.text)
        logger.info("买单返回信息：{}".format(buy_resp.json()))
        # 撤单
        time.sleep(5)
        update_order_resp = self.session.post(url=base+update_revocation_status_url, data=get_update_revocation_status_param(_type=买单,order_id=buy_order_id))
        logger.info("用户：{0}-----url：{1}-----接口返回状态：{2}".format(BUYER, update_revocation_status_url, update_order_resp.status_code))
        status = JMESPathExtractor().extract(query="STATUS", body=update_order_resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=update_order_resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=update_order_resp.text)
        logger.info("撤单返回信息：{0}".format(update_order_resp.json()))

        self.assertListEqual([200, "SUCCESS", None, "0"], [update_order_resp.status_code, msg, OBJECT, status])

    def tet_02(self):
        """
        撤单接口，错误token，验证接口返回状态、MSG、OBJECT、STATUS
        """
        logger.info("用例编号：4-2--撤单接口，错误token，验证接口返回状态、MSG、OBJECT、STATUS")
        buy_resp = self.session.post(url=base+order_reservations_url, data=get_order_reservations_param(transtion_id=transtion_id,order_type=限价,price=price,num=num))
        logger.info("用户：{0}-----url：{1}-----接口状态：{2}".format(BUYER, order_reservations_url, buy_resp.status_code))
        buy_order_id = JMESPathExtractor().extract(query="OBJECT.buyerOrderId", body=buy_resp.text)
        logger.info("买单返回信息：{}".format(buy_resp.json()))
        # 撤单
        wrong_param = {
            "languageType": 3,
            "timeStamp": "1538118050702",
            "type": 买单,
            "orderId": buy_order_id,
            "token": "a65s4d",
        }
        time.sleep(5)
        update_resp = self.session.post(url=base+update_revocation_status_url, data=wrong_param)
        logger.info("用户：{0}----url：{1}-----接口状态：{2}".format(BUYER, update_revocation_status_url, update_resp.status_code))
        logger.info("撤单返回信息：{}".format(update_resp.json()))
        status = JMESPathExtractor().extract(query="STATUS", body=update_resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=update_resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=update_resp.text)

        self.assertListEqual([200, "令牌错误", None, "1"], [update_resp.status_code, msg, OBJECT, status])

    def tet_03(self):
        """
        撤单接口，错误买单ID，验证接口返回状态、MSG、STATUS、OBJECT
        """
        logger.info("用例编号：4-3---撤单接口，错误买单ID，验证接口返回状态、MSG、STATUS、OBJECT")
        update_resp = self.session.post(url=base+update_revocation_status_url, data=get_update_revocation_status_param(_type=买单, order_id="a56s4d6a54sd"))
        logger.info("用户：{0}----url：{1}-----接口状态：{2}".format(BUYER, update_revocation_status_url, update_resp.status_code))
        logger.info("撤单返回信息：{}".format(update_resp.json()))
        status = JMESPathExtractor().extract(query="STATUS", body=update_resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=update_resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=update_resp.text)

        self.assertListEqual([200, "订单不存在", None, "1"], [update_resp.status_code, msg, OBJECT, status])

    def tet_04(self):
        """
        撤单接口，下卖单正常撤单，验证接口返回状态、MSG、STATUS、OBJECT
        """
        logger.info("用例编号：4-4---撤单接口，下卖单正常撤单，验证接口返回状态、MSG、STATUS、OBJECT")
        ConnectMysql(_type=mysql_type).update_order_status(transtion_id=transtion_id, order_type=1, order_status=1)
        ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id=transtion_id))
        sell_resp = self.session.post(url=base+sell_order_url, data=get_sell_order_param(transtion_id=transtion_id,order_type=限价,price=price,num=num))
        sell_order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=sell_resp.text)
        logger.info("URL：{0}-----卖单接口返回状态：{1}-------卖单返回信息：{2}".format(sell_order_url,sell_resp.status_code, sell_resp.json()))
        time.sleep(5)
        update_resp = self.session.post(url=base+update_revocation_status_url, data=get_update_revocation_status_param(_type=卖单,order_id=sell_order_id))
        status = JMESPathExtractor().extract(query="STATUS", body=update_resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=update_resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=update_resp.text)
        logger.info("用户：{0}----url：{1}------接口状态：{2}".format(BUYER, update_revocation_status_url, update_resp.status_code))
        logger.info("撤单返回信息：{}".format(update_resp.json()))
        self.assertListEqual([200, "SUCCESS", "0"], [update_resp.status_code, msg, status])

    def tet_05(self):
        """
        撤单接口，错误卖单ID撤单，验证接口返回状态、MSG、STATUS、OBJECT
        """
        logger.info("用例编号：4-5---撤单接口，错误卖单ID撤单，验证接口返回状态、MSG、STATUS、OBJECT")
        update_resp = self.session.post(url=base+update_revocation_status_url, data=get_update_revocation_status_param(_type=卖单, order_id="sajd56"))
        status = JMESPathExtractor().extract(query="STATUS", body=update_resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=update_resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBEJCT", body=update_resp.text)
        logger.info("用户：{0}----url：{1}-----接口状态：{2}".format(BUYER, update_revocation_status_url, update_resp.status_code))
        logger.info("撤单返回信息：{}".format(update_resp.json()))
        self.assertListEqual([200, "订单不存在", "1"], [update_resp.status_code, msg, status])


if __name__ == '__main__':
    unittest.main()