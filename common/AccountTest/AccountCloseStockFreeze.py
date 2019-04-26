import Account


def run(account, sellNum):
    account.saCanSellNum = account.saCanSellNum - sellNum
    return account


if __name__ == '__main__':
    account = Account.init()
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
    run(account, 3)
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
