import Account


def run(account, cancelNum):
    account.saCanSellNum = account.saCanSellNum + cancelNum
    return account


if __name__ == '__main__':
    account = Account.init()
    account.saHoldNum = 10
    account.saCanSellNum = 7
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
    run(account, 3)
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
