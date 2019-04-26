import Account
import AccountUtil


def run(account, buyNum, buyPrice, doMore, unit, lever):
    # 可买保证金
    canBuyBalance = AccountUtil.canOpenStockBalance(account.saBalance, account.saPlatformFreezeBalance)
    # 委托冻结保证金
    freezeBalance = 0
    if (buyPrice > 0):
        freezeBalance = AccountUtil.employBalance(buyPrice, buyNum, unit, lever)
    else:
        freezeBalance = canBuyBalance

    account.saFreezeBalance = freezeBalance
    account.saFreezeNum = account.saFreezeNum + buyNum
    account.saBalance = account.saBalance - freezeBalance
    if (doMore):
        account.saAccountType = 1
    else:
        account.saAccountType = 2
    return account


if __name__ == '__main__':
    account = Account.init()
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
    run(account, 3, 3, True, 100000000, 1)
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
