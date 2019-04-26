# coding=utf-8
import unittest
import warnings
from common.tools import init_environment_213
from common.names import names
from common._mytest import MyTestThreeUser
from common._mytest import account_info
from common._mytest import account_info_sync
from common.params import *
from common.logger import logger
from common.AccountTest.AccountUtil import openStockCost
import time
from common.jsonparser import JMESPathExtractor
from common._mytest import market_info_get
from common.connectMysql import ConnectMysql
from common.AccountTest.AccountUtil import *
import random

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_create_url = names.sda_order_create_url
sda_order_get_open_url = names.sda_order_get_open_url
sda_order_cancel_url = names.sda_order_cancel_url

sda_get_url = names.sda_get_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url
sda_account_positions_get_url = names.sda_account_positions_get_url

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan


class TestCase(MyTestThreeUser):
    """
    不同手续费和资金费率测试类
    """
    def test_01(self):
        """
        参数化测试不同手续费和资金费率
        :return:
        """
        lever = 10
        logger.info("用例编号：130-1---参数化测试不同开仓手续费和资金费率")
        deal_num = 100000000
        warnings.simplefilter("ignore", ResourceWarning)

        for i in range(50):
            charge = int(random.uniform(0.01, 0.99) * 100) / 100
            cost = int(random.uniform(0.01, 0.99) * 100) / 100
            # print("charge", charge)
            # print("cost", cost)
            # 更新用户开仓手续费和资金费率
            ConnectMysql(_type=mysql_type).update_user_charge(user_mail=self.buyer, sda_id=sda_id, charge=charge,
                                                              cost=cost)

            # 查询当前股价
            stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
            now_stock_price = int(stock_price_dict["stockPrice"])
            stock_unit = int(stock_price_dict["tradeUnit"])

            deal_price = int(int(now_stock_price) * 0.95)

            # 查询交易前用户余额
            before_buy_info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
            before_buy_balance = int(before_buy_info_dict["balance"])

            # 下一单多单、空单，完全成交
            buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                        order_type=多单,
                                                                                                        order_price_type=限价,
                                                                                                        lever=lever,
                                                                                                        order_price=deal_price,
                                                                                                        order_num=deal_num))
            buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
                self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
            ))
            # time.sleep(3)
            sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                              order_type=空单,
                                                                                                              order_price_type=限价,
                                                                                                              lever=lever,
                                                                                                              order_price=deal_price,
                                                                                                              order_num=deal_num))
            sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
                self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
            ))

            time.sleep(1)
            # 第三个用户下多单
            three_resp = self.three_session.post(url=base+sda_order_create_url,
                                                 data=get_sda_order_create_param(sda_id=sda_id,
                                                                                 order_type=多单,
                                                                                 order_price_type=限价,
                                                                                 lever=lever,
                                                                                 order_price=deal_price,
                                                                                 order_num=deal_num))
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(self.three_user,
                                                                         sda_order_create_url, three_resp.status_code,
                                                                         three_resp.json()))

            # 买方做平多单于多单成交
            close_buy_resp = self.session.post(url=base+sda_order_create_url,
                                               data=get_sda_order_create_param(sda_id=sda_id,
                                                                               order_type=平多,
                                                                               order_price_type=限价,
                                                                               order_price=deal_price,
                                                                               order_num=deal_num))
            logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(self.buyer,
                                                                         sda_order_create_url,
                                                                         close_buy_resp.status_code,
                                                                         close_buy_resp.json()))
            sync_key = JMESPathExtractor().extract(query="syncLockKey", body=close_buy_resp.text)

            buy_info_resp = account_info_sync(user=self.buyer, session=self.session, sda_id=sda_id, sync_id=sync_key)
            after_buy_balance = int(buy_info_resp["balance"])
            buy_open_cost = openStockCost(price=deal_price, count=deal_num, stockPrice=now_stock_price, doMore=True,
                                          unit=stock_unit)
            buy_close_cost = openStockCost(price=deal_price, count=deal_num, stockPrice=now_stock_price, doMore=False,
                                           unit=stock_unit)
            # print("after buy balance :", after_buy_balance)
            assert before_buy_balance, after_buy_balance + int(buy_open_cost + buy_close_cost)

    def test_02(self):
        """
        0费率账户多单测试
        :return:
        """
        lever = 10
        logger.info("用例编号：130-2---0费率账户多单测试")
        deal_num = 100000000
        warnings.simplefilter("ignore", ResourceWarning)

        # charge = int(random.uniform(0.01, 0.99) * 100) / 100
        # cost = int(random.uniform(0.01, 0.99) * 100) / 100
        charge = 0
        cost = 0
        # 更新用户开仓手续费和资金费率
        ConnectMysql(_type=mysql_type).update_user_charge(user_mail=self.buyer, sda_id=sda_id, charge=charge, cost=cost)

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(stock_price_dict["stockPrice"])
        stock_unit = int(stock_price_dict["tradeUnit"])

        deal_price = int(int(now_stock_price) * 0.95)

        # 查询交易前用户余额
        before_buy_info_dict = account_info(user=self.buyer, session=self.session, sda_id=sda_id)
        before_buy_balance = int(before_buy_info_dict["balance"])

        # 下一单多单、空单，完全成交
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                    order_type=多单,
                                                                                                    order_price_type=限价,
                                                                                                    lever=lever,
                                                                                                    order_price=deal_price,
                                                                                                    order_num=deal_num))
        buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))
        # time.sleep(3)
        sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                          order_type=空单,
                                                                                                          order_price_type=限价,
                                                                                                          lever=lever,
                                                                                                          order_price=deal_price,
                                                                                                          order_num=deal_num))
        sell_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=sell_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
            self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
        ))

        time.sleep(1)

        # 第三个用户下多单
        three_resp = self.three_session.post(url=base+sda_order_create_url,
                                             data=get_sda_order_create_param(sda_id=sda_id,
                                                                             order_type=多单,
                                                                             order_price_type=限价,
                                                                             lever=lever,
                                                                             order_price=deal_price,
                                                                             order_num=deal_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(self.three_user,
                                                                     sda_order_create_url, three_resp.status_code,
                                                                     three_resp.json()))

        # 买方做平多单于多单成交
        close_buy_resp = self.session.post(url=base+sda_order_create_url,
                                           data=get_sda_order_create_param(sda_id=sda_id,
                                                                           order_type=平多,
                                                                           order_price_type=限价,
                                                                           order_price=deal_price,
                                                                           order_num=deal_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(self.buyer,
                                                                     sda_order_create_url,
                                                                     close_buy_resp.status_code,
                                                                     close_buy_resp.json()))
        sync_key = JMESPathExtractor().extract(query="syncLockKey", body=close_buy_resp.text)

        buy_info_resp = account_info_sync(user=self.buyer, session=self.session, sda_id=sda_id, sync_id=sync_key)
        after_buy_balance = int(buy_info_resp["balance"])
        buy_open_cost = openStockCost(price=deal_price, count=deal_num, stockPrice=now_stock_price, doMore=True,
                                      unit=stock_unit)
        buy_close_cost = openStockCost(price=deal_price, count=deal_num, stockPrice=now_stock_price, doMore=False,
                                       unit=stock_unit)
        assert before_buy_balance, after_buy_balance + int(buy_open_cost + buy_close_cost)

    def test_03(self):
        """
        0费率账户空单测试
        :return:
        """
        lever = 10
        logger.info("用例编号：130-3---0费率账户空单测试，验证对手单的余额、手续费")
        deal_num = 100000000
        warnings.simplefilter("ignore", ResourceWarning)

        # charge = int(random.uniform(0.01, 0.99) * 100) / 100
        # cost = int(random.uniform(0.01, 0.99) * 100) / 100
        charge = 0
        cost = 0
        # 更新用户开仓手续费和资金费率
        ConnectMysql(_type=mysql_type).update_user_charge(user_mail=self.buyer, sda_id=sda_id, charge=charge, cost=cost)

        # 查询当前股价
        stock_price_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(stock_price_dict["stockPrice"])
        stock_unit = int(stock_price_dict["tradeUnit"])

        deal_price = int(int(now_stock_price) * 0.95)

        # 查询交易前用户余额

        before_sell_info_dict = account_info(user=self.seller, sda_id=sda_id, session=self.sell_session)
        before_sell_balance = int(before_sell_info_dict["balance"])

        # 下一单多单、空单，完全成交
        buy_resp = self.session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                    order_type=空单,
                                                                                                    order_price_type=限价,
                                                                                                    lever=lever,
                                                                                                    order_price=deal_price,
                                                                                                    order_num=deal_num))
        buy_sync_id = JMESPathExtractor().extract(query="syncLockKey", body=buy_resp.text)
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(
            self.buyer, sda_order_create_url, buy_resp.status_code, buy_resp.json()
        ))
        # time.sleep(3)
        sell_resp = self.sell_session.post(url=base+sda_order_create_url, data=get_sda_order_create_param(sda_id=sda_id,
                                                                                                          order_type=多单,
                                                                                                          order_price_type=限价,
                                                                                                          lever=lever,
                                                                                                          order_price=deal_price,
                                                                                                          order_num=deal_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：空单--返回信息：{3}".format(
            self.seller, sda_order_create_url, sell_resp.status_code, sell_resp.json()
        ))

        time.sleep(1)
        # 第三个用户下多单
        three_resp = self.three_session.post(url=base+sda_order_create_url,
                                             data=get_sda_order_create_param(sda_id=sda_id,
                                                                             order_type=多单,
                                                                             order_price_type=限价,
                                                                             lever=lever,
                                                                             order_price=deal_price,
                                                                             order_num=deal_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(self.three_user,
                                                                     sda_order_create_url, three_resp.status_code,
                                                                     three_resp.json()))

        # 卖方做平多单于多单成交
        close_buy_resp = self.sell_session.post(url=base+sda_order_create_url,
                                           data=get_sda_order_create_param(sda_id=sda_id,
                                                                           order_type=平多,
                                                                           order_price_type=限价,
                                                                           order_price=deal_price,
                                                                           order_num=deal_num))
        logger.info("用户：{0}--接口：{1}--状态：{2}--类型：多单--返回信息：{3}".format(self.seller,
                                                                     sda_order_create_url,
                                                                     close_buy_resp.status_code,
                                                                     close_buy_resp.json()))
        sync_key = JMESPathExtractor().extract(query="syncLockKey", body=close_buy_resp.text)

        after_sell_info_dict = account_info(user=self.seller, session=self.sell_session, sda_id=sda_id, sync_id=sync_key)
        after_sell_balance = int(after_sell_info_dict["balance"])

        # 计算开仓手续费
        open_cost = openStockCost(price=deal_price, count=deal_num, doMore=True, unit=stock_unit,
                                  stockPrice=now_stock_price)

        # 计算平仓手续费
        close_cost = openStockCost(price=deal_price, count=deal_num, doMore=False, unit=stock_unit,
                                   stockPrice=now_stock_price)

        assert before_sell_balance, after_sell_balance + int(open_cost + close_cost)


if __name__ == '__main__':
    unittest.main()

