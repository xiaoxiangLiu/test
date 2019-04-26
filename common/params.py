__author__ = '123'
# coding=utf-8
from common.token_ import get_token


def get_login_param(user, user_password):
        token_param = {
            "isAuto": "",
            "userMail": user,
            "platform": "Android",
            "timeStamp": "1538118050702",
            "token": "",
            "languageType": 3,
            "userPassword": user_password,
            "uuid": "00000000-7508-8fb8-d616-f1c80033c587",
            "version": "1.2.1",
        }
        token = get_token(path="gin", **token_param)
        login_param = {
            "isAuto": "",
            "userMail": user,
            "platform": "Android",
            "timeStamp": "1538118050702",
            "token": token,
            "languageType": 3,
            "userPassword": user_password,
            "uuid": "00000000-7508-8fb8-d616-f1c80033c587",
            "version": "1.2.1",
        }
        return login_param

def get_user_balance_and_currency_type_param(user):
        user_balance_currency_data = {
            "userMail": user,
            "timeStamp": "1538118050702",
            "languageType": 3,
            "token": "",
        }
        user_balance_token = get_token(path="ype", **user_balance_currency_data)
        user_balance_currency_data = {
            "userMail": user,
            "timeStamp": "1538118050702",
            "languageType": 3,
            "token": user_balance_token,
        }
        return user_balance_currency_data
def get_user_balance_servlet_param(user, currency_id, orderId=None, transactionId=None):

    if orderId == None or transactionId == None:

        user_balance_data = {
            "currencyId": currency_id,
            "languageType": 3,
            "timeStamp": "1538118050702",
            "token": "",
            "userMail": user,
        }
        token = get_token(path="let", **user_balance_data)
        user_balance_data_ = {
            "currencyId": currency_id,
            "languageType": 3,
            "timeStamp": "1538118050702",
            "token": token,
            "userMail": user,
        }
        return user_balance_data_
    else:
        user_balance_data = {
            "transactionId": transactionId,
            "orderId": orderId,
            "currencyId": currency_id,
            "languageType": 3,
            "timeStamp": "1538118050702",
            "token": "",
            "userMail": user,
        }
        token = get_token(path="let", **user_balance_data)
        user_balance_data_ = {
            "transactionId": transactionId,
            "orderId": orderId,
            "currencyId": currency_id,
            "languageType": 3,
            "timeStamp": "1538118050702",
            "token": token,
            "userMail": user,
        }
        return user_balance_data_

def get_user_balance_details_param(user, currency_id):

        user_balance_data = {
            "currencyId": currency_id,
            "languageType": 3,
            "timeStamp": "1538118050702",
            "token": "",
            "userMail": user,
        }
        token = get_token(path="ils", **user_balance_data)
        user_balance_data = {
            "currencyId": currency_id,
            "languageType": 3,
            "timeStamp": "1538118050702",
            "token": token,
            "userMail": user,
        }
        return user_balance_data

def get_order_reservations_param(transtion_id, order_type, num, price=None):
        order_reservations_param = {
            "transtionId": transtion_id,
            "orderType": order_type,
            "buyerOrderPrice": price,
            "buyerOrderNum": num,
            "timeStamp": "1538118050702",
            "languageType": 3,
            "token": "",
        }
        token = get_token("ons", **order_reservations_param)

        _order_reservations_param = {
            "transtionId": transtion_id,
            "orderType": order_type,
            "buyerOrderPrice": price,
            "buyerOrderNum": num,
            "timeStamp": "1538118050702",
            "languageType": 3,
            "token": token,
        }
        return _order_reservations_param

def get_sell_order_param(transtion_id, order_type,num, price=None):
        sell_order_param = {
            "transtionId": transtion_id,
            "orderType": order_type,
            "sellerOrderPrice": price,
            "sellerOrderNum": num,
            "timeStamp": "1538118050702",
            "languageType": 3,
            "token": "",
        }
        token = get_token(path="der", **sell_order_param)
        sell_order_param = {
            "transtionId": transtion_id,
            "orderType": order_type,
            "sellerOrderPrice": price,
            "sellerOrderNum": num,
            "timeStamp": "1538118050702",
            "languageType": 3,
            "token": token,
        }
        return sell_order_param

def get_update_revocation_status_param(_type, order_id):
        update_revocation_status_param = {
            "languageType": 3,
            "timeStamp": "1538118050702",
            "type": _type,
            "orderId":order_id,
            "token": "",
        }
        token = get_token(path="tus", **update_revocation_status_param)
        update_revocation_status_param = {
            "languageType": 3,
            "timeStamp": "1538118050702",
            "type": _type,
            "orderId": order_id,
            "token": token,
        }
        return update_revocation_status_param

