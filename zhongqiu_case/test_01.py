__author__ = '123'
# coding=utf-8
import requests, unittest
from common.jsonparser import JMESPathExtractor
from common.logger import logger


class TestWinprobability(unittest.TestCase):

    """
    测试大转盘中奖几率
    """

    def tet_01(self):
        """
        循环次数，验证中奖奖品个数
        """
        self.headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "android-6.0/Meizu(M5)",
        }
        self.param = {
            "isAuto": " ",
            "userMail": "38@qq.com",
            "platform": "Android",
            "timeStamp": "1536997844366",
            "token": "b69b76193d95b196d7f476aa49f443da",
            "userPassword": "1ebb51846675cb9802783d6dae3c8c79",
            "uuid": "00000000-7508-8fb8-d616-f1c80033c587",
            "version": "1.2.1",
        }
        self.login_url = "http://192.168.1.123:10002/dididu/userLogin.do"
        self.r = requests.session()
        self.win_url = "http://192.168.1.123:10002/dididu/winActivityPrize.do"

        for i in range(2):
            with self.subTest():
                win_param = {
                    "activityId": "f90bb97a1a7f4cd099df7e57fd8c5883",
                }
                self.r = requests.session()
                self.r.post(url=self.login_url, headers=self.headers, data=self.param)
                self.resp = self.r.post(url=self.win_url, data=win_param)
                self.prize_id = JMESPathExtractor().extract(query="OBJECT.data.prize_id", body=self.resp.text)
                self.prize_name = JMESPathExtractor().extract(query="OBJECT.data.prize_name", body=self.resp.text)
                print(self.prize_id, self.prize_name)
                logger.info("第{0}次中奖--中奖ID:   {1}----中奖礼品:   {2}".format(i, self.prize_id, self.prize_name))
                print(self.resp.json())
                self.r.close()

if __name__ == '__main__':
    unittest.main()




