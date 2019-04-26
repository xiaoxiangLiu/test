import Account


def run(account, cancelNum, orderTotalNum, orderFreezeBalance):
    # 需撤销委托冻结
    cancelBalanceT = account.saFreezeBalance  # 冻结金额
    cancelNumT = account.saFreezeNum  # 冻结数量
    if ((account.saFreezeNum - cancelNum) > 0):  # 如果冻结数量大于撤销数量
        cancelBalanceT = cancelNum / orderTotalNum * orderFreezeBalance  # 冻结金额等于等比例的冻结金额
        cancelNumT = cancelNum  # 撤销数量重新赋值
    account.saFreezeBalance = account.saFreezeBalance - cancelBalanceT  # 用户的冻结金额等于历史冻结金额减去此次撤销金额
    account.saFreezeNum = account.saFreezeNum - cancelNumT  # 用户的冻结数量等于冻结数量减去撤销数量
    account.saBalance = account.saBalance + cancelBalanceT  # 可用余额等于冻结金额加上撤销金额
    if (account.saFreezeNum < 1):  # 如果冻结数量小于1
        account.saAccountType = 0  # 更新用户类型为0
    return account


if __name__ == '__main__':
    account = Account.init()
    account.saFreezeNum = 1
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
    run(account, 3, 3, 100000000)
    print('\t'.join(['%s:%s' % item for item in account.__dict__.items()]))
