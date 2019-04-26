from .AccountUtil import canOpenStockBalance
from .AccountUtil import employBalance
from .AccountUtil import holdTotalPrice
from .AccountUtil import openStockCost
from .AccountUtil import holdAvgPrice
from .AccountUtil import crashPrice
from .AccountUtil import crashPutPrice
from .AccountUtil import realLoss


class Account(object):
    """
    账户计算类
    """

    def __init__(self, user_mail, balance=0, unit=1, lever=1, stock_id=2, stock_price=18.11):
        self.user_id = None
        self.user_mail = user_mail  # 用户邮箱
        self.stock_id = stock_id  # 股票ID
        self.stock_price = stock_price  # 股票价格
        self.balance = balance  # 可用余额
        self.plat_from_freeze_balance = 0  # 赠送金额
        self.freeze_balance = 0  # 冻结金额
        self.freeze_num = 0  # 冻结数量
        self.employ_balance = 0  # 仓位保证金
        self.make_money = 0  # 以实现盈亏
        self.hold_total_price = 0  # 持仓总价
        self.hold_num = 0  # 持仓数量
        self.hold_average_price = 0  # 持仓均价
        self.hold_charge = 0  # 持仓手续费
        self.can_sell_num = 0  # 可平持仓量
        self.account_type = 0  # 账户下单类型
        self.crash_price = 0  # 爆仓价
        self.plat_form_put_price = 0  # 爆仓挂单价
        self.unit = unit  # 交易单位
        self.lever = lever  # 杠杆

    def open_stock_freeze(self, price, num, do_more=True):
        """
        开仓，下委托单，计算下委托单后用户的各项数据
        :param price: 下单价格
        :param num: 下单数量
        :return:冻结金额
        """
        can_open_balance = canOpenStockBalance(balance=self.balance, platformFreezeBalance=self.plat_from_freeze_balance)

        if price > 0:  # 如果输入价格大于0，冻结金额等于此订单的金额，限价单
            self.freeze_balance = employBalance(price=price, count=num, unit=self.unit, lever=self.lever)
        else:  # 如果输入价格等于0，冻结金额等于可用余额，市价单
            self.freeze_balance = can_open_balance

        self.freeze_num = self.freeze_num + num
        self.balance = self.balance - self.freeze_balance

        if do_more:
            self.account_type = 1
        else:
            self.account_type = 2

        return self.freeze_balance

    def open_stock(self, price, num, order_total_num, order_freeze_balance, do_more=True):
        """
        持仓计算公式
        :param price: 成交价
        :param num: 成交数量
        :param do_more: 是否做多
        :param order_total_num: 委托单的总数量
        :param order_freeze_balance:订单冻结保证金
        :param stock_price:指数价
        :return:
        """
        freeze_balance_t = None
        if self.freeze_num - num > 0:  # 如果冻结数量减去成交数量大于0，成交数量小于委托中的总数量
            freeze_balance_t = num / self.freeze_num * order_freeze_balance  # 成交的部分是持仓金额
        else:
            print("成交数量：{0}不能大于委托数量：{1}".format(num, order_total_num))
        self.freeze_balance = self.freeze_balance - freeze_balance_t  # 冻结金额的总冻结金额减去持仓金额
        self.freeze_num = self.freeze_num - num  # 冻结数量等于总冻结数量减去持仓的数量

        # 本次成交的仓位保证金和持仓价值
        self.employ_balance = employBalance(price=price, count=num, unit=self.unit, lever=self.lever)
        self.hold_total_price = holdTotalPrice(self.hold_total_price, price, num)

        # 开仓手续费计算
        do_more = False
        if self.account_type == 1:
            do_more = True

        open_stock_cost = openStockCost(price=price, count=num, doMore=do_more, unit=self.unit,
                                        stockPrice=self.stock_price)
        self.hold_num = self.hold_num + num
        self.hold_average_price = holdAvgPrice(self.hold_total_price, self.hold_num)
        self.can_sell_num = self.can_sell_num + num
        self.balance = self.balance + freeze_balance_t - self.employ_balance

        # 计算爆仓价使用的余额
        calc_cash_balance = self.balance + self.plat_from_freeze_balance + self.freeze_balance + self.employ_balance \
                            - open_stock_cost

        # 预估爆仓价
        self.crash_price = crashPrice(self.hold_average_price, calc_cash_balance, self.hold_num, unit=self.unit,
                                      doMore=do_more)

        # 爆仓挂单价
        self.plat_form_put_price = crashPutPrice(self.hold_average_price, calc_cash_balance, self.hold_num,
                                                 unit=self.unit, doMore=do_more)

        # 持仓手续费
        self.hold_charge = self.hold_charge + open_stock_cost

        return self.hold_average_price, self.employ_balance, self.crash_price, self.plat_form_put_price

    def open_stock_cancel(self, cancel_num, order_total_num, order_freeze_balance):
        """
        撤销委托单
        :param cancel_num:撤销数量
        :param order_total_num: 委托单总数量
        :param order_freeze_balance: 委托单总结金额
        :return: 可用余额，冻结金额
        """
        cancel_balance_t = self.freeze_balance  # 冻结金额
        cancel_num_t = self.freeze_num  # 冻结数量

        if self.freeze_num - cancel_num > 0:  # 如果冻结数量大于撤销数
            cancel_balance_t = cancel_num / order_total_num * order_freeze_balance  # 冻结金额等于等比例的冻结金额
            cancel_num_t = cancel_num  # 撤销数量重新赋值

        self.freeze_balance = self.freeze_balance - cancel_balance_t  # 用户冻结金额等于历史冻结金额减去此次撤销金额
        self.freeze_num = self.freeze_num - cancel_num_t  # 用户的冻结数量等于冻结数量减去撤销数量
        self.balance = self.balance + cancel_balance_t  # 可用余额等于冻结金额加上撤销金额
        if self.freeze_num < 1:  # 如果冻结数量小于1
            self.account_type = 0  # 更新用户类型为0

        return self.balance, self.freeze_balance

    def close_stock_freeze(self, sell_num):
        """
        平仓冻结计算
        :param sell_num: 卖出数量
        :return:可平仓量
        """
        self.can_sell_num = self.can_sell_num - sell_num

        return self.can_sell_num

    def close_stock_cancel(self, cancel_num):
        """
        撤销平仓委托
        :param cancel_num: 平仓数量
        :param order_total_num: 持仓总量
        :param order_freeze_balance: 仓位保证金
        :return:
        """

        self.can_sell_num = self.can_sell_num + cancel_num

        return self.can_sell_num

    def close_stock(self, sell_num, sell_price, stock_price):
        """
        平仓计算
        :param sell_num:平仓数量
        :param sell_price:平仓价格
        :param stock_price:指数价
        :return:
        """
        self.hold_num = self.hold_num - sell_num  # 持仓数量等于原持仓数量减去此次平仓数量
        employ_balance_t = self.employ_balance  # 需减少的仓位占用保证金
        hold_charge_t = self.hold_charge  # 需减少的持仓手续费
        do_more = False
        if self.account_type == 1:
            do_more = True

        # 平仓手续费
        close_stock_cost = openStockCost(price=sell_price, count=sell_num, doMore=not do_more, unit=self.unit, stockPrice=self.stock_price)

        # 已实现盈亏
        make_money_t = realLoss(price=sell_price, count=sell_num, holdAvgPrice=self.hold_average_price,
                                   doMore=not do_more, unit=self.unit, closeStockCost=close_stock_cost)

        if not self.hold_num == 0:
            # 使用原来的持仓均价计算需要减少的仓位保证金
            employ_balance_t = employBalance(price=self.hold_average_price, count=sell_num, unit=self.unit, lever=self.lever)
            hold_charge_t = sell_num / self.hold_num * self.hold_charge / 100000000

            # 持仓总价计算
            self.hold_total_price = holdTotalPrice(self.hold_total_price +
                                                   make_money_t - hold_charge_t,
                                                   self.hold_average_price, -sell_num)
            self.hold_average_price = holdAvgPrice(self.hold_total_price, self.hold_num)

        # 已实现盈亏等于已实现盈亏加上此次已实现盈亏减去持仓手续费
        self.make_money = self.make_money + make_money_t - hold_charge_t

        # 加上这次交易释放的仓位占用金，减去这次交易开仓时记的手续费
        self.balance = self.balance + employ_balance_t - hold_charge_t

        # 仓位保证金
        self.employ_balance = self.employ_balance - employ_balance_t

        # 持仓手续费
        self.hold_charge = self.hold_charge - hold_charge_t

        # 计算爆仓价使用的保证金，可用保证金 + 赠送保证金 + 冻结保证金 + 仓位保证金 - 持仓手续费
        calc_crash_balance = self.balance + self.plat_from_freeze_balance + self.freeze_balance + \
                             self.employ_balance - self.hold_charge

        # 计算预估爆仓价
        self.crash_price = crashPrice(holdAvgPrice=self.hold_average_price, totalBalance=calc_crash_balance,
                                      holdCount=self.hold_num, unit=self.unit, doMore=do_more)
        # 计算爆仓挂单价
        self.plat_form_put_price = crashPutPrice(holdAvgPrice=self.hold_average_price, totalBalance=calc_crash_balance,
                                                 holdCount=self.hold_num, unit=self.unit, doMore=do_more)

        # 冻结数量和持仓数量两个任一小于1，设账户类型为初始状态。
        if self.freeze_num < 1 and self.hold_num < 1:
            self.account_type = 0

        return self.balance