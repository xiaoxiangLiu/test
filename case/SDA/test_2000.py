import threading
import requests
from common.names import names
from common.params import *
from common.tools import init_environment_213
from common.jsonparser import JMESPathExtractor
from common._mytest import market_info_get
from common._mytest import account_info
from common._mytest import account_info_sync
import time

base, mysql_type, redis_type, sda_id = init_environment_213()


class MyThread(threading.Thread):
    """
    多线程下单撤单
    """

    def __init__(self, session, sell_sessiion, sda_id):
        super(MyThread, self).__init__()
        self.session = session
        self.sda_id = sda_id
        self.sell_session = sell_sessiion

    def run(self):
        buy_account_dict = account_info(user="41@qq.com", session=session, sda_id=self.sda_id)
        before_buy_balance = int(buy_account_dict["balance"])
        sell_account_dict = account_info(user="42@qq.com", session=self.sell_session, sda_id=self.sda_id)
        before_sell_balance = int(sell_account_dict["balance"])
        print("before buy balance ：", before_buy_balance)
        print("before sell balance ：", before_sell_balance)
        marker_info_dict = market_info_get(user="41@qq.com", session=self.session, sda_id=self.sda_id)
        now_stock_price = int(marker_info_dict["stockPrice"])
        buy_resp = session.post(url=base+names.sda_order_create_url, data=get_sda_order_create_param(sda_id=self.sda_id,
                                                                                          order_type=names.多单,
                                                                                          order_price_type=0,
                                                                                          order_price=now_stock_price,
                                                                                          order_num=100000000))
        # print("buy resp :", buy_resp.json())
        order_id = JMESPathExtractor().extract(query="OBJECT.orderId", body=buy_resp.text)
        # time.sleep(0.2)
        sell_resp = self.sell_session.post(url=base+names.sda_order_create_url, data=get_sda_order_create_param(sda_id=self.sda_id,
                                                                                                                order_type=names.空单,
                                                                                                                order_price_type=1,
                                                                                                                order_price=now_stock_price,
                                                                                                                order_num=100000000,))
        close_buy_resp = session.post(url=base+names.sda_order_create_url, data=get_sda_order_create_param(sda_id=self.sda_id,
                                                                                                           order_type=names.平多,
                                                                                                           order_price_type=0,
                                                                                                           order_price=now_stock_price,
                                                                                                           order_num=100000000,))
        close_sell_resp = sell_session.post(url=base+names.sda_order_create_url, data=get_sda_order_create_param(sda_id=self.sda_id,
                                                                                                            order_type=names.平空,
                                                                                                            order_price_type=1,
                                                                                                            order_price=now_stock_price,
                                                                                                            order_num=100000000,))
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=close_sell_resp.text)
        after_buy_balance_dict = account_info_sync(user="41@qq.com", session=self.session, sda_id=self.sda_id,
                                                   sync_id=sync_id)
        after_buy_balance = after_buy_balance_dict["balance"]

        after_sell_balance_dict = account_info(user="42@qq.com", session=self.sell_session, sda_id=self.sda_id)
        after_sell_balance = after_sell_balance_dict["balance"]

        print("after buy balance ：", after_buy_balance)
        print("after sell balance ：", after_sell_balance)
        time.sleep(0.1)
        # sync_id = JMESPathExtractor().extract(query="syncLockKey", body=cancel_resp.text)
        # after_buy_account_dict = account_info_sync(user="41@qq.com", session=session, sda_id=self.sda_id, sync_id=sync_id)
        # after_buy_balance = int(after_buy_account_dict["balance"])
        # assert before_buy_balance, after_buy_balance


if __name__ == '__main__':
        session = requests.session()
        session.post(url=base + names.login_url, data=get_login_param(user="41@qq.com", user_password=names.password))
        # time.sleep(0.1)
        sell_session = requests.session()
        sell_session.post(url=base+names.login_url, data=get_login_param(user="42@qq.com", user_password=names.password))
        import random
        li = [14, 81, 16]
        for v in range(10000000):
            # time.sleep(1)
            for i in li:
                t = MyThread(session=session, sell_sessiion=sell_session, sda_id=i)
                t.start()
                t.join()


