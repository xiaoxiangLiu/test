__author__ = '123'
# coding=utf-8
from common.logger import logger
from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
from common.names import names
import re

base_url = names.url_123
base_50_url = names.url_50



def count_balance(free_type, deal_price, deal_num, **kwargs):
    """
    计算用户余额在交易、撤单后是否符合计算规则
    :param free_type: 免除手续费类型，接受四个参数：buy_free，买方免除手续费，sell_free，卖方免除手续费，all_free，买卖都免除手续费，no_free，买卖方都不免除手续费
    :param deal_price: 交易单价
    :param deal_num: 交易数量
    :param value_list: 交易前后的买卖方的余额，类型：dict，
    示例:buy_dict = {"before_buy_main_balance": 1000000, "before_buy_target_balance": 5000000,
                "before_sell_main_balance": 1000000, "before_sell_target_balance": 5000000,
                "after_buy_main_balance": 2000000, "after_bue_target_balance": 3000000,
                "after_sell_main_balance": 2000000,"after_sell_target_balance": 3000000}
    :return:
    """

    before_buy_main_balance, before_buy_target_balance = 0, 0
    after_buy_main_balance, after_buy_target_balance = 0, 0
    before_sell_main_balance, before_sell_target_balance = 0, 0
    after_sell_main_balance, after_sell_target_balance = 0, 0
    deal_value = int(deal_price) * int(deal_num)

    for k, v in kwargs.items():
        if k == "before_buy_main_balance":
            before_buy_main_balance = v
        elif k == "before_buy_target_balance":
            before_buy_target_balance = v
        elif k == "after_buy_main_balance":
            after_buy_main_balance = v
        elif k == "after_buy_target_balance":
            after_buy_target_balance = v
        elif k == "before_sell_main_balance":
            before_sell_main_balance = v
        elif k == "before_sell_target_balance":
            before_sell_target_balance = v
        elif k == "after_sell_main_balance":
            after_sell_main_balance = v
        elif k == "after_sell_target_balance":
            after_sell_target_balance = v

    if free_type == "buy_free":  # 买方为市商，买方购入不出手续费
        buy_main_balance_flag = False
        buy_target_balance_flag = False
        sell_main_balance_flag = False
        sell_target_balance_flag = False
        if int(before_buy_main_balance) - int(after_buy_main_balance) - int(deal_value/100000000) in [0 ,1]:
            buy_main_balance_flag = True
        else:
            buy_main_balance_flag = False

        if int(after_buy_target_balance) - int(before_buy_target_balance) - int(deal_num) in [0, 1]:
            buy_target_balance_flag = True
        else:
            buy_target_balance_flag = False

        if int(after_sell_main_balance) - int(before_sell_main_balance) - int(deal_value/100000000 * (1-2/1000)) in [0, 1]:
            sell_main_balance_flag = True
        else:
            sell_main_balance_flag = False

        if int(before_sell_target_balance) - int(after_sell_target_balance) - int(deal_num) in [0, 1]:
            sell_target_balance_flag = True
        else:
            sell_target_balance_flag = False
        logger.info("买家主币断言结果：{0}".format(buy_main_balance_flag))
        logger.info("买家目标币断言结果：{0}".format(buy_target_balance_flag))
        logger.info("卖家主币断言结果：{0}".format(sell_main_balance_flag))
        logger.info("卖家目标币断言结果：{0}".format(sell_target_balance_flag))
        return buy_main_balance_flag, buy_target_balance_flag, sell_main_balance_flag, sell_target_balance_flag
    elif free_type == "sell_free":  # 卖方为市商，卖方不出手续费
        buy_main_balance_flag = False
        buy_target_balance_flag = False
        sell_main_balance_flag = False
        sell_target_balance_flag = False
        if int(before_buy_main_balance) - int(after_buy_main_balance) - int(deal_value/100000000) in [0, 1]:
            buy_main_balance_flag = True
        else:
            buy_main_balance_flag = False

        if int(after_buy_target_balance) - int(before_buy_target_balance) - int(deal_num * (1-2/1000)) in [0, 1]:
            buy_target_balance_flag = True
        else:
            buy_target_balance_flag = False

        if int(after_sell_main_balance) - int(before_sell_main_balance) - int(deal_value/100000000) in [-1, 0]:
            sell_main_balance_flag = True
        else:
            sell_main_balance_flag = False

        if int(before_sell_target_balance) - int(after_sell_target_balance) - int(deal_num) in [0, 1]:
            sell_target_balance_flag = True
        else:
            sell_target_balance_flag = False
        logger.info("买家主币断言结果：{0}".format(buy_main_balance_flag))
        logger.info("买家目标币断言结果：{0}".format(buy_target_balance_flag))
        logger.info("卖家主币断言结果：{0}".format(sell_main_balance_flag))
        logger.info("卖家目标币断言结果：{0}".format(sell_target_balance_flag))
        return buy_main_balance_flag, buy_target_balance_flag, sell_main_balance_flag, sell_target_balance_flag

    elif free_type == "all_free":  # 买方、卖方均为市商，都不收取手续费
        buy_main_balance_flag = False
        buy_target_balance_flag = False
        sell_main_balance_flag = False
        sell_target_balance_flag = False
        if int(before_buy_main_balance) - int(after_buy_main_balance) - int(deal_value/100000000) in [0 ,1]:
            buy_main_balance_flag = True
        else:
            buy_main_balance_flag = False

        if int(after_buy_target_balance) - int(before_buy_target_balance) - int(deal_num) in [0, 1]:
            buy_target_balance_flag = True
        else:
            buy_target_balance_flag = False

        if int(after_sell_main_balance) - int(before_sell_main_balance) - int(deal_value/100000000) in [0 ,1]:
            sell_main_balance_flag = True
        else:
            sell_main_balance_flag = False

        if int(before_sell_target_balance) - int(after_sell_target_balance) - int(deal_num) in [0, 1]:
            sell_target_balance_flag = True
        else:
            sell_target_balance_flag = False
        logger.info("买家主币断言结果：{0}".format(buy_main_balance_flag))
        logger.info("买家目标币断言结果：{0}".format(buy_target_balance_flag))
        logger.info("卖家主币断言结果：{0}".format(sell_main_balance_flag))
        logger.info("卖家目标币断言结果：{0}".format(sell_target_balance_flag))
        return buy_main_balance_flag, buy_target_balance_flag, sell_main_balance_flag, sell_target_balance_flag

    elif free_type == "no_free":  # 买卖方均不是市商，都收取手续费
        buy_main_balance_flag = False
        buy_target_balance_flag = False
        sell_main_balance_flag = False
        sell_target_balance_flag = False
        if int(before_buy_main_balance) - int(after_buy_main_balance) - int(deal_value/100000000) in [0, 1]:
            buy_main_balance_flag = True

        if int(after_buy_target_balance) - int(before_buy_target_balance) - int(deal_num * (1-2/1000)) in [0, 1]:
            buy_target_balance_flag = True

        if int(after_sell_main_balance) - int(before_sell_main_balance) - int(deal_value/100000000 * (1-2/1000)) in [0, 1]:
            sell_main_balance_flag = True

        if int(before_sell_target_balance) - int(after_sell_target_balance) - int(deal_num) in [0, 1]:
            sell_target_balance_flag = True

        logger.info("买家主币断言结果：{0}".format(buy_main_balance_flag))
        logger.info("买家目标币断言结果：{0}".format(buy_target_balance_flag))
        logger.info("卖家主币断言结果：{0}".format(sell_main_balance_flag))
        logger.info("卖家目标币断言结果：{0}".format(sell_target_balance_flag))
        return buy_main_balance_flag, buy_target_balance_flag, sell_main_balance_flag, sell_target_balance_flag


