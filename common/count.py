__author__ = '123'
# coding=utf-8
from common.logger import logger

def count_value_buy_first(buy_price=None, buy_num=None, sell_price=None, sell_num=None):

    """
    多个买卖单计算余额公式，此方法计算先下N个买单，再下N个卖单的余额
    :param buy_price: List，所有买单的单价，按照下买单的顺序
    :param buy_num: list,所有买单的数量，按照下买单的顺序
    :param sell_price: List,所有卖单的单价，按照下卖单的顺序
    :param sell_num: list,所有卖单的数量，按照下卖单的顺序
    :return:buy_price，总买入金额，用户计算买家主币， deal_num，总成交数量，用于计算买家目标币，
            sell_price，总卖出金额，用于计算卖家主币，sell_num，卖出数量，用于计算卖家目标币
    """
    buy_value = []
    for i in range(len(buy_price)):
        buy_value.append(buy_price[i] * buy_num[i])

    deal_num = []
    buy_dict = dict(zip(buy_price, buy_num))
    sell_dict = dict(zip(sell_price, sell_num))
    key_list = []
    for k, v in buy_dict.items():
        key_list.append(k)
    key_list.sort(reverse=False)
    new_dict = {}
    for m in key_list:
        new_dict.update({m: buy_dict[m]})
    buy_index = 0
    buy_flag = len(buy_price) - 1
    sell_index = 0
    sell_flag = len(sell_price) - 1
    value = 0
    deal_price = []
    for _buy_price in reversed(key_list):
        if _buy_price >= sell_price[sell_index]:
            value = sell_num[sell_index] - new_dict[_buy_price]
            sell_index += 1
            if value >= 0:
                value = value - sell_num[sell_index]
            elif value < 0:
                deal_num.append(new_dict[_buy_price])
                deal_price.append(_buy_price)
    deal_value_list = []
    for i in deal_price:
        deal_value = i * new_dict[i]
        deal_value_list.append(deal_value)

    return [sum(buy_value), sum(deal_num), sum(deal_value_list), sum(sell_num)]

def count_value_sell_first(buy_price=None, buy_num=None, sell_price=None, sell_num=None):

    """
    多个买卖单计算余额公式，此方法计算先下N个卖单，再下N个买单的余额
    :param buy_price: List，所有买单的单价，按照下买单的顺序
    :param buy_num: list,所有买单的数量，按照下买单的顺序
    :param sell_price: List,所有卖单的单价，按照下卖单的顺序
    :param sell_num: list,所有卖单的数量，按照下卖单的顺序
    :return:buy_price，总买入金额，用户计算买家主币， deal_num，总成交数量，用于计算买家目标币，
            sell_price，总卖出金额，用于计算卖家主币，sell_num，卖出数量，用于计算卖家目标币
    """

    buy_value = []
    for i in range(len(buy_price)):
        buy_value.append(buy_price[i] * buy_num[i])

    buy_dict = dict(zip(buy_price, buy_num))
    sell_dict = dict(zip(sell_price, sell_num))
    key_list = []
    for k, v in buy_dict.items():
        key_list.append(k)
    key_list.sort(reverse=False)
    new_dict = {}
    for m in key_list:
        new_dict.update({m: buy_dict[m]})
    buy_index = 0
    buy_flag = len(buy_price) - 1
    sell_index = 0
    sell_flag = len(sell_price) - 1
    value = 0
    deal_price = []
    deal_num = []
    for _buy_price in key_list:
        if _buy_price >= sell_price[sell_index]:
            value = new_dict[_buy_price] - sell_num[sell_index]
            if value < 0:
                deal_num.append(new_dict[_buy_price])
                value = new_dict[key_list[buy_index]] - value
            elif value == 0:
                deal_num.append(sell_num[sell_index])
                value = new_dict[key_list[buy_index]] - sell_num[sell_index]
            elif value > 0:
                if new_dict[_buy_price] < sell_num[sell_index]:
                    deal_num.append(sell_num[sell_index])
                    value = new_dict[_buy_price] - sell_num[sell_index]
                elif new_dict[_buy_price] > sell_num[sell_index]:
                    deal_num.append(new_dict[_buy_price])
                    value = new_dict[_buy_price] - sell_num[sell_index]
            sell_index += 1
            buy_index += 1

    deal_value_list = []
    for i in deal_num:
        for k, v in new_dict.items():
            if v == i:
                deal_value_list.append(k * v)

    return [sum(buy_value), sum(deal_num), sum(deal_value_list), sum(sell_num)]

