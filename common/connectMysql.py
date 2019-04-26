__author__ = '123'
# coding=utf-8
import pymysql, requests
from common.names import names
from common.logger import logger
from collections import namedtuple
from common.params import *
from common.names import names


sda_id = "bfec1605014d43f6968f7cf3d83511fe"
base_url = names.url_123
base_253_url = names.url_253
base_50_url = names.url_50
sda_refresh_user_balance_url = names.sda_refresh_user_balance_url


def update_user_balance_value(user_id, _type=1):
    """
    根据用户ID给程序发送更新用户余额请求。
    :param user_id: 用户ID
    :param _type: 类型标注环境，1是123环境，2是50环境
    """
    url = None
    if _type == 1:
        url = "192.168.1.135:8080/dididu" + "/updateUserpurse.do"
    elif _type == 2:
        url = base_50_url + "/updateUserpurse.do"
    elif _type == 3:
        url = "http://192.168.1.135:10002/dididu" + "/updateUserpurse.do"
    elif _type == 5:
        url = "http://192.168.1.253:8080/dididu" + "/updateUserpurse.do"
    elif _type == 6:
        url = "http://192.168.1.252:8080/dididu" + "/updateUserpurse.do"
    elif _type == 7:
        url = "http://192.168.1.251:8080/dididu" + "/updateUserpurse.do"
    r = requests.get(url=url, params={"userId": user_id})
    r.close()


def update_sda_user_balance_value(user_id, sda_id, _type):
    """
    根据用户ID，sda_id，刷新用户的redis余额
    :param user_id: 用户ID
    :param sda_id: 合约ID
    :param _type: 测试环境地址
    :return:None
    """
    if _type == 5:
        session = requests.post(url=base_253_url+sda_refresh_user_balance_url,
                                data=sda_refresh_user_balance(user_id=user_id, sda_id=sda_id))
        session.close()
    elif _type == 2:
        session = requests.post(url=base_50_url+sda_refresh_user_balance_url,
                                data=sda_refresh_user_balance(user_id=user_id, sda_id=sda_id))
        session.close()
    elif _type == 6:
        session = requests.post(url=names.url_252+sda_refresh_user_balance_url,
                                data=sda_refresh_user_balance(user_id=user_id, sda_id=sda_id))
        session.close()
    elif _type == 3:
        session = requests.post(url=names.url_135+sda_refresh_user_balance_url,
                                data=sda_refresh_user_balance(user_id=user_id, sda_id=sda_id))
        session.close()
    elif _type == 7:
        session = requests.post(url=names.url_251+sda_refresh_user_balance_url,
                                data=sda_refresh_user_balance(user_id=user_id, sda_id=sda_id))
        session.close()
    else:
        print("环境切换错误")


user_name = "dididu_backend"


