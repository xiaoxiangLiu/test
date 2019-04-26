__author__ = '123'
# coding=utf-8
from common.jsonparser import JMESPathExtractor
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.params import *
from common.logger import logger

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_fund_balance_url = names.sda_fund_balance_url


class TestCase(MytestOnePlayer):
    """
    查询用户资金余额接口测试类
    """
    def test_01(self):
        """
        正常访问。
        """
        logger.info("用例编号：17-1---查询用户资金余额接口，正常访问，验证接口状态、MSG、STATUS")
        balance_resp = self.session.post(url=base+sda_fund_balance_url, data=get_sda_fund_balance_param())

        logger.info("用户：{0}--接口：{1}--状态：{2}--返回信息：{3}".format(self.buyer, sda_fund_balance_url, balance_resp.status_code, balance_resp.json()))
        status = JMESPathExtractor().extract(query="STATUS", body=balance_resp.text)
        msg = JMESPathExtractor().extract(query="MSG", body=balance_resp.text)
        self.assertListEqual([200, "SUCCESS", "0"], [balance_resp.status_code, msg, status])


if __name__ == '__main__':
    import unittest
    unittest.main()