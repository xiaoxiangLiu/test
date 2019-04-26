import unittest
import requests
import warnings
from common.tools import init_environment_otc
from common.names import names
from common.otc_base import *


class SubTest(unittest.TestCase):
    """
    普通用户访问各个接口测试
    """
    def setUp(self):
        """
        登陆用户
        :return:
        """
        warnings.simplefilter("ignore", ResourceWarning)
        self.user_mail = "41@qq.com"
        self.session = requests.session()
        # self.sub_session, login_resp = login(user_mail=self.user_mail, password=names.password)
        self.otc_token = get_otc_token(user_mail=self.user_mail)

    def test_01(self):
        """
        正常访问设置法币交易密码接口
        :return:
        """
        pwd = "123456"
        nick_name = "41@qq.com"
        # print(token)
        set_resp = otc_set_password(otc_token=self.otc_token, session=self.session, pwd=pwd, pwd2=pwd,
                                    nick_name=nick_name)
        print(set_resp.text)

    def test_02(self):
        """
        法币账户接口
        :return:
        """
        asset_resp = otc_user_asset(session=self.session, otc_token=self.otc_token)
        print(asset_resp.json())

    def tearDown(self):
        self.session.close()


if __name__ == '__main__':
    unittest.main()