def get_query_present_order_param(currentPage, pageSize):

    query_Present_Orde_data = {
        "languageType": 3,
        "currentPage": currentPage,
        "pageSize": pageSize,
        "timeStamp": "1538118050702",
        "token": ""
    }
    token = get_token(path="der", **query_Present_Orde_data)
    query_Present_Orde_data = {
        "languageType": 3,
        "currentPage": currentPage,
        "pageSize": pageSize,
        "timeStamp": "1538118050702",
        "token": token
    }
    return query_Present_Orde_data

def get_user_logout_param():
    param = {
        "timeStamp": "1542016948959",
        "languageType": 3,
        "token":"",
    }
    token = get_token(path="out", **param)
    token_param = {
        "timeStamp":"1542016948959",
        "languageType":3,
        "token":token,
    }
    return token_param

def get_query_transtion_pair_param():

    param = {
        "timeStamp":"1542016948959",
        "languageType":3,
        "token":"",
    }
    token = get_token(path="air", **param)
    token_param = {
        "timeStamp":"1542016948959",
        "languageType":3,
        "token":token
    }
    return token_param


def get_user_withdraw_operate(user, withdraw_address, currency_tag, currency_id, currency_transtion_commission,withdraw_quantity):
    param = {
        "userMail":user,
        "checkWay":2,
        "veryCode":"",
        "googleCode":"",
        "withdrawAddress":withdraw_address,
        "currencyTag":currency_tag,
        "currencyId":currency_id,
        "currencyTranstionCommission":currency_transtion_commission,
        "withdrawQuantity":withdraw_quantity,
        "timeStamp":"1542016948959",
        "languageType":"3",
        "token":"",
    }
    token = get_token(path="ate", **param)
    token_param = {
        "userMail":user,
        "checkWay":2,
        "veryCode":"",
        "googleCode":"",
        "withdrawAddress":withdraw_address,
        "currencyTag":currency_tag,
        "currencyId":currency_id,
        "currencyTranstionCommission":currency_transtion_commission,
        "withdrawQuantity":withdraw_quantity,
        "timeStamp":"1542016948959",
        "languageType":"3",
        "token":token,
    }
    return token_param


def get_user_withdreaw_check(user, currency_id):
    param = {
        "userMail":user,
        "currencyId":currency_id,
        "timeStamp":"1543032477954",
        "languageType":"3",
        "token":"",
    }
    token = get_token(path="eck", **param)
    token_param = {
        "userMail":user,
        "currencyId":currency_id,
        "timeStamp":"1543032477954",
        "languageType":"3",
        "token":token,
    }
    return token_param


def get_sda_order_create_param(sda_id, order_type, order_price_type, lever=1, order_price="", order_num=""):
    """
    合约下单接口参数模板
    """
    param = {
        "languageType":3,
        "token": "",
        "timeStamp": "1543493849",
        "sdaId": sda_id,  # 合约ID
        "orderType": order_type,  # 订单类型
        "orderPriceType": order_price_type,  # 价格类型
        "orderPrice": order_price,  # 订单价格
        "orderAmount": order_num,  # 订单数量
        "lever":lever
    }
    token = get_token(path="ate", **param)
    token_param = {
        "languageType": 3,
        "token": token,
        "timeStamp": "1543493849",
        "sdaId": sda_id,  # 合约ID
        "orderType": order_type,  # 订单类型
        "orderPriceType": order_price_type,  # 价格类型
        "orderPrice": order_price,  # 订单价格
        "orderAmount": order_num,  # 订单数量
        "lever":lever,
    }
    return token_param


def get_sda_account_deposit_param(sda_id, amount):
    """
    划转金额接口参数模板
    """
    param = {
        "languageType": "3",
        "sdaId":sda_id,
        "amount":amount,
        "token":""
    }
    token = get_token(path="sit", **param)
    token_param = {
        "languageType": "3",
        "sdaId":sda_id,
        "amount":amount,
        "token":token
    }
    return token_param


