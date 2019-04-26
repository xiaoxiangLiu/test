class Account(object):
    pass


def init():
    account = Account()
    account.saAccountId = "xuyongjun_19"
    account.saUserId = 'xuyongjun'
    account.saSdaId = '19'
    account.saSdaName = 'MOMO'
    account.saSdaTag = 'MOMO'
    account.saBalance = 0
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
    return account


if __name__ == '__main__':
    account = init()
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
