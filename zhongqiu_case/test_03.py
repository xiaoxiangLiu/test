__author__ = '123'
# coding=utf-8
import requests, unittest, time
from common.jsonparser import JMESPathExtractor
from common.logger import logger
import threading

class TestWinprobability_1(unittest.TestCase):

    """
    测试大转盘中奖几率
    """

    def tet_01(self):
        """
        <-------------------------------------------------------------------------------------->
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

        self.user_balance_data = {
            "currencyId": 4,
            "languageType": 3,
            "timeStamp": int(time.time() * 1000),
            "token": "b69b76193d95b196d7f476aa49f443da",
            "userMail": "38@qq.com",
        }

        # 兑换抽奖次数param
        self.exchangeActivityTimes_param = {
            "activityId": "f90bb97a1a7f4cd099df7e57fd8c5883",
            "times": 4,
        }
        self.login_url = "http://192.168.1.123:10002/dididu/userLogin.do"
        self.r = requests.session()
        self.win_url = "http://192.168.1.123:10002/dididu/winActivityPrize.do"
        self.query_balance_value_url = "http://192.168.1.123:10002/dididu/userBalanceDetails.do"
        # 兑换抽奖次数地址
        self.exchangeActivityTimes_url = "http://192.168.1.123:10002/dididu/exchangeActivityTimes.do"

        logger.info("注释： {0}".format(TestWinprobability_1.tet_01.__doc__))
        logger.info("当前线程：    {0}".format(threading.current_thread()))
        # -------------------------
        self.r = requests.session()
        self.r.post(url=self.login_url, headers=self.headers, data=self.param)
        # ------------------------
        # 购买抽奖次数之前查询余额
        self.balacne_value_resp = self.r.post(url=self.query_balance_value_url, data=self.user_balance_data)
        self.TNB_balance_value = JMESPathExtractor().extract(query="OBJECT.balanceValue",
                                                                body=self.balacne_value_resp.text)
        logger.info("抽奖之前TNB的余额：------{0}".format(self.TNB_balance_value))
        # ------------------------------------
        # 购买抽奖次数--10
        self.exchangeActivityTimes_resp = self.r.post(url=self.exchangeActivityTimes_url,
                                                        data=self.exchangeActivityTimes_param)
        logger.info("user_id : {0}\------times_left : {1}".format(
            JMESPathExtractor().extract(query="OBJECT.data.user_id", body=self.exchangeActivityTimes_resp.text),
        JMESPathExtractor().extract(query="OBJECT.data.times_left", body=self.exchangeActivityTimes_resp.text)))
        self.r.close()
        time.sleep(0.2)

        for i in range(2):
            with self.subTest():
                logger.info("for循环内当前线程：    {0}".format(threading.current_thread()))
                win_param = {
                    "activityId": "f90bb97a1a7f4cd099df7e57fd8c5883",
                }
                self.r = requests.session()
                self.r.post(url=self.login_url, headers=self.headers, data=self.param)
                time.sleep(0.2)

                # 抽奖
                self.resp = self.r.post(url=self.win_url, data=win_param)
                self.prize_id = JMESPathExtractor().extract(query="OBJECT.data.prize_id", body=self.resp.text)
                self.prize_name = JMESPathExtractor().extract(query="OBJECT.data.prize_name", body=self.resp.text)
                print(self.prize_id, self.prize_name)
                logger.info("第{0}次中奖--中奖ID----{1}----中奖礼品----{2}".format(i + 1, self.prize_id, self.prize_name))
                print(self.resp.json())
                self.r.close()

    def test_02(self):
        """
        <-------------------------------------------------------------------------------------->
        循环次数，验证中奖奖品个数
        """
        self.headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "android-6.0/Meizu(M5)",
        }
        self.param = {
            "isAuto": " ",
            "userMail": "39@qq.com",
            "platform": "Android",
            "timeStamp": "1536997844366",
            "token": "b69b76193d95b196d7f476aa49f443da",
            "userPassword": "1ebb51846675cb9802783d6dae3c8c79",
            "uuid": "00000000-7508-8fb8-d616-f1c80033c587",
            "version": "1.2.1",
        }

        self.user_balance_data = {
            "currencyId": 4,
            "languageType": 3,
            "timeStamp": int(time.time() * 1000),
            "token": "b69b76193d95b196d7f476aa49f443da",
            "userMail": "39@qq.com",
        }

        # 兑换抽奖次数param
        self.exchangeActivityTimes_param = {
            "activityId": "f90bb97a1a7f4cd099df7e57fd8c5883",
            "times": 2,
        }
        self.login_url = "http://192.168.1.123:10002/dididu/userLogin.do"
        self.r = requests.session()
        self.win_url = "http://192.168.1.123:10002/dididu/winActivityPrize.do"
        self.query_balance_value_url = "http://192.168.1.123:10002/dididu/userBalanceDetails.do"
        # 兑换抽奖次数地址
        self.exchangeActivityTimes_url = "http://192.168.1.123:10002/dididu/exchangeActivityTimes.do"

        logger.info("注释： {0}".format(TestWinprobability_1.test_02.__doc__))
        logger.info("当前线程：    {0}".format(threading.current_thread()))
        # -------------------------
        self.r = requests.session()
        self.r.post(url=self.login_url, headers=self.headers, data=self.param)
        # ------------------------
        # 购买抽奖次数之前查询余额
        self.balacne_value_resp = self.r.post(url=self.query_balance_value_url, data=self.user_balance_data)
        self.TNB_balance_value = JMESPathExtractor().extract(query="OBJECT.balanceValue",
                                                                body=self.balacne_value_resp.text)
        logger.info("抽奖之前TNB的余额：------{0}".format(self.TNB_balance_value))
        # ------------------------------------
        # 购买抽奖次数--10
        self.exchangeActivityTimes_resp = self.r.post(url=self.exchangeActivityTimes_url,
                                                        data=self.exchangeActivityTimes_param)
        logger.info("user_id : {0}\------times_left : {1}".format(
            JMESPathExtractor().extract(query="OBJECT.data.user_id", body=self.exchangeActivityTimes_resp.text),
        JMESPathExtractor().extract(query="OBJECT.data.times_left", body=self.exchangeActivityTimes_resp.text)))
        self.r.close()
        time.sleep(0.2)

        for i in range(3):
            with self.subTest():
                logger.info("for循环内当前线程：    {0}".format(threading.current_thread()))
                win_param = {
                    "activityId": "67c5b75fbd784ecf8f8f996138420077",
                }
                self.r = requests.session()
                self.r.post(url=self.login_url, headers=self.headers, data=self.param)
                time.sleep(0.2)

                # 抽奖
                self.resp = self.r.post(url=self.win_url, data=win_param)
                self.prize_id = JMESPathExtractor().extract(query="OBJECT.data.prize_id", body=self.resp.text)
                self.prize_name = JMESPathExtractor().extract(query="OBJECT.data.prize_name", body=self.resp.text)
                print(self.prize_id, self.prize_name)
                logger.info("第{0}次中奖--中奖ID----{1}----中奖礼品----{2}".format(i + 1, self.prize_id, self.prize_name))
                print(self.resp.json())
                self.r.close()

if __name__ == '__main__':
    unittest.main()