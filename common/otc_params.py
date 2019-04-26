from common.token_ import get_token


def get_otc_user_index_params(user_id):
    """
    otc首页
    :param user_id:
    :return:
    """
    param = {
        "userId":user_id,
    }

    return param


def get_otc_token_param(user_id):
    """
    获取otc token
    :param user_id: 用户id
    :return:
    """
    pass


def get_otc_user_asset_param(otc_token):
    """
    Otc 法币资产
    :return: param
    """
    param = {
        "languageType":3,
        "token": "",
        "timeStamp": "1552965566",
        "otc-Authorization": otc_token
    }
    _token = get_token(path="set", **param)
    token_param = {
        "languageType": 3,
        "token": _token,
        "timeStamp": "1552965566",
        "otc-authorization": otc_token
    }
    return token_param


def get_otc_user_asset_detail_param():
    """
    otc 法币账户资产明细
    :return:
    """
    pass


def get_otc_user_auth_info_param():
    """
    otc 法币账户认证信息
    :return: param
    """
    param = {

    }


def get_otc_user_recharge(user_id, currency_id, recharge_num):
    """
    otc 充值，BB转法币
    :return:
    """
    param = {
        "userId":user_id,
        "currencyId":currency_id,
        "recharge_num":recharge_num,
    }
    return param


def get_otc_user_withdraw_param(user_id, currency_id, withdraw_num):
    """
    otc 提现，法币转BB
    :param user_id: 用户id
    :param currency_id: 币id
    :param withdraw_num: 提现数量
    :return: 提现参数
    """
    param = {
        "userId":user_id,
        "currencyId":currency_id,
        "withdraw_num":withdraw_num,
    }

    return param


def get_otc_user_setPwd(pwd, pwd2, nick_name, otc_token):
    """
    otc 设置交易密码
    :param nick_name: 用户昵称
    :param pwd: 用户密码
    :return: 参数
    """
    param = {
        "token":"",
        "pwd":pwd,
        "pwd2":pwd2,
        "nickName":nick_name,
        "timeStamp":"1552965566",
        "otc-authorization":otc_token,
        "languageType":3,
    }
    _token = get_token(path="Pwd", **param)
    token_param = {
        "token":_token,
        "pwd":pwd,
        "pwd2":pwd2,
        "nickName":nick_name,
        "timeStamp":"1552965566",
        "otc-authorization":otc_token,
        "languageType": 3,
    }

    return token_param


def get_otc_user_update_pwd(user_id, old_pwd, new_pwd, new_pwd_2):
    """
    otc 修改交易密码
    :param user_id: 用户id
    :param old_pwd: 旧密码
    :param new_pwd: 新密码
    :param new_pwd_2: 新密码
    :return: 参数
    """
    param = {
        "userId":user_id,
        "oldPwd":old_pwd,
        "newPwd":new_pwd,
        "newPwd2":new_pwd_2,
    }
    return param


def get_otc_user_bank_list(offset=0,count=5):
    """
    otc 收款方式列表
    :param user_id: 用户id
    :return: 参数
    """
    param = {
        "offset":offset,
        "count":count,
    }
    return param


def get_otc_user_bank_add_0(bank_card_no, bank_name, user_real_name, pwd):
    """
    otc 添加银行卡
    :param user_id: 用户id
    :param user_name: 用户姓名
    :param bank_card_no: 银行卡号
    :param bank_name: 银行名称
    :param bank_detail_name:银行支行
    :return:参数
    """
    param = {
        "bankCardNo":bank_card_no,
        "bankName":bank_name,
        "userRealName":user_real_name,
        "pwd":pwd,
    }

    return param


def get_otc_user_bank_add_1(bank_card_no, bank_name, user_real_name, pwd):
    """
    otc 添加支付宝
    :param user_id: 用户id
    :param user_name: 用户姓名
    :param bank_card_no: 支付宝账户
    :param ewmPath: 二维码
    :return: 参数
    """
    param = {
        "bankCardNo":bank_card_no,
        "bankName":bank_name,
        "userRealName":user_real_name,
        "pwd":pwd,
    }

    return param