def get_sda_order_get_open_param(sda_id, order_id=""):
    """
    查询当前委托接口参数模板
    """
    param = {
        "languageType": 3,
        "token": "",
        "sdaId": sda_id,
        "timeStamp": "1543493849",
        "page": 1,  # 当前页码
        "numPerPage": 10,  # 每页数量
        "orderId":order_id,
    }
    token = get_token(path="pen", **param)
    token_param = {
        "languageType": 3,
        "token": token,
        "sdaId": sda_id,
        "timeStamp": "1543493849",
        "page": 1,  # 当前页码
        "numPerPage": 10,  # 每页数量
        "orderId": order_id,
    }
    return token_param


def get_sda_order_cancel_param(sda_id, order_id, order_type):
    """
    sda，撤单接口参数模板
    :param order_id: 合约id
    """
    param = {
        "languageType":3,
        "token":"",
        "timeStamp":"1543493849",
        "orderId":order_id,  # 订单ID
        "orderType": order_type,  # 订单类型
        "sdaId":sda_id,  # 合约ID
    }
    token = get_token(path="cel", **param)
    token_param = {
        "languageType": 3,
        "token": token,
        "timeStamp": "1543493849",
        "orderId": order_id,  # 订单ID
        "orderType": order_type,  # 订单类型
        "sdaId": sda_id,  # 合约ID
    }
    return token_param


def get_sda_get_param(sda_id):
    """
    sda，查询单个sda账户信息
    """
    param = {
        "languageType":3,
        "token":"",
        "timeStamp":"1543493849",
        "sdaId":sda_id,
    }
    token = get_token(path="get", **param)
    token_param = {
        "languageType": 3,
        "token": token,
        "timeStamp": "1543493849",
        "sdaId": sda_id,
    }
    return token_param


def get_sda_account_asset_get_param():
    """
    账户信息接口参数模板
    """
    param = {
        "languageType":3,
        "token":"",
        "timeStamp":"1543493849",
    }
    token = get_token(path="Get", **param)
    token_param = {
        "languageType": 3,
        "token": token,
        "timeStamp": "1543493849",
    }
    return token_param


def get_sda_account_asset_detail_get_param():
    """
    账户详情接口参数模板
    """
    param = {
        "languageType": 3,
        "token": "",
        "timeStamp": "1543493849",
    }
    token = get_token(path="Get", **param)
    token_param = {
        "languageType": 3,
        "token": token,
        "timeStamp": "1543493849",
    }
    return token_param


def get_sda_query_sda_fund_record_param():
    """
    资金流水接口参数模板
    """
    param = {
        "languageType":3,
        "token":"",
        "timeStamp":"1543493849",
        "currentPage":1,
        "pageSize":10,
    }
    token = get_token(path="Get", **param)
    token_param = {
        "languageType": 3,
        "token": token,
        "timeStamp": "1543493849",
        "currentPage": 1,
        "pageSize": 10,
    }
    return token_param


def get_sda_agreement_accept_param():
    """
    交易提醒接口参数模板
    """
    pass


def get_sda_market_info_get_param(sda_id):
    """
    获取市场行情及十档数据接口参数模板
    """
    param = {
        "languageType":3,
        "sdaId":sda_id,
        "timeStamp":"timeStamp",
        "token":"",
    }
    token = get_token(path="Get", **param)
    token_param = {
        "languageType": 3,
        "sdaId": sda_id,
        "timeStamp": "timeStamp",
        "token": token,
    }
    return token_param


def get_sda_minute_kline_param(sda_id, k_type):
    """
    获取K线接口参数模板
    """
    param = {
        "languageType":3,
        "token":"",
        "timeStamp":"1543493849",
        "kType":k_type,
        "sdaId":sda_id
    }
    token = get_token(path="ine", **param)
    token_param = {
        "languageType": 3,
        "token": token,
        "timeStamp": "1543493849",
        "kType": k_type,
        "sdaId": sda_id
    }
    return token_param


def get_sda_fund_balance_param():
    """
    查询用户资金余额接口参数模板
    """
    param = {
        "languageType":3,
        "token":"",
        "timeStamp":"1543493849"
    }
    token = get_token(path="nce", **param)
    token_param = {
        "languageType": 3,
        "token": token,
        "timeStamp": "1543493849"
    }
    return token_param


def get_sda_account_withdraw_param(sda_id, amount):
    """
    合约账户转到BB账户接口参数模板
    """
    param = {
        "languageType":3,
        "sdaId":sda_id,
        "amount":amount,
        "token":"",
    }
    token = get_token(path="raw", **param)
    token_param = {
        "languageType": 3,
        "sdaId": sda_id,
        "amount": amount,
        "token":token,
    }
    return token_param


