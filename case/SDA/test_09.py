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

sda_order_get_history_url = names.sda_order_get_history_url

param = {
    "languageType":3,
    "token":"44c497f850dee5dc8d8a21946b57e9fa",
    "timeStamp":"1543493849",
    "sdaId":"ed50033fd2384439947987f19434eea4",
    "page": 1,
    "numPerPage":1,
}


class TestCase(MytestOnePlayer):
    """
    查询历史委托接口测试类
    """
    def test_01(self):
        """
        正常访问
        """
        logger.info("用例编号：9-1---查询历史委托接口，正常访问，验证接口状态、MSG、STATUS")
        history_resp = self.session.post(url=base+sda_order_get_history_url, data=get_sda_order_get_history_param(sda_id=sda_id))
        msg = JMESPathExtractor().extract(query="MSG", body=history_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=history_resp.text)
        logger.info("用户：{0}---接口：{1}--状态：{2}---返回信息：{3}".format(self.buyer, sda_order_get_history_url, history_resp.status_code, history_resp.json()))

        self.assertListEqual([200, "SUCCESS", "0"], [history_resp.status_code, msg, status])


if __name__ == '__main__':
    unittest.main()