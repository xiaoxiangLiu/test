__author__ = '123'
# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common._mytest import assert_list
from common._mytest import account_info

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_get_url = names.sda_get_url

param = {
    "languageType":3,
    "token":"44c497f850dee5dc8d8a21946b57e9fa",
    "timeStamp":"1543493849",
    "sdaId":"b7850e9d2bb740578630e51acd761c2a",
}

class TestCase(MytestOnePlayer):
    """
    查询单个SDA信息接口测试类
    """

    def test_01(self):
        """
        正常访问
        """
        info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id, price=1000000000)
        info_user_id = info_dict["userId"]
        info_sda_id = info_dict["sdaId"]
        # 验证返回的sda_id和user_id是否正确
        assert_list([info_user_id, info_sda_id], [self.user_id, sda_id])


if __name__ == '__main__':
    unittest.main()