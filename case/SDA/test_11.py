__author__ = '123'
# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.params import *
from common.jsonparser import JMESPathExtractor
from common.logger import logger

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_account_asset_get_url = names.sda_account_asset_get_url


class TestCase(MytestOnePlayer):
    """
    账户信息接口测试类
    """
    def test_01(self):
        """
        正常访问
        """
        logger.info("用例编号：11-1--账户信息接口测试类，正常访问，验证接口状态、STATUS、MSG")
        asset_get_resp = self.session.post(url=base+sda_account_asset_get_url, data=get_sda_account_asset_get_param())
        msg = JMESPathExtractor().extract(query="MSG", body=asset_get_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=asset_get_resp.text)
        logger.info("用户：{0}---接口：{1}--状态：{2}---返回信息：{3}".format(self.buyer, sda_account_asset_get_url, asset_get_resp.status_code, asset_get_resp.json()))

        self.assertListEqual([200, "SUCCESS", "0"], [asset_get_resp.status_code, msg, status])


if __name__ == '__main__':
    unittest.main()