def get_sda_get_list_param():
    """
    查询SDA列表接口参数模板
    """
    param = {
        "languageType":3,
        "token":"",
        "timeStamp":"1543493849",
    }
    token = get_token(path="ist", **param)
    token_param = {
        "languageType": 3,
        "token": token,
        "timeStamp": "1543493849",
    }
    return token_param


def get_sda_account_positions_get_param(sda_id):
    """
    查询当前持仓参数模板
    """
    param = {
        "languageType":3,
        "sdaId":sda_id,
        "token":"",
        "page":1,
        "numPerPage":100,
        "timeStamp":"1533280078000"
    }
    token = get_token(path="Get", **param)
    token_param = {
        "languageType": 3,
        "sdaId": sda_id,
        "token": token,
        "page": 1,
        "numPerPage": 100,
        "timeStamp":"1533280078000"
    }
    return token_param


def get_sda_order_get_history_param(sda_id):
    """
    查询历史委托接口参数模板
    :param sda_id: 合约ID
    :return:
    """
    param = {
        "languageType":3,
        "token":"",
        "timeStamp":"1543493849",
        "sdaId":sda_id,
        "page": 1,
        "numPerPage":1,
    }
    token = get_token(path="ory", **param)
    token_param = {
        "languageType":3,
        "token":token,
        "timeStamp":"1543493849",
        "sdaId":sda_id,
        "page": 1,
        "numPerPage":1,
    }
    return token_param

def get_sda_account_info_param(sda_id, lever=1):
    """
    查询单个SDA合约账户信息接口参数模板
    :param sda_id: 合约ID
    :return:
    """
    param = {
        "languageType":3,
        "token":"",
        "timeStamp":"1543493849",
        "sdaId":sda_id,
        "lever":lever
    }
    token = get_token(path="nfo", **param)
    token_param = {
        "languageType": 3,
        "token": token,
        "timeStamp": "1543493849",
        "sdaId": sda_id,
        "lever": lever
    }
    return token_param


def get_sda_set_stock_price(stock_id, price):
    """
    set股票价格接口参数模板
    :param stock_id: 股票小写名字
    :param price: 价格
    :return: 加密后的参数
    """
    param = {
        "stockPrice": price,
        "stockId": stock_id,
        "token":"",
    }
    token = get_token(path="ice", **param)
    token_param = {
        "stockPrice": price,
        "stockId": stock_id,
        "token": token,
    }
    return token_param

def sda_refresh_user_balance(user_id, sda_id):
    """
    刷新sda用户余额接口
    :return: 加密后的参数
    """
    param = {
        "userId":user_id,
        "sdaId":sda_id,
        "token":"",
    }
    token = get_token(path="esh", **param)
    token_param = {
        "userId":user_id,
        "sdaId":sda_id,
        "token":token
    }
    return token_param


def get_sda_sync_lock_param(sync_id):
    """
    用来同步sda数据的接口，返回OK代表同步完成，每次做了业务上的操作去调用这个接口，返回OK之后去查询余额
    :param sync_id: 同步ID，每次下单、赠送、转入、转出都会返回的一个ID
    :return: 加密后的参数
    """
    param = {
        "syncLockKey":sync_id,
        "token":"",
    }
    token = get_token(path="ock", **param)
    token_param = {
        "syncLockKey": sync_id,
        "token": token,
    }
    return token_param


def query_success():
    param = {
        "currentPage":1,
        "languageType":3,
        "pageSize":100,
        "timeStamp":"1546401150000",
        "token":""
    }
    token = get_token(path="der", **param)
    token_param = {
        "currentPage": 1,
        "languageType": 3,
        "pageSize": 100,
        "timeStamp": "1546401150000",
        "token":token
    }
    print(token_param)


def home_page(version):
    param = {
        "version":version,
        "timeStamp":"1546695129377",
        "languageType":3,
        "token":"",
    }
    token = get_token(path="Get", **param)
    token_param = {
        "version": version,
        "timeStamp": "1546695129377",
        "languageType": 3,
        "token": token,
    }
    return token_param


def get_partner_rest_password_param(sys_user_id):
    """
    代理商系统重置密码参数
    :return:
    """
    param = {
        "sysUserId":sys_user_id,
    }
    return param

def get_partner_login_param(user, passwd):
    """
    代理商登陆
    :param user: 用户名
    :param passwd: 密码
    :return:
    """
    param = {
        "username":user,
        "password":passwd,
    }
    return param


if __name__ == '__main__':
    get_sda_account_positions_get_param(sda_id="2")