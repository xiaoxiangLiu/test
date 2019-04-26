__author__ = '123'
# coding=utf-8
import unittest
import requests
from common.names import names
from common.tools import init_environment
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.params import *
import hashlib

base, mysql_type, redis_type = init_environment()
base_url = "http://211.103.178.202:9107/dididu"
BUYER = names.user_39
SELLER = names.user_41
限价 = names.xianjiadan
市价 = names.shijiadan
买单 = names.buy_order
卖单 = names.sell_order
login_url = names.login_url
logout_url = names.logout_url
headers = names.login_header
password = names.password
wrong_password = "C1234567"
wrong_user_mail = "a65sd4@qq.com"
transtion_id_list = names.transtion_id
balance_value = names.balance_value
check_user_url = "/userAuthentication.do"
withdraw_url = "/pandaWithdraw.do"
get_withdraw_status_url = "/getPandaWithdrawStatus.do"


def _md5_user(word):
    """
    加密参数
    :param user_mail: 用户民
    :return:
    """
    key_word = "panda&dididu"
    _user_mail = str(word).lower() + key_word
    print("lower user mail:", _user_mail)
    h = hashlib.md5()
    h.update(_user_mail.encode("UTF-8"))
    print(h.hexdigest())
    return h.hexdigest()


_md5_user(word="38@qq.com")


class TestLogin(unittest.TestCase):
    """
    登陆接口测试
    """

    def setUp(self):
        self.session = requests.session()

    def tearDown(self):
        self.session.close()

    def test_01(self):
        """
        测试提现，签名错误
        """
        check_user_param = {
            "Email": "38@qq.com",
            "Signature": "22e63226e0ae4111bd1834721"
        }

        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用户编号：29-1-----测试提现")
        resp = self.session.post(url=base_url + login_url, headers=headers,
                                 data=get_login_param(user=BUYER, user_password=password))
        status = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}------登陆url：{1}-------接口返回状态：{2}-------登陆状态{3}".format(BUYER, login_url, resp.status_code, status))
        check_user_resp = self.session.post(url=base_url+check_user_url, data=check_user_param)
        check_flag = JMESPathExtractor().extract(query="MSG", body=check_user_resp.text)
        self.assertEqual(check_flag, "签名错误!")

    def test_02(self):
        """
        签名正常访问，用户名错误
        """
        check_user_param = {
            "Email": "3@qq.com",
            "Signature": "22e63226e0ae4111b6161a2bd1834721"
        }
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用户编号：29-2-----测试提现")
        resp = self.session.post(url=base_url + login_url, headers=headers,
                                 data=get_login_param(user=BUYER, user_password=password))
        status = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}------登陆url：{1}-------接口返回状态：{2}-------登陆状态{3}".format(BUYER, login_url, resp.status_code, status))
        check_user_resp = self.session.post(url=base_url+check_user_url, data=check_user_param)
        check_flag = JMESPathExtractor().extract(query="MSG", body=check_user_resp.text)
        self.assertEqual(check_flag, "用户不存在!")

    def test_03(self):
        """
        签名正常访问，用户正常、签名正常
        """
        check_user_param = {
            "Email": "38@qq.com",
            "Signature": "22e63226e0ae4111b6161a2bd1834721"
        }
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用户编号：29-3-----测试提现")
        resp = self.session.post(url=base_url + login_url, headers=headers,
                                 data=get_login_param(user=BUYER, user_password=password))
        status = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}------登陆url：{1}-------接口返回状态：{2}-------登陆状态{3}".format(BUYER, login_url, resp.status_code, status))
        check_user_resp = self.session.post(url=base_url+check_user_url, data=check_user_param)
        check_flag = JMESPathExtractor().extract(query="MSG", body=check_user_resp.text)
        self.assertEqual(check_flag, "用户存在!")

    def test_04(self):
        """
        正常提现
        """
        check_user_param = {
            "Email": "38@qq.com",
            "Signature": "22e63226e0ae4111b6161a2bd1834721"
        }
        withdraw_param = {
            "Email": "38720034@qq.com",
            "number": 3,
            "Signature": "ac0f5266e552fcff5b64d99d80ffdd31",
        }
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用户编号：29-4-----测试提现")
        resp = self.session.post(url=base_url + login_url, headers=headers,
                                 data=get_login_param(user=BUYER, user_password=password))
        status = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}------登陆url：{1}-------接口返回状态：{2}-------登陆状态{3}".format(BUYER, login_url, resp.status_code, status))
        check_user_resp = self.session.post(url=base_url+check_user_url, data=check_user_param)
        withdraw_resp = self.session.post(url=base_url+withdraw_url, data=withdraw_param)
        print(withdraw_resp.status_code)
        print(withdraw_resp.json())

    def test_05(self):
        """
        提现后查询状态
        :return:
        """
        check_user_param = {
            "Email": "38@qq.com",
            "Signature": "22e63226e0ae4111b6161a2bd1834721"
        }
        withdraw_param = {
            "Email": "38720034@qq.com",
            "number": 900000000000,
            "Signature": "2bf28bcd080d619618430b32f77b64b4",
        }
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用户编号：29-4-----测试提现")
        resp = self.session.post(url=base_url + login_url, headers=headers,
                                 data=get_login_param(user=BUYER, user_password=password))
        status = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}------登陆url：{1}-------接口返回状态：{2}-------登陆状态{3}".format(BUYER, login_url, resp.status_code, status))
        check_user_resp = self.session.post(url=base_url+check_user_url, data=check_user_param)
        withdraw_resp = self.session.post(url=base_url+withdraw_url, data=withdraw_param)
        order_id = JMESPathExtractor().extract(query="OBJECT.withdrawId", body=withdraw_resp.text)
        key = _md5_user(word=order_id)
        get_withdraw_status_param = {
            "withdrawId":order_id,
            "Signature":key,
        }
        withdraw_status_resp = self.session.post(url=base_url+get_withdraw_status_url, data=get_withdraw_status_param)
        print(withdraw_status_resp.status_code)
        print(withdraw_status_resp.json())


if __name__ == '__main__':
    unittest.main()
