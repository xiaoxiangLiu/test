__author__ = '123'
# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import MytestOnePlayer
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.logger import logger

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_account_info_url = names.sda_account_info_url

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan


class TestCase(MytestOnePlayer):
    """
    查询单个SDA合约账户信息接口测试类
    """
    def test_01(self):
        """
        正常访问
        """
        logger.info("用例编号：19-1---查询单个SDA合约账户信息接口，正常访问，验证接口状态、MSG、STATUS")
        info_resp = self.session.post(url=base+sda_account_info_url, data=get_sda_account_info_param(sda_id=sda_id))
        msg = JMESPathExtractor().extract(query="MSG", body=info_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=info_resp.text)
        logger.info("接口：{0}----接口状态：{1}----接口返回信息：{2}".format(sda_account_info_url, info_resp.status_code, info_resp.json()))
        self.assertListEqual([200, "SUCCESS", "0"], [info_resp.status_code, msg, status])


if __name__ == '__main__':
    unittest.main()
