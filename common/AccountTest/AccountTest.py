import Account
import AccountUtil
import AccountOpenStockFreeze
import AccountOpenStockCancel
import AccountOpenStock
import AccountCloseStockFreeze
import AccountCloseStockCancel
import AccountCloseStock

UNIT = 100000000

if __name__ == '__main__':
    account = Account.init()
    account.saAccountId = "xuyongjun_19"
    account.saUserId = 'xuyongjun'
    account.saSdaId = '19'
    account.saSdaName = 'MOMO'
    account.saSdaTag = 'MOMO'
    account.saBalance = 1000000 * UNIT
    account.saPlatformFreezeBalance = 0
    account.saFreezeBalance = 0
    account.saFreezeNum = 0
    account.saEmployBalance = 0
    account.saMakeMoney = 0
    account.saHoldTotalPrice = 0
    account.saHoldNum = 0
    account.saHoldAveragePrice = 0
    account.saHoldCharge = 0
    account.saCanSellNum = 0
    account.saAccountType = 0
    account.saCrashPrice = 0
    account.saPlatformPutPrice = 0
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))

    # 开仓冻结（账户、开仓数量、开仓价格、多空-多True,空False、单位、杠杆）
    AccountOpenStockFreeze.run(account, 100 * UNIT, 100 * UNIT, True, 1 * UNIT, 1)
    print("开仓冻结")
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))

    # 开仓取消（账户、取消数量、订单总数量、订单冻结总数量）
    # AccountOpenStockCancel.run(account, 1 * UNIT, 1 * UNIT, 2 * 1 * UNIT)
    # print("开仓取消")
    # print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))

    # 开仓（账户、开仓数量、开仓价格、订单总数量、订单总冻结金额、单位、杠杆、现货指数）
    AccountOpenStock.run(account, 100 * UNIT, 100 * UNIT, 100 * UNIT, 10000 * UNIT, 1 * UNIT, 1, 18.11 * UNIT)
    print("开仓")
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))


    # 平仓冻结（账户、平仓数量）
    AccountCloseStockFreeze.run(account, 100 * UNIT)
    print("平仓冻结")
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))

    # 平仓取消（账户、取消数量）
    # AccountCloseStockCancel.run(account, 1 * UNIT)
    # print("平仓取消")
    # print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))

    # 平仓（账户、平仓数量、平仓价格、单位、杠杆、现货指数）
    AccountCloseStock.run(account, 100 * UNIT, 120 * UNIT, 1 * UNIT, 1, 18.11 * UNIT)
    print("平仓")
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