class ConnectMysql(object):

    """
    链接数据库，做测试数据准备工作
    """
    def __init__(self, _type=1, host="192.168.1.123", user="root", password="123456", db="dididu1", port=3306):

        # self.host, self.user, self.password, self.db, self.port = None
        self._type = _type
        if _type == 1:
            self.host = host
            self.user = user
            self.password = password
            self.db = db
            self.port = port
        elif _type == 2:
            self.host = "192.168.1.17"
            self.user = "root"
            self.password = password
            self.db = "dididu_exchange"
            self.port = 3308
        elif _type == 3:
            self.host = "192.168.1.135"
            self.user = user
            self.password = password
            self.db = "dididu_exchange"
            self.port = port
        elif _type == 4:
            self.host = "192.168.1.7"
            self.user = user
            self.password = password
            self.db = "dididu_management"
            self.port = 3309
        elif _type == 5:
            self.host = "192.168.1.253"
            self.user = user
            self.password = password
            self.db = "dididu_exchange"
            self.port = 3306

        elif _type == 6:
            self.host = "192.168.1.252"
            self.user = user
            self.password = password
            self.db = "dididu_exchange"
            self.port = 3306

        elif _type == 7:
            self.host = "192.168.1.251"
            self.user = user
            self.password = password
            self.db = "dididu_exchange"
            self.port = 3306
        # ------------------
        # 连接数据库
        try:
            self._db = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db, port=self.port, charset="utf8")
            self.cur = self._db.cursor()
        except Exception as E:
            print("数据库连接错误： ", E)

    def update_balance_value(self, user_mail, currency_id, balance_value):
        """
        根据用户user_mail和币id更新此用户的币余额
        :param user_mail: 用户邮箱、用户名
        :param currency_id: 币ID
        :param balance_value: 币余额
        """
        user_id = None
        try:
            user_id_sql = "SELECT user_id FROM t_user WHERE user_mail = %s"
            self.cur.execute(user_id_sql, user_mail)
            user_id = self.cur.fetchone()
            self._db.commit()
        except Exception as E:
            print("执行sql语句读取user_id错误，", E)
        try:
            update_balance_value_sql = "UPDATE t_user_balance SET balance_value = %s WHERE user_id = %s AND currency_id = %s"
            self.cur.execute(update_balance_value_sql, (balance_value, user_id, currency_id))
            self._db.commit()
        except Exception as F:
            print("执行sql语句更新用户余额", F)
        finally:
            self._db.close()
            self.cur.close()
        update_user_balance_value(user_id=user_id, _type=self._type)

    def get_Order_Status(self, order_id, order_type=1):
        """
        查询订单的状态
        :param order_type:订单类型，1 代表 买单， 2 代表卖单
        :param order_id: 订单ID
        :return:int类型，订单状态
        """
        if order_type == 1:
            sql = 'SELECT a.buyer_order_status FROM t_order_record_buyer as a WHERE a.buyer_order_id =%s'
        elif order_type == 2:
            sql = 'SELECT a.seller_order_status FROM t_order_record_seller as a WHERE a.seller_order_id =%s'
        try:
            r = self.cur.execute(sql, order_id)
            result = self.cur.fetchone()
            self._db.commit()
            self.cur.close()
            for i in result:
                return i
        except Exception as E:
            print("查询订单状态失败：", E)

    def update_order_status(self, transtion_id, order_type=1, order_status=0):
        """
        清除指定交易对的指定状态的订单
        :param order_type: 订单类型，1是买单，2是卖单，默认是1
        :param transtion_id: 必填参数，交易对ID
        :param order_status: 订单状态，0是委托中，1是撤单，2是成交
        :return:无
        """
        if order_type == 1:
            sql = "UPDATE t_order_record_buyer SET buyer_order_status = %s WHERE transtion_id = \'%s\' AND buyer_order_no <> %s AND buyer_order_status = 0"
        elif order_type == 2:
            sql = "UPDATE t_order_record_seller SET seller_order_status = %s WHERE transtion_id = \'%s\' AND seller_order_no <> %s AND seller_order_status = 0"
        self.cur.execute(sql, (order_status, transtion_id, "system"))
        self._db.commit()
        self.cur.close()
        self._db.close()

    def get_user_balance_data(self, user_mail, currency_id):
        """
        根据用户邮箱和币ID查询用户这个币的余额
        """
        sql = "SELECT balance_value FROM t_user_balance AS tub, t_user AS tu WHERE tu.user_mail =%s AND tu.user_id = tub.user_id AND tub.currency_id =%s"
        self.cur.execute(sql, (user_mail, currency_id))
        result = self.cur.fetchall()
        self._db.commit()
        self.cur.close()
        self._db.close()
        for i in result:
            for k in i:
                return k

    def insert_into_user(self):
        """
        循环插入用户
        并更新用户余额
        :return:
        """
        import time
        import random
        currency_balance = 990000000000000
        random_str = "abcdefghijklmn"
        password = "1ebb51846675cb9802783d6dae3c8c79"
        user_list = [ str(user_id) + "@163.com" for user_id in range(6900, 7000)]
        currency_id_list = [5,6,7,8,9,11,12, 13, 14,15, 16, 17, 18, 19,20,22, 23, 24, 25,26, 27]
        for k in currency_id_list:
            for i in user_list:
                insert_user_sql = "INSERT INTO t_user (user_id, user_mail, user_password, user_name) VALUE (%s, %s, %s, %s)"
                self.cur.execute(insert_user_sql, (random.choice(random_str) + i, i, password, i))
                time.sleep(0.1)
                insert_user_currency_sql = "INSERT INTO t_user_balance (balance_id, user_id, currency_id, balance_value) VALUE (%s, %s, %s, %s)"
                self.cur.execute(insert_user_currency_sql, (random_str + str(random.randint(1000, 9999) * 1000000) + random.choice(random_str) + str(random.randint(2000, 9999)), i, str(k), str(currency_balance)))
                self._db.commit()
                r = requests.get(url="http://192.168.1.123:10002/dididu/updateUserpurse.do", params={"userId": i})
                r.close()
        self.cur.close()
        self._db.close()

    def query_currency_min(self, transtion_id):
        """
        根据交易对ID查询单价最小输入位数和数量最小输入位数
        :param transtion_id: 交易对ID
        :return:单价最小单位,数量最小位数
        """
        query_sql = "SELECT tct.transtion_currency_unit_min, tct.transtion_price_unit_min FROM t_currency_transtion AS tct WHERE transtion_id = %s"
        self.cur.execute(query_sql, str(transtion_id))
        result = self.cur.fetchall()
        self._db.commit()
        self._db.close()
        self.cur.close()
        min_list = []
        for i in result:
            for k in i:
                min_list.append(k)
        return min_list

    def query_main_target_currency(self,transtion_id):
        """
        根据交易对ID查询此交易对的主币和目标币
        :param transtion_id:
        :return:主币ID，目标币ID
        """
        sql = "SELECT transtion_currency_base, transtion_currency_target FROM t_currency_transtion WHERE transtion_id = %s"
        self.cur.execute(sql,transtion_id)
        result = self.cur.fetchall()
        self._db.commit()
        self.cur.close()
        self._db.close()
        a_list = []
        for i in result:
            for k in i:
                a_list.append(k)
        return a_list

    def sda_query_user_freeze_balance(self, user_id):
        """
        sda-----根据用户userId查询用户sda委托保证金余额
        """
        sql = "SELECT sa_freeze_balance FROM t_sda_account WHERE sa_user_id = %s"
        self.cur.execute(sql, user_id)
        result = self.cur.fetchall()
        self._db.commit()
        self.cur.close()
        self._db.close()
        return result

    def sda_clear_open_empty_close_multi_order(self, user_id, contract_id, status):
        """
        根据contract_id将空单、平多单的状态Update为status
        :param contract_id:合约ID
        :param status:合约状态
        """
        sql = "UPDATE t_sda_close_empty SET sce_status = %s WHERE contract_id = %s"
        sql_second = "UPDATE t_sda_open_multi SET som_status = %s WHERE contract_id = %s"
        sql_third = "UPDATE t_sda_account SET sa_account_type = 0 WHERE sa_user_id = %s"
        self.cur.execute(sql, (status, contract_id))
        self.cur.execute(sql_second, (status, contract_id))
        self.cur.execute(sql_third, user_id)
        self._db.commit()
        self.cur.close()
        self._db.close()

    def sda_clear_open_multi_close_open_order(self, user_id, contract_id, status):
        """
        根据contract_id将多单、平空单的状态update为status
        :param contract_id: 合约ID
        :param status: 合约状态
        """
        sql = "UPDATE t_sda_open_empty SET soe_status = %s WHERE contract_id = %s"
        sql_second = "UPDATE t_sda_close_multi SET scm_status = %s WHERE contract_id = %s"
        sql_third = "UPDATE t_sda_account SET sa_account_type = 0 WHERE sa_user_id = %s"
        self.cur.execute(sql, (status, contract_id))
        self.cur.execute(sql_second, (status, contract_id))
        self.cur.execute(sql_third, user_id)
        self._db.commit()
        self.cur.close()
        self._db.close()

    def sda_update_user_balance(self, user_id, sda_id, sda_balance):
        """
        根据用户ID和合约ID更新用户的可用保证金
        :param user_id: 用户ID
        :param sa_balance: 可用保证金
        :param sda_id: 合约ID
        """
        sql = "UPDATE t_sda_account SET sa_balance = %s WHERE sa_user_id = %s AND sa_sda_id = %s"
        try:
            self.cur.execute(sql, (sda_balance, user_id, sda_id))
            self._db.commit()
            self.cur.close()
            self._db.close()
            update_sda_user_balance_value(user_id=user_id, sda_id=sda_id, _type=self._type)
        except Exception as f:
            print("       mysql更新用户余额错误：", f)
            logger.info("mysql更新用户：{0}----异常：{1}".format(user_id, f))

    def sda_query_contract_min(self, sda_id):
        """
        根据合约ID查询价格、数量输入最小范围
        :param contract_id: 合约ID
        :return:返回最小价格，最小数量
        """
        sql = "SELECT ts.sda_unit_min,ts.sda_unit_max, ts.sda_heigt_price, ts.sda_lowest_price FROM t_sda AS ts WHERE sda_id = %s"
        try:
            self.cur.execute(sql, sda_id)
            self._db.commit()
            result = self.cur.fetchall()
            self.cur.close()
            self._db.close()
            _result = []
            for i in result:
                for k in i:
                    _result.append(k)
            name = namedtuple("min_max", ("num_min", "num_max", "price_min", "price_max"))
            na = name._make(_result)
            return na
        except Exception as E:
            print("查询合约最小、最大交易价格，最小、最大交易数量错误：", E)
            logger.info("查询合约：{0}交易、数量单位错误：{1}".format(sda_id, E))

    def query_sda_unit(self, sda_id):
        """
        查询sda_id的交易单位，股张比
        :param sda_id: 合约ID
        :return:交易单位
        """
        sql = "SELECT t_sda.sda_unit FROM t_sda WHERE sda_id = %s"
        try:
            self.cur.execute(sql, sda_id)
            _result = self.cur.fetchall()
            self._db.commit()
            self.cur.close()
            self._db.close()
            result = None
            for i in _result:
                for k in i:
                    result = k
            return result
        except Exception as E:
            logger.info("查询合约ID：{0}的交易单位错误：{1}".format(sda_id, E))
            print("查询合约交易单位错误：", E)

    def query_sda_level(self, sda_id):
        """
        查询合约的杠杆倍数
        :param sda_id: 合约ID
        :return:杠杆倍数
        """
        sql = "SELECT sda_lever_multiple FROM t_sda WHERE sda_id = %s"
        try:
            self.cur.execute(sql, sda_id)
            _result = self.cur.fetchall()
            self._db.commit()
            self.cur.close()
            self._db.close()
            result = None
            for i in _result:
                for k in i:
                    result = k
            return result
        except Exception as E:
            logger.info("查询合约ID：{0}的杠杆倍数错误：{1}".format(sda_id, E))
            print("查询合约杠杆倍数错误：", E)

    def sda_clear_balance_value(self, user_id, sda_id):
        """
        根据用户ID和SDA_ID清除用户合约账户的各项字段数据
        :param user_id: 用户ID
        :param sda_id: 合约ID
        :return:none
        """
        sql = "UPDATE t_sda_account SET sa_balance = 0, sa_platform_freeze_balance=0, sa_freeze_balance=0, sa_freeze_num=0,sa_employ_balance=0,sa_make_money=0,sa_hold_total_price=0,sa_hold_num=0,sa_hold_average_price=0 WHERE sa_user_id = %s AND sa_sda_id = %s"
        sql_2 = "UPDATE t_sda_account SET sa_hold_charge=0,sa_can_sell_num=0,sa_crash_price=0,sa_platform_put_price=0 WHERE sa_user_id = %s AND sa_sda_id = %s"
        sql_third = "UPDATE t_sda_account SET sa_account_type = 0 WHERE sa_user_id = %s"
        try:
            self.cur.execute(sql, (user_id, sda_id))
            self.cur.execute(sql_2, (user_id, sda_id))
            self.cur.execute(sql_third, user_id)
            self._db.commit()
            self.cur.close()
            self._db.close()
            update_sda_user_balance_value(user_id=user_id, sda_id=sda_id, _type=self._type)
        except Exception as E:
            print("mysql清除用户余额错误：", E)
            logger.info("mysql清除用户余额错误：{}".format(E))

    def sda_delete_user_order(self, sda_id):
        """
        根据用户ID和合约ID删除用户名下所有订单
        :param user_id: 用户ID
        :param sda_id: 合约ID
        :return:
        """
        open_empty_sql = "DELETE FROM t_sda_open_empty where contract_id = %s"
        open_multi_sql = "DELETE FROM t_sda_open_multi where contract_id = %s"
        close_empty_sql = "DELETE FROM t_sda_close_empty where contract_id = %s"
        close_multi_sql = "DELETE FROM t_sda_close_multi where contract_id = %s"
        try:
            self.cur.execute(open_multi_sql, sda_id)
            self.cur.execute(open_empty_sql, sda_id)
            self.cur.execute(close_multi_sql, sda_id)
            self.cur.execute(close_empty_sql, sda_id)
            self._db.commit()
            self.cur.close()
            self._db.close()
        except Exception as E:
            print("删除用户订单数据异常：", E)

    def sda_delete_order(self, sda_id):
        """
        清除合约下所有订单
        :param sda_id: 合约ID
        :return:
        """
        open_empty_sql = "DELETE FROM t_sda_open_empty where contract_id = %s"
        open_multi_sql = "DELETE FROM t_sda_open_multi where contract_id = %s"
        close_empty_sql = "DELETE FROM t_sda_close_empty where contract_id = %s"
        close_multi_sql = "DELETE FROM t_sda_close_multi where contract_id = %s"
        try:
            self.cur.execute(open_multi_sql, sda_id)
            self.cur.execute(open_empty_sql, sda_id)
            self.cur.execute(close_multi_sql, sda_id)
            self.cur.execute(close_empty_sql, sda_id)
            self._db.commit()
            self.cur.close()
            self._db.close()
        except Exception as E:
            print("删除订单数据异常：", E)

    def update_user_charge(self, user_mail, sda_id, charge, cost):
        """
        更新指定用户的交易手续费、资金费率
        :param user_mail: 用户名
        :param charge: 手续费
        :param cost:资金费率
        :param sda_id: 合约ID
        :return:
        """
        query_user_id_sql = "SELECT user_id FROM t_user WHERE user_mail = %s"
        self.cur.execute(query_user_id_sql, user_mail)
        user_id = self.cur.fetchall()
        sql = "UPDATE t_sda_account SET sa_service_charge_rate = %s, sa_fund_rate = %s WHERE sa_sda_id = %s AND sa_user_id = %s"
        self.cur.execute(sql, (charge, cost, sda_id, user_id))
        self._db.commit()
        self.cur.close()
        self._db.close()
        update_sda_user_balance_value(user_id=user_id, sda_id=sda_id, _type=self._type)

    def sda_update_user_platform_freeze_balance(self, user_mail, sda_id, balance):
        """
        更新用户的赠金
        :param user_id:用户id
        :param sda_id:合约id
        :param balance:更新的金额
        :return:
        """
        query_user_id_sql = "SELECT user_id From t_user where user_mail = %s"
        self.cur.execute(query_user_id_sql, user_mail)
        user_id = self.cur.fetchall()
        # print("user id：", user_id)
        sql = "UPDATE t_sda_account SET sa_platform_freeze_balance = %s where sa_user_id = %s and sa_sda_id = %s"
        self.cur.execute(sql, (balance, user_id, sda_id))
        self._db.commit()
        self.cur.close()
        self._db.close()
        update_sda_user_balance_value(user_id=user_id, sda_id=sda_id, _type=self._type)

    def query_user_id(self, user_mail):
        """
        查询用户id
        :return: user_id
        """
        sql = "SELECT user_id FROM t_user where user_mail = %s"
        self.cur.execute(sql, user_mail)
        user_id = self.cur.fetchall()
        self._db.commit()
        self.cur.close()
        self._db.close()
        return user_id


if __name__ == '__main__':
    # li = [2, 14, 16, 3, 4, 5, 81, 82]
    # for i in li:
    # update_sda_user_balance_value(user_id="sdaSysQuanLongAccountId", sda_id=10, _type=5)
    # update_user_balance_value(user_id="as6d46a5s4d5w4d56wa1d65w1a6d5", _type=5)
    # sda_list = [14,16,81]
    # for i in sda_list:
    ConnectMysql(_type=2).sda_update_user_balance(user_id="cce62b1e97704b15a93248cb3874b488", sda_id=32,
                                                  sda_balance=99000000 * 100000000)