import Account
import AccountUtil


def run(account, sellNum, sellPrice, unit, lever, stockPrice):
    saHoldNum = account.saHoldNum - sellNum
    # 需减少仓位占用保证金
    saEmployBalanceT = account.saEmployBalance
    # 需减少持仓手续费
    saHoldChargeT = account.saHoldCharge
    saHoldTotalPrice = 0
    saHoldAveragePrice = 0
    saCrashPrice = 0
    saPlatformPutPrice = 0
    # 账户多空类型(0 - 初始, 1 - 买多 / 平多, 2 - 买空 / 平空)
    doMore = False
    if (account.saAccountType == 1):
        doMore = True
    # 平仓手续费公式
    closeStockCost = AccountUtil.openStockCost(sellPrice, sellNum, not doMore, unit, stockPrice)
    # 已实现盈亏公式
    saMakeMoneyT = AccountUtil.realLoss(sellPrice, sellNum, account.saHoldAveragePrice, not doMore, unit,
                                        closeStockCost)
    if (not (saHoldNum == 0)):
        # 使用原来的持仓均价计算需要减少的仓位保证金
        saEmployBalanceT = AccountUtil.employBalance(account.saHoldAveragePrice, sellNum, unit, lever)
        saHoldChargeT = sellNum / account.saHoldNum * account.saHoldCharge / AccountUtil.UNIT
        # 持仓总价公式
        saHoldTotalPrice = AccountUtil.holdTotalPrice(account.saHoldTotalPrice + saMakeMoneyT - saHoldChargeT, account.saHoldAveragePrice, -sellNum)
        saHoldAveragePrice = AccountUtil.holdAvgPrice(saHoldTotalPrice, saHoldNum)
    saMakeMoney = account.saMakeMoney + saMakeMoneyT - saHoldChargeT
    # 加上这次交易释放的仓位占用保证金，减掉这次交易开仓时记的手续费
    saBalance = account.saBalance + saEmployBalanceT + saMakeMoneyT - saHoldChargeT
    # 仓位占用保证金
    saEmployBalance = account.saEmployBalance - saEmployBalanceT
    # 持仓手续费
    saHoldCharge = account.saHoldCharge - saHoldChargeT
    # 计算爆仓价的保证金
    calcCrashBalance = saBalance + account.saPlatformFreezeBalance + account.saFreezeBalance + saEmployBalance - saHoldCharge
    # 爆仓公式
    saCrashPrice = AccountUtil.crashPrice(saHoldAveragePrice, calcCrashBalance, saHoldNum, unit, doMore)
    # 爆仓挂单价公式
    saPlatformPutPrice = AccountUtil.crashPutPrice(saHoldAveragePrice, calcCrashBalance, saHoldNum, unit, doMore)
    # 冻结数量 == 0 & & 持仓量 == 0，设账户类型为初始状态
    if ((account.saFreezeNum < 1) & (saHoldNum < 1)):
        account.saAccountType = 0

    # 组装返回数据
    account.saBalance = saBalance
    account.saEmployBalance = saEmployBalance
    account.saMakeMoney = saMakeMoney
    account.saHoldNum = saHoldNum
    account.saHoldAveragePrice = saHoldAveragePrice
    account.saHoldTotalPrice = saHoldTotalPrice
    account.saCrashPrice = saCrashPrice
    account.saPlatformPutPrice = saPlatformPutPrice
    account.saHoldCharge = saHoldCharge
    return account


if __name__ == '__main__':
    account = Account.init()
    account.saBalance = 10000000
    account.saAccountType = 1
    account.saHoldNum = 100
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
    run(account, 1, 1, 0.002, 1, 5)
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
