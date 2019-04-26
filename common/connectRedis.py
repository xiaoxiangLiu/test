__author__ = '123'
# coding=utf-8
import redis
from common.logger import logger

from common.connectMysql import ConnectMysql


class MyRedisException(Exception):
    pass


class ConnectRedis(object):

    def __init__(self, _type=1, host="192.168.1.123", port=6379, db=6):

        self.type = _type

        if _type == 1:
            self.host = host
            self.port = port
            self.db = db
            self.password = "123"
            self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, password=self.password, decode_responses=True)
            self.r = redis.Redis(connection_pool=self.pool)

        elif _type == 2:
            self.host = "192.168.1.17"
            self.port = 7000
            self.db = db
            self.password = "111111"
            self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, password=self.password, decode_responses=True)
            self.r = redis.Redis(connection_pool=self.pool)

        elif _type == 3:
            self.host = "192.168.1.135"
            self.port = 6379
            self.db = db
            self.password = "123"
            self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, password=self.password, decode_responses=True)
            self.r = redis.Redis(connection_pool=self.pool)

        elif _type == 5:
            self.host = "192.168.1.135"
            self.port = 6379
            self.db = db
            self.password = "123"
            self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, password=self.password, decode_responses=True)
            self.r = redis.Redis(connection_pool=self.pool)

        elif _type == 6:
            self.host = "192.168.1.253"
            self.port = 6379
            self.db = db
            self.password = "123"
            self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, password=self.password, decode_responses=True)
            self.r = redis.Redis(connection_pool=self.pool)

        elif _type == 7:
            self.host = "192.168.1.252"
            self.port = 6379
            self.db = db
            self.password = "123"
            self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, password=self.password,
                                             decode_responses=True)
            self.r = redis.Redis(connection_pool=self.pool)

        elif _type == 8:
            self.host = "192.168.1.251"
            self.port = 6379
            self.db = db
            self.password = "123"
            self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, password=self.password,
                                             decode_responses=True)
            self.r = redis.Redis(connection_pool=self.pool)

    def clear_redis(self, name):
        """
        清除制定name或者是包含name的list的value
        :param name: redis的name，或者包含name的list
        :return:无
        """
        if isinstance(name, list):
            for i in name:
                index = self.r.llen(i)
                for k in range(index):
                    self.r.lpop(i)
        elif isinstance(name, str):
            if self.r.llen(name) < 1:
                print("这个%s没有value", name)
            else:
                index = self.r.llen(name=name)
                for i in range(index):
                    self.r.lpop(name=name)
        else:
            print("只接受str类型或者list类型")

    def get_user_balance(self, user_id, currency_id):
        name = str(user_id) + "_balance"
        data = self.r.hgetall(name)
        if isinstance(data, dict):
            value = data.get(str(currency_id))
            return value

    def clear_user_freezing_assets(self, user_id, currency_id):
        name = str(user_id) + "_frozen_balance"
        self.r.hdel(name, currency_id)

    def sda_clear_order(self, sda_id):
        name = "sda_sell_" + str(sda_id)
        buy_name = "sda_buy_" + str(sda_id)
        crash_name = "SDACache-AccountShortCrash-" + str(sda_id)
        a = [name, buy_name, crash_name]

        try:
            for i in a:
                self.r.delete(i)
        except Exception as E:
            print("清除sda订单错误：", E)
            logger.info("清除sda订单：{}".format(E))

    def sda_delete_crash(self, sda_id):
        """
        根据合约ID删除此合约的所有爆仓价存储数据
        :param sda_id: 合约ID
        :return:
        """
        name = "SDACache-AccountShortCrash-" + str(sda_id)

        try:
            self.r.delete(name)
        except Exception as E:
            print("删除合约的爆仓价报错：", E)
            logger.info("删除合约ID：{0}的爆仓价报错：{1}".format(sda_id, E))

    def sda_clear_user_balance(self, user_id, keys):
        """
        根据用户ID删除用户在redis中的余额，然后刷新
        :param user_id: 用户ID
        :return:none
        """
        name = "SDACache-Account-" + str(user_id)
        try:
            self.r.hdel(name, keys)
        except Exception as E:
            logger.info("清除redis用户余额失败：{}".format(E))
            print("清除redis用户余额失败：", E)

    def sda_update_stock_price(self, sda_id, stock_price):
        """
        根据股票ID修改股票价格
        :param sda_id:股票ID
        :param stock_price:股票价格
        :return:
        """
        try:
            sda_key = self.r.hget(name="ceshi_stock", key=sda_id)
            if sda_key != None:
                self.r.hdel("ceshi_stock", str(sda_id))
                self.r.hset(name="ceshi_stock", key=sda_id, value=stock_price)
            else:
                self.r.hset(name="ceshi_stock", key=sda_id, value=stock_price)
        except Exception as E:
            logger.error("更新股票指数价格错误：{}".format(E))
            raise MyRedisException


if __name__ == '__main__':
    ConnectRedis(_type=7, db=6).sda_update_stock_price(sda_id="81", stock_price=23)