def get_redis_name(transtion_id):
    """
    根据transtion_id返回redis name list
    :param transtion_id: 交易对ID
    :return:redis name list
    """
    name_list = [str(transtion_id) + "buy", str(transtion_id) + "sell"]
    return name_list


def init_environment():
    base_url = names.url_50
    mysql_url = 2
    redis_url = names.redis_type_50
    return base_url, mysql_url, redis_url


def init_environment_123():
    base_url = names.url_123
    mysql_url = names.mysql_type_54
    redis_url = names.redis_type_123
    return base_url, mysql_url, redis_url


def init_environment_252():
    base_url = names.url_253
    mysql_url = 5
    redis_url = names.redis_type_253
    sda_id = "81"
    return base_url, mysql_url, redis_url, sda_id


def init_environment_213():
    base_url = names.url_252
    mysql_url = 6
    redis_url = names.redis_type_252
    sda_id = "81"
    return base_url, mysql_url, redis_url, sda_id


def init_environment_otc():
    """
    otc 测试切换环境使用
    :return:
    """
    login_url = "http://192.168.1.253:8080/dididu"
    base_url = "http://192.168.1.253:18090"
    mysql_url = 5
    redis_url = names.redis_type_253
    return login_url, base_url, mysql_url, redis_url


def inti_environment_partner():
    """
    代理商系统切换环境使用
    :return:
    """
    mysql_type = 2
    base_url = names.url_partner
    redis_type = names.redis_type_253
    return base_url, mysql_type, redis_type


