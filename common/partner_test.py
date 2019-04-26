import unittest
import requests
from common.tools import names
from common.tools import inti_environment_partner
from common.params import *
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
from common.AccountTest.Account import init
from common.AccountTest.AccountUtil import crashPrice
import time
import random

base_url, mysql_type, redis_type = inti_environment_partner()


class PartnerTest(unittest.TestCase):
    """
    代理商测试类
    """

    def setUp(self):
        """
        登陆
        :return:
        """
        self.sys_user = "admin"
        self.sys_passwd = "123456"
        self.session = requests.session()
        login = self.session.post(url=base_url+names.partner_login_url,
                                  data=get_partner_login_param(user=self.sys_user,passwd=self.sys_passwd))
        time.sleep(0.1)
        logger.info("代理商登陆：{}".format(login.json()))
        rest_passwd_resp = self.session.post(url=base_url + names.partner_rest_password_url,
                                       data=get_partner_rest_password_param(
                                           sys_user_id="28"))
        logger.info("代理商重置密码：{}".format(rest_passwd_resp.json()))

    def tearDown(self):
        """
        退出登陆
        :return:
        """
        self.session.close()