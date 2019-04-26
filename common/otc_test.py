import unittest
from common.otc_base import login
import requests
from common.tools import names
from common.tools import init_environment_213
from common.params import *
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
from common.AccountTest.Account import init
from common.AccountTest.AccountUtil import crashPrice
import time
import random


class childMerchantTest(unittest.TestCase):
    """
    商家、用户登陆
    """
    def setUp(self):
        """
        登陆一个商家、一个用户
        :return:
        """
        # Merchant_session, login_resp = login(user_mail=)
        # pass