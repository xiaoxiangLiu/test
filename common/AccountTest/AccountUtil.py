import math


class AccountUtil(object):
    pass


SDA_FUNDING_COST_RATE = 0.01
SDA_DEAL_CHARGE_RATE = 0.002
SDA_ACCOUNT_CRASH_LINE_RATE = 0.7
SDA_ACCOUNT_CRASH_REMIND_LINE_RATE = 0.6
UNIT = 100000000


# 资金费用=【（现货指数价-开仓价） /现货指数价】 *1%*（成交价*成交量*交易单位）
def fundingCost(price, count, doMore, stockPrice, unit, cost=SDA_FUNDING_COST_RATE):
    currBig = price > stockPrice
    result = abs(price - stockPrice) / stockPrice * cost * price / UNIT * count / UNIT * unit / UNIT
    # _result = -result if
    # if currBig or doMore:
    #    return -result * UNIT
    # elif currBig and doMore:
    #    print(result * UNIT)
    #    return result * UNIT

    # if doMore:
    #    if currBig:
    #        return -result * UNIT
    #    else:
    #        return result * UNIT
    # else:
    #    if currBig:
    #        return -result * UNIT
    #    else:
    #        return result * UNIT

    if (currBig & doMore) | (not (currBig | doMore)):
        return result * UNIT
    else:
        return -result * UNIT


# 交易手续费=平仓价格*平仓数量*交易单位*交易平仓手续费率
def dealFee(price, count, unit, charge=SDA_DEAL_CHARGE_RATE):
    result = price * count / UNIT * unit / UNIT * charge
    return result


# 开仓手续费=平仓手续费=交易手续费＋资金费用
def openStockCost(price, count, doMore, unit, stockPrice):
    return int(dealFee(price, count, unit) + fundingCost(price, count, doMore, stockPrice, unit))


# 可开仓余额=余额+平台锁定余额
def canOpenStockBalance(balance, platformFreezeBalance):
    return balance + platformFreezeBalance


# 可开张数=（可用保证金*杠杆倍数）/（开仓价*交易单位）
def canOpenStockCount(balance, price, unit, lever):
    return balance * lever / price * UNIT / unit * UNIT


# 持仓总价公式
def holdTotalPrice(holdTotalPrice, dealPrice, dealCount):
    return holdTotalPrice + dealPrice * dealCount / UNIT


# 持仓均价公式
def holdAvgPrice(holdTotalPrice, holdCount):
    return holdTotalPrice * UNIT / holdCount


# 仓位价值=委托价值=仓位数量*价格*交易单位
def stockValue(price, count, unit):
    return int(price * count) / UNIT * unit / UNIT


# 仓位保证金=委托保证金=仓位价值/杠杆倍数
def employBalance(price, count, unit, lever):
    return stockValue(price, count, unit) / lever


# 爆仓价=持仓均价+—70%保证金/（持仓数量*交易单位）
def crashPrice(holdAvgPrice, totalBalance, holdCount, unit, doMore):
    if (holdCount < 1):
        return 0
    tPrice = int(totalBalance * SDA_ACCOUNT_CRASH_LINE_RATE / holdCount * UNIT / unit * UNIT)
    if (doMore):
        return int(holdAvgPrice - tPrice)
    else:
        return int(holdAvgPrice + tPrice)


# 爆仓挂单价=持仓均价+—保证金/（持仓数量*交易单位）
def crashPutPrice(holdAvgPrice, totalBalance, holdCount, unit, doMore):
    if (holdCount < 1):
        return 0
    tPrice = totalBalance * 1 / holdCount * UNIT / unit * UNIT
    if (doMore):
        return holdAvgPrice - tPrice
    else:
        return holdAvgPrice + tPrice


# 爆仓提醒价=持仓均价+—60%保证金/（持仓数量*交易单位）
def crashRemindPrice(holdAvgPrice, totalBalance, holdCount, unit, doMore):
    if (holdCount < 1):
        return 0
    tPrice = totalBalance * SDA_ACCOUNT_CRASH_REMIND_LINE_RATE / holdCount * UNIT / unit * UNIT
    if (doMore):
        return holdAvgPrice - tPrice
    else:
        return holdAvgPrice + tPrice


# 未实现盈亏=持仓数量*（最新成交价—持仓均价）*交易单位-持仓手续费
def unRealLoss(holdAvgPrice, count, unit, doMore, holdCharge, stock_price):
    def cutPrice():
        if (doMore):
            return stock_price - holdAvgPrice
        else:
            return holdAvgPrice - stock_price

    return cutPrice() * count / UNIT * unit / UNIT - holdCharge


# 未实现盈亏率=（当前市价—开仓均价）/开仓均价
def unRealLossRate(holdAvgPrice, doMore, sdaLastPrice):
    def cutPrice():
        if (doMore):
            return sdaLastPrice - holdAvgPrice
        else:
            return holdAvgPrice - sdaLastPrice

    return cutPrice() / holdAvgPrice


# 已实现盈亏=平仓数量*（平仓价格—开仓价格）*交易单位＋ 平仓手续费
def realLoss(price, count, holdAvgPrice, doMore, unit, closeStockCost):
    def cutPrice():
        if (doMore):
            return price - holdAvgPrice
        else:
            return holdAvgPrice - price

    makeMoney = count * cutPrice() / UNIT * unit / UNIT
    return makeMoney - closeStockCost


# 单个SDA合约账户权益=可用保证金+占用保证金+冻结保证金+未实现盈亏
def accountWorth(totalBalance, holdAvgPrice, holdCount, unit, doMore, sdaLastPrice, holdCharge):
    return totalBalance + unRealLoss(holdAvgPrice, holdCount, unit, doMore, holdCharge, sdaLastPrice)


# 账户风险率=账户权益/仓位保证金*100%
def riskRate(accountWorth, employBalance):
    return accountWorth / employBalance

# 开仓价值=开仓均价*仓位数量*交易单位
def open_positions_value(hold_price, hold_num, trade_unit):
    """
    开仓价值计算
    :param hold_price:开仓均价
    :param hold_num: 开仓数量
    :param trade_unit: 交易单位
    :return: 开仓价值
    """
    return hold_price/UNIT*hold_num/UNIT*trade_unit


def positions_value(stock_price, hold_num, trade_unit):
    """
    持仓价值计算
    :param stock_price: 指数价
    :param hold_num: 持仓数量
    :param trade_unit: 交易单位
    :return: 持仓价值
    """
    return stock_price/UNIT*hold_num/UNIT*trade_unit


if __name__ == '__main__':
    print(stockValue(price=100*100000000, count=90000000000*100000000, unit=100000000))
    # print(fundingCost(price=100*100000000, count=100*100000000, doMore=True, stockPrice=18.11, unit=1))
    # #
    # # print(employBalance(price=100*100000000, count=100*100000000, unit=1, lever=1))
    # # print(stockValue(price=100*UNIT, count=100*UNIT, unit=1))
    # # print(riskRate(accountWorth=100*UNIT, employBalance=10*UNIT))
    # # print('Hello World')
    # # print(abs(-12))
    # # print(fundingCost(1, 2, True, 3, 1))
    # # print(dealFee(1, 2, 1))
