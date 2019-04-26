import Account
import AccountUtil


def run(account, buyNum, buyPrice, orderTotalNum, orderFreezeBalance, unit, lever, stockPrice):
    # 需撤销委托冻结
    buyFreezeBalanceT = account.saFreezeBalance
    buyNumT = account.saFreezeNum
    if ((account.saFreezeNum - buyNum) > 0):
        buyFreezeBalanceT = buyNum / orderTotalNum * orderFreezeBalance
        buyNumT = buyNum
    saFreezeBalance = account.saFreezeBalance - buyFreezeBalanceT
    saFreezeNum = account.saFreezeNum - buyNumT

    # 本次成交的仓位保证金
    saEmployBalance = AccountUtil.employBalance(buyPrice, buyNum, unit, lever)
    saHoldTotalPrice = AccountUtil.holdTotalPrice(account.saHoldTotalPrice, buyPrice, buyNum)
    # 开仓手续费公式
    doMore = False
    if (account.saAccountType == 1):
        doMore = True
    # 开仓手续费
    openStockCost = AccountUtil.openStockCost(buyPrice, buyNum, doMore, unit, stockPrice)
    saHoldNum = account.saHoldNum + buyNum
    saHoldAveragePrice = AccountUtil.holdAvgPrice(saHoldTotalPrice, saHoldNum)
    saCanSellNum = account.saCanSellNum + buyNum
    saBalance = account.saBalance + buyFreezeBalanceT - saEmployBalance
    # 计算爆仓价的余额
    calcCashBalace = saBalance + account.saPlatformFreezeBalance + saFreezeBalance + saEmployBalance + account.saEmployBalance - openStockCost
    # 爆仓公式
    saCrashPrice = AccountUtil.crashPrice(saHoldAveragePrice, calcCashBalace, saHoldNum, unit, doMore)
    # 爆仓后平台挂单价公式
    saPlatformPutPrice = AccountUtil.crashPutPrice(saHoldAveragePrice, calcCashBalace, saHoldNum, unit, doMore)
    # 持仓手续费
    saHoldCharge = account.saHoldCharge + openStockCost

    # 组装返回数据
    account.saFreezeBalance = saFreezeBalance
    account.saFreezeNum = saFreezeNum
    account.saEmployBalance = account.saEmployBalance + saEmployBalance
    account.saHoldAveragePrice = saHoldAveragePrice
    account.saHoldTotalPrice = saHoldTotalPrice
    account.saHoldNum = saHoldNum
    account.saCanSellNum = saCanSellNum
    account.saCrashPrice = saCrashPrice
    account.saPlatformPutPrice = saPlatformPutPrice
    account.saBalance = saBalance
    account.saHoldCharge = saHoldCharge
    return account


if __name__ == '__main__':
    account = Account.init()
    account.saBalance = 10000000
    account.saAccountType = 1
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
    run(account, 3, 3, 10, 500000000, 0.01, 1, 1)
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