def count_value_single(buy_price, buy_num, sell_price, sell_num, **kwargs):
    """
    计算非多单成交余额，不
    :param buy_price:买单价格
    :param buy_num:买单数量
    :param sell_price:卖单价格
    :param sell_num:卖单数量
    :param kwargs:成交前后买方和卖方的两个币的余额组成的字典
    :return:List，分别是买家主币断言结果，买家目标币断言结果，卖家主币断言结果，卖家目标币断言结果
    """

    buy_main_balance_flag, buy_target_balance_flag, sell_main_balance_flag, sell_target_balance_flag = True, True, True, True

    before_buy_main_balance, before_buy_target_balance = 0, 0
    after_buy_main_balance, after_buy_target_balance = 0, 0
    before_sell_main_balance, before_sell_target_balance = 0, 0
    after_sell_main_balance, after_sell_target_balance = 0, 0
    deal_value, deal_num = 0, 0

    if buy_price >= sell_price and buy_num >= sell_num:
        deal_value = buy_price * sell_num
        deal_num = sell_num
    elif buy_price >= sell_price and buy_num < sell_num:
        deal_value = buy_price * buy_num
        deal_num = buy_num
    else:
        print("买单价格小于卖单价格不会成交")

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

    if int(after_buy_main_balance) - int(before_buy_main_balance) - int(deal_value/100000000) == 0 or 1:
        buy_main_balance_flag = True
    elif int(after_buy_main_balance) - int(before_buy_main_balance) - int(deal_value/100000000) != 0 or 1:
        buy_main_balance_flag = False

    if int(after_buy_target_balance) - int(before_buy_target_balance) + int(deal_num * (1-2/1000)) == 0 or 1:
        buy_target_balance_flag = True
    elif int(after_buy_target_balance) - int(before_buy_target_balance) + int(deal_num * (1-2/1000)) != 0 or 1:
        buy_target_balance_flag = False

    if int(after_sell_main_balance) - int(before_sell_main_balance) + int(deal_value/100000000 * (1-2/1000)) == 0 or 1:
        sell_main_balance_flag = True
    elif int(after_sell_main_balance) - int(before_sell_main_balance) + int(deal_value/100000000 * (1-2/1000)) != 0 or 1:
        sell_main_balance_flag = False

    if int(after_sell_target_balance) - int(before_sell_target_balance) - int(sell_num) == 0 or 1:
        sell_target_balance_flag = True
    elif int(after_sell_target_balance) - int(before_sell_target_balance) - int(sell_num) == 0 or 1:
        sell_target_balance_flag = False

    logger.info("买家主币断言结果：{0}".format(buy_main_balance_flag))
    logger.info("买家目标币断言结果：{0}".format(buy_target_balance_flag))
    logger.info("卖家主币断言结果：{0}".format(sell_main_balance_flag))
    logger.info("卖家目标币断言结果：{0}".format(sell_target_balance_flag))

    return buy_main_balance_flag, buy_target_balance_flag, sell_main_balance_flag, sell_target_balance_flag

if __name__ == '__main__':
    a, b, c, d, = count_value_sell_first(
        buy_price=[20000000000,25000000000,30000000000,35000000000,40000000000],
        buy_num=[100000000, 200000000, 300000000, 400000000, 600000000],
        sell_price=[20000000000,25000000000,30000000000,35000000000,40000000000],
        sell_num=[100000000, 200000000, 300000000, 400000000, 500000000],
    )
    print(a, b, c, d)

    """
    buy_dict = {"before_buy_main_balance": 9900000000000000, "before_buy_target_balance": 9900000000000000,
                "before_sell_main_balance": 9900000000000000, "before_sell_target_balance": 9900000000000000,
                "after_buy_main_balance": 9887036690640000, "after_buy_target_balance": 9982298872400000,
                "after_sell_main_balance": 9912937382741280, "after_sell_target_balance": 9817536200000000, }
    print(count_value_single(buy_price=15720000, buy_num=82463800000000, sell_price=15720000, sell_num=82463800000000, **buy_dict))
        """