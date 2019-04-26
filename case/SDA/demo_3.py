from common.AccountTest.AccountUtil import openStockCost


UNIT = 100000000
cost = openStockCost(price=18.1*UNIT, count=20*UNIT, doMore=True, unit=1*UNIT, stockPrice=18.12*UNIT)
print(cost)