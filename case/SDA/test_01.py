__author__ = '123'
# coding=utf-8
import requests
import unittest
from common.names import names
from common.tools import init_environment_213
from common._mytest import MyTestTwoUser
from common._mytest import sda_sync_lock

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_account_create_url = names.sda_account_create_url

param = {
    "languageType": "3",
    "sdaId": sda_id
}


class TestCase(MyTestTwoUser):
    """
    创建账户接口测试类
    """
    def tet_01(self):
        create_resp = self.session.post(url=base+sda_account_create_url, data=param)
        sell_create_resp = self.sell_session.post(url=base+sda_account_create_url, data=param)
        print(create_resp.status_code)
        print(create_resp.text)
        print(sell_create_resp.status_code)
        print(sell_create_resp.text)

    def tet_02(self):
        """
        sync_lock
        :return:
        """
        pass


if __name__ == '__main__':
    unittest.main()
