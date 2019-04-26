# coding=utf-8
import unittest
from common._mytest import MytestOnePlayer
from common.tools import init_environment_213
from common.names import names
from common.params import *
from common.jsonparser import JMESPathExtractor
from common.logger import logger

base, mysql_type, redis_type,sda_id = init_environment_213()

home_page_url = names.home_page_url


class TestCase(MytestOnePlayer):
    """
    首页接口
    """
    def test_01(self):
        """
        正常访问
        """
        logger.info("用例编号：201-1--查询首页接口测试，正常访问，验证接口状态、STATUS、MSG")
        positons_resp = self.session.post(url=base+home_page_url, data=home_page(version="1.3.2"))
        msg = JMESPathExtractor().extract(query="MSG", body=positons_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=positons_resp.text)
        print(msg, status, positons_resp.status_code)


if __name__ == '__main__':
    unittest.main()