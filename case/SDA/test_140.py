import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import MytestOnePlayer
from common.connectMysql import ConnectMysql
from common._mytest import sda_account_withdraw
from common.connectRedis import ConnectRedis
from common._mytest import sda_order_create
from common._mytest import sda_fund_balance
from common._mytest import query_account_position_get
from common.AccountTest.AccountUtil import positions_value
from common.AccountTest.AccountUtil import open_positions_value
from common._mytest import assert_list
from common._mytest import MyTestOn
from common._mytest import set_stock_price
from common._mytest import assert_one
from common.params import *
from common.logger import logger
from common._mytest import market_info_get
from common.jsonparser import JMESPathExtractor
from common._mytest import account_info
from common._mytest import account_info_sync
import time

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_create_url = names.sda_order_create_url
sda_order_get_open_url = names.sda_order_get_open_url
sda_order_cancel_url = names.sda_order_cancel_url
positions_url = names.sda_account_positions_get_url

sda_get_url = names.sda_get_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url
sda_account_positions_get_url = names.sda_account_positions_get_url

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan


class TestCase(MytestOnePlayer):
    """
    转出测试类
    """
    def test_01(self):
        """
        转出清除赠金测试
        :return:
        """
        logger.info("用例编号：140-1----把用户转入的钱全部转出，赠金清除为0")
        balance = 30*100000000
        sda_balance = 30*100000000
        ConnectMysql(_type=mysql_type).sda_update_user_platform_freeze_balance(user_mail=self.buyer, sda_id=sda_id,
                                                                               balance=balance)
        # 更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=sda_balance)

        time.sleep(0.2)
        withdraw_dict = sda_account_withdraw(user=self.buyer, session=self.session, sda_id=sda_id, amount=balance)
        sync_id = JMESPathExtractor().extract(query="syncLockKey", body=withdraw_dict.text)
        account_info_dict = account_info_sync(sync_id=sync_id, user=self.buyer, session=self.session, sda_id=sda_id)
        flag = assert_one(int(account_info_dict["balance"]), 0)
        self.assertEqual(flag, True)

    def test_02(self):
        """
        有委托的情况下禁止转出余额
        :return:
        """
        logger.info("用例编号：140-2---有委托的情况下禁止转出")
        info_dict = market_info_get(user=self.buyer, session=self.session, sda_id=sda_id)
        now_stock_price = int(info_dict["stockPrice"])
        deal_num = 1*100000000
        balance = 30*100000000
        sda_balance = 30*100000000
        ConnectMysql(_type=mysql_type).sda_update_user_platform_freeze_balance(user_mail=self.buyer, sda_id=sda_id,
                                                                               balance=balance)
        # 更新可用余额
        ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=self.user_id, keys=sda_id)
        ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=self.user_id, sda_id=sda_id)
        ConnectMysql(_type=mysql_type).sda_update_user_balance(user_id=self.user_id, sda_id=sda_id,
                                                               sda_balance=sda_balance)

        time.sleep(0.2)
        # 下委托
        sda_order_create(user=self.buyer, session=self.session,sda_id=sda_id, order_type=多单,order_price_type=限价,
                         order_price=now_stock_price, order_num=deal_num)
        fund_balance_dict = sda_fund_balance(user=self.buyer, session=self.session, sda_id=sda_id)

        time.sleep(0.2)
        flag = assert_one(int(fund_balance_dict["withdrawMargin"]), 0)
        self.assertEqual(flag, True)


if __name__ == '__main__':
    unittest.main()
