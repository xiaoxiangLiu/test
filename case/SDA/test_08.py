__author__ = '123'
# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.params import *
from common.logger import logger
from common.jsonparser import JMESPathExtractor

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_get_open_url = names.sda_order_get_open_url



class TestCase(MytestOnePlayer):
    """
    查询当前委托测试类
    """
    def test_01(self):
        """
        正常访问
        """
        logger.info("用例编号：8-1---查询当前委托，正常访问，验证接口状态、MSG、STATUS")
        order_get_resp = self.session.post(url=base+sda_order_get_open_url, data=get_sda_order_get_open_param(sda_id=sda_id))
        msg = JMESPathExtractor().extract(query="MSG", body=order_get_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=order_get_resp.text)
        logger.info("用户：{0}---接口：{1}--状态：{2}---返回信息：{3}".format(self.buyer, sda_order_get_open_url, order_get_resp.status_code, order_get_resp.json()))
        self.assertListEqual([200, "SUCCESS", "0"], [order_get_resp.status_code, msg, status])


if __name__ == '__main__':
    unittest.main()