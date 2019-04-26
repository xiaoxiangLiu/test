from common._mytest import set_stock_price
import random
import time

for i in range(10):
    time.sleep(1)
    random_stock_price = int(random.uniform(43.01, 43.40) * 100) / 100
    print("time：", time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))
    print("stock_price", random_stock_price)
    # set_stock_price(stock_price=random_stock_price, stock_id="00700")