def init_environment_253():
    base_url = names.url_253
    mysql_url = 5
    redis_url = names.redis_type_253
    sda_id = "81"
    return base_url, mysql_url, redis_url, sda_id


def mySetUp(transtion_id, mysql_type, redis_type, buyer, seller, balance_value):
    """
    将DB中指定的交易对的买卖单更新为状态1，将redis中的指定交易对的key删除，为用户更新此交易对的主币和目标币的balance_value
    :param transtion_id:
    :param mysql_type:
    :param redis_type:
    :param buyer:
    :param seller:
    :param balance_value:
    """
    main_currency_id, target_currency_id = ConnectMysql(_type=mysql_type).query_main_target_currency(transtion_id=transtion_id)
    ConnectRedis(_type=redis_type).clear_redis(get_redis_name(transtion_id=transtion_id))
    ConnectMysql(_type=mysql_type).update_order_status(transtion_id, order_type=1, order_status=1)
    ConnectMysql(_type=mysql_type).update_order_status(transtion_id, order_type=2, order_status=1)
    ConnectMysql(_type=mysql_type).update_balance_value(user_mail=buyer, currency_id=main_currency_id, balance_value=balance_value)
    ConnectMysql(_type=mysql_type).update_balance_value(user_mail=buyer, currency_id=target_currency_id, balance_value=balance_value)
    ConnectMysql(_type=mysql_type).update_balance_value(user_mail=seller, currency_id=main_currency_id, balance_value=balance_value)
    ConnectMysql(_type=mysql_type).update_balance_value(user_mail=seller, currency_id=target_currency_id, balance_value=balance_value)


def transform_freezing_assets(num):
    """
    转换科学记数法到整数
    :param num: 接受科学记数法的Num
    :return:输出整数类型的整数
    """
    x = "{:.14f}".format(float(num))
    b = re.search(".\d*", x).group()
    return int(b)

if __name__ == '__main__':
    s = "2.082499739973E13"
    print(type(transform_freezing_assets(s)))
    """
    buy_dict = {"before_buy_main_balance": 990000000000000, "before_buy_target_balance": 990000000000000,
                "before_sell_main_balance": 990000000000000, "before_sell_target_balance": 990000000000000,
                "after_buy_main_balance": 989999999999500, "after_buy_target_balance": 990004990000000,
                "after_sell_main_balance": 990000000000499, "after_sell_target_balance": 989995000000000}
    print(count_balance(free_type=4, deal_price=10, deal_num=5000000000, **buy_dict))
    """