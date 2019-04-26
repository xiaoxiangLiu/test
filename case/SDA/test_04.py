__author__ = '123'
# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.logger import logger
from common.jsonparser import JMESPathExtractor
from common.params import *

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_get_list_url = names.sda_get_list_url


class TestCase(MytestOnePlayer):
    """
    查询SDA列表信息
    """
    def test_01(self):
        """
        正常访问，验证接口状态、STATUS、MSG
        """
        logger.info("用例编号：4-1----查询SDA列表信息，正常访问，验证接口状态、STATUS、MSG")
        list_resp = self.session.post(url=base+sda_get_list_url, data=get_sda_get_list_param())
        logger.info("接口：{0}---状态：{1}--返回信息：{2}".format(sda_get_list_url, list_resp.status_code, list_resp.json()))
        msg = JMESPathExtractor().extract(query="MSG", body=list_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=list_resp.text)

        self.assertListEqual([200, "0", "SUCCESS"], [list_resp.status_code, status, msg])


if __name__ == '__main__':
    unittest.main()