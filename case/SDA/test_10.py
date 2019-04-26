__author__ = '123'
# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.params import *
from common.jsonparser import JMESPathExtractor
from common.logger import logger

base, mysql_type, redis_type,sda_id = init_environment_213()

sda_account_positions_get_url = names.sda_account_positions_get_url


class TestCase(MytestOnePlayer):
    """
    查询当前持仓接口测试类
    """
    def test_01(self):
        """
        正常访问
        """
        logger.info("用例编号：10-1--查询当前持仓接口测试，正常访问，验证接口状态、STATUS、MSG")
        positons_resp = self.session.post(url=base+sda_account_positions_get_url,
                                          data=get_sda_account_positions_get_param(sda_id=sda_id))
        msg = JMESPathExtractor().extract(query="MSG", body=positons_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=positons_resp.text)
        logger.info("用户：{0}---接口：{1}--状态：{2}---返回信息：{3}".format(self.buyer, sda_account_positions_get_url, positons_resp.status_code, positons_resp.json()))
        print(positons_resp.json())
        self.assertListEqual([200, "SUCCESS", "0"], [positons_resp.status_code, msg, status])


if __name__ == '__main__':
    unittest.main()