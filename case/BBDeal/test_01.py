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
headers = names.login_header
password = names.password
wrong_password = "C1234567"
wrong_user_mail = "a65sd4@qq.com"
transtion_id_list = names.transtion_id
balance_value = names.balance_value

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
        正常登陆，验证返回的状态和状态代码、userId
        """
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用户编号：1-1-----正常登陆，验证返回的状态、状态代码、OBJECT")
        resp = self.session.post(url=base + login_url, headers = headers, data= get_login_param(user=BUYER, user_password=password))
        status = JMESPathExtractor().extract(query="MSG", body=resp.text)
        login_number = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=resp.text)
        logger.info("用户：{0}------登陆url：{1}-------接口返回状态：{2}-------登陆状态{3}".format(BUYER, login_url, resp.status_code, status))
        self.assertListEqual(["SUCCESS","3a4b44f789844704a52ae30852195cc7", "0"], [status, user_id, login_number])

    def test_02(self):
        """
        账号正确，未加密密码登陆，验证返回状态的状态代码、OBJECT
        """
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用例编号：1-2----账号正确，未加密密码登陆，验证返回状态、状态代码、OBJECT")
        resp = self.session.post(url=base + login_url, headers = headers, data= get_login_param(user=BUYER, user_password=wrong_password))
        status = JMESPathExtractor().extract(query="MSG", body=resp.text)
        login_num = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        logger.info("用户：{0}-----错误密码：{1}-------登陆url：{2}-----接口返回状态：{3}-----登陆状态：{4}".format(BUYER, wrong_password, login_url, resp.status_code, status))
        self.assertListEqual(["账户或密码错误！您还有4次登录机会", None, "1"], [status, OBJECT, login_num])

    def test_03(self):
        """
        账号错误，密码正确登陆，验证返回状态和状态代码
        """
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用例编号：1-3---账号错误，密码正确登陆，验证返回状态、状态代码、OBJECT")
        resp = self.session.post(url=base+login_url,headers=headers,data=get_login_param(user=wrong_user_mail, user_password=password))
        status = JMESPathExtractor().extract(query="MSG", body=resp.text)
        login_num = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        logger.info("错误账号：{0}-----登陆url：{1}-----接口返回状态：{2}------登陆状态：{3}".format(wrong_user_mail, login_url, resp.status_code, status))
        self.assertListEqual(["用户未注册", None, "1"], [status, OBJECT, login_num])

    def test_04(self):
        """
        错误token登陆，验证返回状态、状态代码、OBJECT
        """
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用例编号：1-4----空token登陆，验证返回状态、状态代码、OBJECT")
        wrong_token_param = {
            "isAuto": "",
            "userMail": BUYER,
            "platform": "Android",
            "timeStamp": "1538118050702",
            "languageType": 3,
            "userPassword": password,
            "token": "",
            "uuid": "00000000-7508-8fb8-d616-f1c80033c587",
            "version": "1.2.1",
        }
        resp = self.session.post(url=base+login_url, headers=headers,data=wrong_token_param)
        status = JMESPathExtractor().extract(query="MSG", body=resp.text)
        login_num = JMESPathExtractor().extract(query="STATUS", body=resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=resp.text)
        logger.info("用户：{0}-----url：{1}-------接口返回状态：{2}--------登陆状态：{3}".format(BUYER, login_url, resp.status_code, status))
        logger.info("空token的param：{}".format(wrong_token_param))
        self.assertListEqual(["令牌错误",None,"1"], [status, OBJECT, login_num])

    def test_05(self):
        """
        get方式访问接口，验证接口返回状态
        """
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用例编号：1-5-----get方式访问接口，验证接口返回状态")
        resp = self.session.get(url=base + login_url, headers = headers, data= get_login_param(user=BUYER, user_password=password))
        status = JMESPathExtractor().extract(query="MSG", body=resp.text)
        logger.info("用户：{0}-----url：{1}-------接口返回状态：{2}--------登陆状态：{3}".format(BUYER, login_url, resp.status_code, status))
        self.assertEqual("令牌错误", status)

    def test_06(self):
        """
        正常退出，验证接口返回状态、状态代码、OBJECT
        """
        logger.info("分割线----------------------------------------------------------------------------------------------------------------")
        logger.info("用例编号：1-6-----正常退出，验证接口返回状态、状态代码、OBJECT")
        login_resp = self.session.post(url=base+login_url, headers=headers, data=get_login_param(user=BUYER, user_password=password))
        status = JMESPathExtractor().extract(query="MSG", body=login_resp.text)
        logger.info("用户：{0}-----url：{1}------登陆状态：{2}".format(BUYER, login_url, status))
        logout_resp = self.session.post(url=base+logout_url, data=get_user_logout_param())
        status = JMESPathExtractor().extract(query="MSG", body=logout_resp.text)
        OBJECT = JMESPathExtractor().extract(query="OBJECT", body=logout_resp.text)
        logout_num = JMESPathExtractor().extract(query="STATUS", body=logout_resp.text)
        logger.info("用户：{0}---url：{1}-----接口返回状态：{1}------退出登陆状态：{2}".format(BUYER, logout_url, logout_resp.status_code, status))
        self.assertListEqual(["SUCCESS", None, "0"], [status, OBJECT, logout_num])


if __name__ == '__main__':
    unittest.main()