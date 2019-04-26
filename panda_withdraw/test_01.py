import requests
import unittest
from common.names import names
from common.tools import init_environment_213
from common._mytest import MyTestTwoUser
from common.jsonparser import JMESPathExtractor
from common._mytest import sda_sync_lock
from common.params import *
import warnings

base, mysql_type, redis_type, sda_id = init_environment_213()
base_1 = "http://192.168.2.213:8080/dididu"
sda_account_create_url = names.sda_account_create_url
login_url = names.login_url
login_header = names.login_header

check_user_url = "/userAuthentication.do"
panda_withdraw_url = "/pandaWithdraw.do"
panda_withdraw_status_url = "/getPandaWithdrawStatus.do"
user_mail = "40@qq.com"
password = names.password


class TestCase(unittest.TestCase):
    """
    panda币提现测试
    """
    def test_01(self):
        """
        未登陆状态访问用户验证接口
        :return:
        """
        param = {
            "Email": "38@qq.com",
            "Signature": "a6s4d65as4d654a6s5d4"
        }
        warnings.simplefilter("ignore", ResourceWarning)
        session = requests.session()
        check_user_resp = session.post(url=base + check_user_url, data=param)
        msg = JMESPathExtractor().extract(query="MSG", body=check_user_resp.text)
        self.assertListEqual(["签名错误!", 200], [msg, check_user_resp.status_code])

    def test_02(self):
        """
        登陆加密状态访问用户验证接口
        :return:
        """
        check_user_param = {
            "Email": "40@qq.com",
            "Signature": "5e8694f2a7456c931fca1aeba37338d3",
        }
        warnings.simplefilter("ignore", ResourceWarning)
        session = requests.session()
        login_resp = session.post(url=base_1+login_url, data=get_login_param(user=user_mail, user_password=password))
        wrong_signature_resp = session.post(url=base+check_user_url, data=check_user_param)
        print(login_resp.json())
        msg = JMESPathExtractor().extract(query="MSG", body=wrong_signature_resp.text)
        self.assertListEqual(["签名错误!", 200], [msg, wrong_signature_resp.status_code])

    def test_03(self):
        """
        正常提现
        :return:
        """
        withdraw_param = {
            "Email": "38720034@qq.com",
            "number": 399999.99999999,
            "Signature": "572ec3716a9f55e869aca8d6d35c68d6",
        }
        warnings.simplefilter("ignore", ResourceWarning)
        session = requests.session()
        login_resp = session.post(url=base_1+login_url, data=get_login_param(user=user_mail, user_password=password))
        print(login_resp.json())
        withdraw_resp = session.post(url=base_1+panda_withdraw_url, data=withdraw_param)
        print(withdraw_resp.status_code)
        print(withdraw_resp.json())
        # withdraw_id = JMESPathExtractor().extract(query="OBJECT.withdrawId", body=withdraw_resp.text)
        # withdraw_status_param = {
        #   "withdrawId": "c2c72be514b744078585492293377016",
        #    "Signature": "ee244514543473b3fe360c497cd1df39"
        # }
        # status_resp = session.post(url=base+panda_withdraw_status_url, data=withdraw_status_param)
        # print(status_resp.status_code, status_resp.json())


if __name__ == '__main__':
    unittest.main()

