__author__ = '123'
# coding=utf-8
from common.logger import logger
from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
from common.base import Base
from common.tools import init_environment

base_url, mysql_type, redis_type = init_environment()



def update_test_status():

    pass

def query_user_balance_value(buyer, seller, main_currency_id, target_currency_id, transaction_id=None, order_id=None):
    """
    查询买卖方的主币、目标币余额
    :param buyer: 可以填入用户登陆名
    :param seller: 可以填入用户登陆名
    :param main_currency_id: 主币id
    :param target_currency_id: 目标币id
    """
    test_buyer = Base(user=buyer)
    test_buyer_id = test_buyer.user_id
    buyer_main_balance_value = test_buyer.get_user_balance_servlet(currency_id=main_currency_id, transaction_id=transaction_id, order_id=order_id)
    buyer_deputy_balance_value = test_buyer.get_user_balance_servlet(currency_id=target_currency_id, transaction_id=transaction_id, order_id=order_id)
    test_buyer.close()
    test_seller = Base(user=seller)
    test_seller_id = test_seller.user_id
    seller_main_balance_value = test_seller.get_user_balance_servlet(currency_id=main_currency_id, transaction_id=transaction_id, order_id=order_id)
    seller_deputy_balance_value = test_seller.get_user_balance_servlet(currency_id=target_currency_id, transaction_id=transaction_id, order_id=order_id)
    test_seller.close()
    logger.info("- - - - - - - - - - - - - - - - - - - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    logger.info(" 通过接口查询--{0}---买家主币余额：{1}-----买家目标币余额：{2}".format(buyer, buyer_main_balance_value, buyer_deputy_balance_value))
    logger.info(" 通过接口查询--{0}---卖家主币余额：{1}-----卖家家目标币余额：{2}".format(seller, seller_main_balance_value, seller_deputy_balance_value))

    buy_mysql_main_value = ConnectMysql(_type=mysql_type).get_user_balance_data(user_mail=buyer, currency_id=main_currency_id)
    buy_mysql_target_value = ConnectMysql(_type=mysql_type).get_user_balance_data(user_mail=buyer, currency_id=target_currency_id)
    sell_mysql_main_value = ConnectMysql(_type=mysql_type).get_user_balance_data(user_mail=seller, currency_id=main_currency_id)
    sell_mysql_target_value = ConnectMysql(_type=mysql_type).get_user_balance_data(user_mail=seller, currency_id=target_currency_id)
    logger.info("- - - - - - - - - - - - - - - - - - - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    logger.info("通过数据库查询--{0}---买家主币余额：{1}-----买家目标币余额：{2}".format(buyer, buy_mysql_main_value, buy_mysql_target_value))
    logger.info("通过数据库查询--{0}---卖家主币余额：{1}-----卖家目标币余额：{2}".format(seller, sell_mysql_main_value, sell_mysql_target_value))

    buy_redis_main_value = ConnectRedis(_type=redis_type, db=5).get_user_balance(user_id=test_buyer_id, currency_id=main_currency_id)
    buy_redis_target_value = ConnectRedis(_type=redis_type, db=5).get_user_balance(user_id=test_buyer_id, currency_id=target_currency_id)
    sell_redis_main_value = ConnectRedis(_type=redis_type, db=5).get_user_balance(user_id=test_seller_id, currency_id=main_currency_id)
    sell_redis_target_value = ConnectRedis(_type=redis_type, db=5).get_user_balance(user_id=test_seller_id, currency_id=target_currency_id)
    logger.info("- - - - - - - - - - - - - - - - - - - - - - - - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    logger.info("通过redis查询--{0}---买家主币余额：{1}-----买家目标币余额：{2}".format(buyer, buy_redis_main_value, buy_redis_target_value))
    logger.info("通过redis查询--{0}---卖家主币余额：{1}-----卖家目标币余额：{2}".format(seller, sell_redis_main_value, sell_redis_target_value))

    return buyer_main_balance_value, buyer_deputy_balance_value, seller_main_balance_value, seller_deputy_balance_value

if __name__ == '__main__':
    print(query_user_balance_value(buyer="39@qq.com", seller="41@qq.com", main_currency_id=3, target_currency_id=13))