def get_otc_user_bank_add_2(bank_card_no, bank_name, user_real_name, pwd):
    """
    otc 添加微信支付
    :param user_id: 用户id
    :param user_name: 用户姓名
    :param bank_card_no: 支付宝账户
    :param ewmPath: 二维码
    :return: 参数
    """
    param = {
        "bankCardNo":bank_card_no,
        "bankName":bank_name,
        "userRealName":user_real_name,
        "pwd":pwd,
    }

    return param


def get_otc_user_bank_off_or_activate_0_param(Id,pwd):
    """
    otc 激活
    :param user_id: 用户id
    :param bank_card_id: 银行卡id
    :param pwd: 交易密码
    :return:参数
    """
    param = {
        "id":Id,
        "pwd":pwd,
    }

    return param


def get_otc_user_bank_off_or_activate_1_param(Id,pwd):
    """
    otc 关闭
    :param user_id: 用户id
    :param bank_card_id: 银行卡id
    :param pwd: 交易密码
    :return:参数
    """
    param = {
        "id":Id,
        "pwd":pwd,
    }

    return param


def get_otc_user_bank_del_param(Id, pwd):
    """
    otc 删除绑定的银行卡
    :param user_id: 用户id
    :param bank_card_id: 银行卡id
    :return:参数
    """
    param = {
        "id":Id,
        "pwd":pwd,
    }

    return param


def get_otc_order_create_param(user_id, legal_currency, digital_currency, unit_price, order_num, min_limit, max_limit, pay_types):
    """
    otc 发布交易单
    :param user_id: 用户id
    :param legal_currency: 法币类型
    :param digital_currency: 数字货币类型
    :param unit_price: 单价
    :param order_num: 数量
    :param min_limit: 最小限额
    :param max_limit: 最大限额
    :param pay_type: 支付方式
    :return: 参数
    """
    param = {
        "userId":user_id,
        "legalCurrency":legal_currency,
        "digitalCurrency":digital_currency,
        "unitPrice":unit_price,
        "orderNum":order_num,
        "minLimit":min_limit,
        "maxLimit":max_limit,
        "payTypes":pay_types,
    }

    return param


def get_otc_order_cancel_param(order_id):
    """
    otc 商家 撤销委托单
    :param order_id: 订单id
    :return: cancel param
    """
    param = {
        "languageType":3,
        "orderId":order_id,
    }
    return param


def get_otc_order_list_param(order_type):
    """
    otc 查询购买/出售委托单列表
    :param order_type: 订单类型，1：购买，2：出售
    :return: 参数
    """
    param = {
        "languageType": 3,
        "orderType": order_type,
    }
    return param


def get_otc_order_delegation_list_param(user_id):
    """
    otc 商户委托列表，商家查看自己的订单列表
    :param user_id: 用户id
    :return: 参数
    """
    param = {
        "userId":user_id,
        "languageType":3,
    }
    return param


def get_otc_sub_order_create_param(order_id, currency_num, money_amount):
    """
    otc 普通用户下单
    :param order_id: 父订单id
    :param currency_num: 数字货币数量
    :param money_amount: 法币数量
    :return: param
    """
    param = {
        "languageType":3,
        "orderId":order_id,
        "currencyNum":currency_num,
        "moneyAmount":money_amount,
    }
    return param


def get_otc_sub_order_cancel_param(sub_order_id):
    """
    otc 普通用户取消订单
    :param sub_order_id: 订单id
    :return: param
    """
    param = {
        "languageType":3,
        "subOrderType":sub_order_id,
    }
    return param


def get_otc_sub_order_confirm_paid_param(sub_order_id):
    """
    otc 付款确认
    :param sub_order_id:子订单id
    :return: param
    """
    param = {
        "languageType":3,
        "subOrderId":sub_order_id,
    }
    return param


def get_otc_sub_order_send_digital_currency_param(sub_order_id):
    """
    otc 放行数字货币
    :param sub_order_id: 子订单id
    :return: param
    """
    param = {
        "languageType":3,
        "subOrderId":sub_order_id,
    }
    return param


def get_otc_sub_order_get_param(order_id):
    """
    otc 订单详情
    :param order_id: 订单id
    :return: param
    """
    param = {
        "languageType":3,
        "orderId":order_id,
    }
    return param


