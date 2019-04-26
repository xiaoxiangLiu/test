__author__ = '123'
# coding=utf-8
import requests, time
from common.jsonparser import JMESPathExtractor
from common.logger import logger
from common.token_ import get_token
from common.config import GetInit
from common.base import Base
import threading


base_url = GetInit().GetData("base", "50_base_url")
user_buyer_mail = GetInit().GetData("user", "user_buyer_mail")
user_password = GetInit().GetData("user", "user_password")

class TestWinprobability(object):

    """
    测试大转盘中奖几率
    """

    def test_02(self):
        """
        <-------------------------------------------------------------------------------------->
        循环次数，验证中奖奖品个数
        """
        headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "android-6.0/Meizu(M5)",
        }
        login_url = base_url + "/userLogin.do"
        token_param = {
            "isAuto": "",
            "userMail": user_buyer_mail,
            "platform": "Android",
            "timeStamp": "1538118050702",
            "token": "",
            "languageType": 3,
            "userPassword": user_password,
            "uuid": "00000000-7508-8fb8-d616-f1c80033c587",
            "version": "1.2.1",
        }
        token = get_token(path="gin", **token_param)

        login_param = {
            "isAuto": "",
            "userMail": user_buyer_mail,
            "platform": "Android",
            "timeStamp": "1538118050702",
            "token": token,
            "languageType": 3,
            "userPassword": user_password,
            "uuid": "00000000-7508-8fb8-d616-f1c80033c587",
            "version": "1.2.1",
        }

        self.user_balance_data = {
            "currencyId": 26,
            "languageType": 3,
            "timeStamp": "1538118050702",
            "token": "5351509846104caa87232d05a885d5fc",
            "userMail": "38@qq.com",
        }

        # 兑换抽奖次数param
        self.exchangeActivityTimes_param = {
            "activityId": "5ff29ea5388245188b6df7c490bcc9aa",
            "times": 100,
        }

        # 查询福袋
        self.getActivityPrizeRecordList_param = {
            "activityId": "5ff29ea5388245188b6df7c490bcc9aa",
        }
        self.login_url = base_url + "/userLogin.do"
        self.r = requests.session()
        self.win_url = base_url + "/winActivityPrize.do"
        self.query_balance_value_url = base_url + "/userBalanceDetails.do"
        # 兑换抽奖次数地址
        self.exchangeActivityTimes_url = base_url + "/exchangeActivityTimes.do"
        self.getActivityPrizeRecordList_url = base_url + "/getActivityPrizeRecordList.do"

        logger.info("注释： {0}".format(TestWinprobability.test_02.__doc__))
        test_buyer = Base(user="buyer")
        before_balacne_value = test_buyer.User_balance_details(currency_id=18)
        test_buyer.close()
        logger.info("抽奖之前用户币的余额：------{0}".format(before_balacne_value))
        # -------------------------
        self.r = requests.session()
        self.r.post(url=self.login_url, headers=headers, data=login_param)
        # ----------------
        # 查询购买之前福袋余额
        self.getActivityPrizeRecordList_resp = self.r.post(url=self.getActivityPrizeRecordList_url, data=self.getActivityPrizeRecordList_param)
        self.getActivityPrizeRecordList_count = len(JMESPathExtractor().extract(query="OBJECT.data", body=self.getActivityPrizeRecordList_resp.text))
        logger.info("购买之前的福袋余额：  {0}".format(
            len(JMESPathExtractor().extract(query="OBJECT.data", body=self.getActivityPrizeRecordList_resp.text))
        ))
        # ------------------------------------
        # 购买抽奖次数--10
        self.exchangeActivityTimes_resp = self.r.post(url=self.exchangeActivityTimes_url,
                                                        data=self.exchangeActivityTimes_param)
        logger.info("user_id : {0}\------times_left : {1}".format(
           JMESPathExtractor().extract(query="OBJECT.data.user_id", body=self.exchangeActivityTimes_resp.text),
        JMESPathExtractor().extract(query="OBJECT.data.times_left", body=self.exchangeActivityTimes_resp.text)))
        self.r.close()
        time.sleep(0.2)

        for i in range(100):
            logger.info("for循环内当前线程：    {0}".format(threading.current_thread()))
            win_param = {
                "activityId": "5ff29ea5388245188b6df7c490bcc9aa",
            }
            self.r = requests.session()
            self.r.post(url=self.login_url, headers=headers, data=login_param)
            time.sleep(0.2)

            # 抽奖
            self.resp = self.r.post(url=self.win_url, data=win_param)
            self.prize_id = JMESPathExtractor().extract(query="OBJECT.data.prize_id", body=self.resp.text)
            self.prize_name = JMESPathExtractor().extract(query="OBJECT.data.prize_name", body=self.resp.text)
            print(self.prize_id, self.prize_name)
            logger.info("第{0}次中奖--福袋余额： {1}--中奖ID----{2}----中奖礼品----{3}".format(
                i + 1, self.getActivityPrizeRecordList_count + 1 + i,self.prize_id, self.prize_name)
            )
            self.r.close()
        # 购买抽奖次数之后查询余额
        test_buyer = Base(user="buyer")
        after_balacne_value = test_buyer.User_balance_details(currency_id=18)
        logger.info("购买之后用户币的余额：{0}".format(after_balacne_value))
        test_buyer.close()


if __name__ == '__main__':
    TestWinprobability().test_02()
