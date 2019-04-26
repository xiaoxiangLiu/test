__author__ = '123'
# coding=utf-8
import unittest
from common._mytest import MyTestOn
from common.tools import init_environment_213
from common.names import names
from common._mytest import MyTestTwoUser
from common.jsonparser import JMESPathExtractor
from common.logger import logger

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_agreement_accept_url = names.sda_agreement_accept_url


class TestCase(MyTestTwoUser):
    """
    交易提醒接口测试类
    """

    def tet_01(self):
        """
        正常访问
        """
        logger.info("用例编号：14-1---交易提醒接口测试，正常访问，验证接口状态、MSG、STATUS")
        param = {
            "languageType": 3,
        }
        agreement_resp = self.session.post(url=base+sda_agreement_accept_url, data=param)
        sell_agreement_resp = self.sell_session.post(url=base+sda_agreement_accept_url, data=param)
        # self.session_53.get(url=base+sda_agreement_accept_url)
        # self.session_54.get(url=base+sda_agreement_accept_url)
        msg = JMESPathExtractor().extract(query="MSG", body=agreement_resp.text)
        status = JMESPathExtractor().extract(query="STATUS", body=agreement_resp.text)
        logger.info("用户：{0}---接口：{1}--状态：{2}---返回信息：{3}".format(self.buyer, sda_agreement_accept_url, agreement_resp.status_code, agreement_resp.json()))

        self.assertListEqual([200, "SUCCESS", "0"], [agreement_resp.status_code, msg, status])


if __name__ == '__main__':
    unittest.main()
