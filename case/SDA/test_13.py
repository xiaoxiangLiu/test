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

query_sda_fund_record_url = names.query_sda_fund_record_url



class TestCase(MytestOnePlayer):
    """
    资金流水接口测试类
    """
    def test_01(self):
        """
        正常访问
        """
        logger.info("用例编号：13-1---资金流水接口测试类，正常访问，验证接口状态、MSG、STATUS")
        fund_resp = self.session.post(url=base+query_sda_fund_record_url, data=get_sda_query_sda_fund_record_param())
        msg = JMESPathExtractor().extract(query="MSG", body=fund_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=fund_resp.text)
        logger.info("用户：{0}---接口：{1}--状态：{2}---返回信息：{3}".format(self.buyer, query_sda_fund_record_url, fund_resp.status_code, fund_resp.json()))

        self.assertListEqual([200, "SUCCESS", "0"], [fund_resp.status_code, msg, status])


if __name__ == '__main__':
    unittest.main()