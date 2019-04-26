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

sda_minute_kline_url = names.sda_minuter_Kline_url


class TestCase(MytestOnePlayer):
    """
    K线接口测试类
    """
    def test_01(self):
        """
        正常访问，
        """
        logger.info("用例编号：16-1--K线接口，正常访问，验证接口状态、MSG、STATUS")
        k_list = [1, 15, 30, 60, 120, 240, 360, 720, 24, 7]
        for i in k_list:
            kline_resp = self.session.post(url=base+sda_minute_kline_url, data=get_sda_minute_kline_param(sda_id=sda_id, k_type=i))
            msg = JMESPathExtractor().extract(query="MSG", body=kline_resp.text)
            status = JMESPathExtractor().extract(query="STATUS", body=kline_resp.text)
            logger.info("用户：{0}---接口：{1}--状态：{2}---传参：{3}---返回信息：{4}".format(self.buyer, sda_minute_kline_url, kline_resp.status_code, i, kline_resp.json()))

            self.assertListEqual([200, "SUCCESS", "0"], [kline_resp.status_code, msg, status])


if __name__ == '__main__':
        unittest.main()