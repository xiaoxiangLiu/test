__author__ = '123'
# coding=utf-8
from common.jsonparser import JMESPathExtractor
import requests, unittest, time
from common.config import GetInit
from common.token_ import get_token
transtion_id = 60
class TestCase(unittest.TestCase):

    """
    做市商老接口
    """
    user_buyer_mail = GetInit().GetData("user", "user_buyer_mail")
    user_password = GetInit().GetData("user", "user_password")
    base_url = GetInit().GetData("base", "50_base_url")

    def setUp(self):
        headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "android-6.0/Meizu(M5)",
        }
        url = self.base_url + "/userLogin.do"
        token_param = {
            "isAuto": "",
            "userMail": self.user_buyer_mail,
            "platform": "Android",
            "timeStamp": "1538118050702",
            "token": "",
            "languageType": 3,
            "userPassword": self.user_password,
            "uuid": "00000000-7508-8fb8-d616-f1c80033c587",
            "version": "1.2.1",
        }
        token = get_token(path="gin", **token_param)
        param = {
            "isAuto": "",
            "userMail": self.user_buyer_mail,
            "platform": "Android",
            "timeStamp": "1538118050702",
            "token": token,
            "languageType": 3,
            "userPassword": self.user_password,
            "uuid": "00000000-7508-8fb8-d616-f1c80033c587",
            "version": "1.2.1",
        }
        self.url = self.base_url + "/queryorderrest.do"
        self.requ = requests.session()
        self.resp = self.requ.post(url=url, headers = headers, data=param)

    def tearDown(self):
        self.requ.close()

    def test_01(self):
        """
        做市商根据订单ID查询订单
        """
        self.sell_url = self.base_url + "/ordersellerrest.do"
        sell_data = {
            "sellerOrderNum": 10000000,
            "sellerOrderPrice": 500000,
            "languageType": 3,
            "timeStamp": "1538118050702",
            "transtionId": transtion_id,
            "userMail": "38@qq.com",
            "userPass": "1ebb51846675cb9802783d6dae3c8c79"
        }
        self.sell_resp = self.requ.post(url=self.sell_url, data = sell_data)
        print(self.sell_resp.status_code)
        order_id = JMESPathExtractor().extract(query="OBJECT.sellerOrderId", body=self.sell_resp.text)
        print(order_id)
        time.sleep(4)
        data = {
            "userMail": "38@qq.com",
            "userPass": "1ebb51846675cb9802783d6dae3c8c79",
            "orderId": order_id,
            "type": "2"
        }
        self.resp_3 = self.requ.post(url=self.url, data = data)
        print(self.resp_3.status_code)
        self.assertEqual(self.resp_3.json()["MSG"], "SUCCESS")
        print("接口返回信息:", self.resp_3.json())

if __name__ == '__main__':
    unittest.main()