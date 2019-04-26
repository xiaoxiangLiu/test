import unittest
import requests
from common.tools import names
from common.tools import init_environment_otc
from common.params import *
from common.otc_params import *
from common.jsonparser import JMESPathExtractor
from common.logger import logger
from common.connectMysql import ConnectMysql
from common.connectRedis import ConnectRedis
from common.AccountTest.Account import init
from common.AccountTest.AccountUtil import crashPrice
from common.logger import logger
from common.myException import *
import time
import random

login_url, base_url, mysql_type, redis_type = init_environment_otc()


def login(user_mail, password):
    """
    登陆
    :param user_mail: 用户名
    :param password: 密码
    :return:login session
    """
    session = requests.session()
    login_resp = session.post(url=login_url+names.login_url, data=get_login_param(user=user_mail, user_password=password))
    logger.info("--------------------------------------------------------------------------------------------------")
    logger.info("用户：{0}---登陆状态：{1}----登陆返回：{2}".format(user_mail, login_resp.status_code, login_resp.json()))

    return session, login_resp


def get_otc_token(user_mail):
    """
    获取用户的token
    :param user_id: 用户id
    :return:
    """
    session = requests.session()
    login_resp = session.post(url=login_url+names.login_url, data=get_login_param(user=user_mail, user_password=names.password))
    logger.info("--------------------------------------------------------------------------------------------------")
    logger.info("用户：{0}---登陆状态：{1}----登陆返回：{2}".format(user_mail, login_resp.status_code, login_resp.json()))
    if login_resp.status_code != 200:
        logger.error("登陆接口状态：%d" % login_resp.status_code)
        raise HttpStatusException("接口状态不是200！")
    try:
        user_id = JMESPathExtractor().extract(query="OBJECT.userId", body=login_resp.text)
    except Exception as E:
        raise ValueError("接口userId错误：" + str(E))
    # user_id = ConnectMysql(_type=mysql_type).query_user_id(user_mail=user_mail)
    # print("user id", user_id)
    token_resp = requests.get(url=base_url+names.otc_token_get_url, params={"userId":user_id})
    # print(token_resp.text)
    if token_resp.status_code != 200:
        raise HttpStatusException
    token = JMESPathExtractor().extract(query="OBJECT", body=token_resp.text)
    # print(token)
    return token


def otc_user_asset(session, otc_token):
    """
    otc 法币账户资产
    :return:
    """
    asset_resp = session.post(url=base_url+names.otc_user_asset_url, data=get_otc_user_asset_param(otc_token=otc_token))
    if asset_resp.status_code != 200:
        logger.error("接口：{}".format(HttpStatusException("访问法币账户接口异常")))
        raise HttpStatusException("访问法币账户接口异常")
    else:
        logger.info("接口：{0}---状态：{1}---返回信息：{2}".format(names.otc_user_asset_url, asset_resp.status_code, asset_resp.json()))
        return asset_resp


def otc_recharge(session, user_id, currency_id, recharge_num):
    """
    otc 充值，bb转法币
    :param user_id: 用户id
    :param currency_id: 币id
    :param recharge_num: 充值数量
    :param session: 登陆用户的session
    :return: resp_dic
    """
    recharge_resp = session.post(url=base_url+names.otc_account_recharge_url, data=get_otc_user_recharge(user_id=user_id,
                                                                                                      currency_id=currency_id,
                                                                                                      recharge_num=recharge_num))
    logger.info("用户：{0}---接口：{1}---状态：{2}---返回：{3}".format(user_id, names.otc_user_recharge_url, recharge_resp.status_code, recharge_resp.json()))

    return recharge_resp.text


def otc_withdraw(session, user_id, currency_id, withdraw_num):
    """
    otc 提现，法币转币币
    :param session: 用户session
    :param user_id: 用户id
    :param currency_id: 币id
    :param withdraw_num: 提现数量
    :return: withdraw_dict
    """
    withdraw_resp = session.post(url=base_url+names.otc_account_withdraw_url, data=get_otc_user_withdraw_param(user_id=user_id,
                                                                                                            currency_id=currency_id,
                                                                                                            withdraw_num=withdraw_num))

    logger.info("用户：{0}---接口：{1}----状态：{2}---提现数量：{3}---返回：{4}".format(user_id, names.otc_user_withdraw_url,
                                                                       withdraw_resp.status_code, withdraw_num,
                                                                       withdraw_resp.json()))

    return withdraw_resp


def otc_order_create(session, user_id, legal_currency, digital_currency, unit_price, order_num, min_limit, max_limit,
                     pay_types):
    """
    otc 商家下委托单，
    :param session: 用户session
    :param user_id: 用户id
    :param legal_currency: 法币类型
    :param digital_currency: 数字货币类型
    :param unit_price: 单价
    :param order_num: 数量
    :param min_limit: 最小限额
    :param max_limit: 最大限额
    :param pay_types: 支付类型
    :return: create resp
    """
    create_resp = session.post(url=base_url+names.otc_order_create_url, data=get_otc_order_create_param(user_id=user_id,
                                                                                                        legal_currency=legal_currency,
                                                                                                        digital_currency=digital_currency,
                                                                                                        unit_price=unit_price,
                                                                                                        order_num=order_num,
                                                                                                        min_limit=min_limit,
                                                                                                        max_limit=max_limit,
                                                                                                        pay_types=pay_types))
    logger.info("用户：{0}---接口：{1}---状态：{2}".format(user_id, names.otc_order_create_url, create_resp.status_code))
    logger.info("委托币种：{0}---委托单价：{1}---委托数量：{2}----最小限额：{3}----最大限额：{4}---支付类型：{5}".format(digital_currency,
                                                                                           unit_price,order_num,min_limit,
                                                                                           max_limit,pay_types))

    return create_resp


def otc_order_cancel(session, order_id):
    """
    Otc 商家 撤销委托单
    :param session: 用户session
    :param order_id: 订单Id
    :return: cancel resp
    """
    cancel_resp = session.post(url=base_url+names.otc_order_cancel_url, data=get_otc_order_cancel_param(order_id=order_id))

    logger.info("撤销委托单接口：{0}----状态：{1}----返回信息：{2}".format(names.otc_order_cancel_url,
                                                           cancel_resp.status_code,cancel_resp.json()))

    return cancel_resp


def otc_set_password(session, otc_token, pwd, pwd2, nick_name):
    """
    otc 设置交易密码
    :param session: 用户session
    :param user_id: 用户id
    :param password: 交易密码
    :return:
    """
    set_resp = session.post(url=base_url+names.otc_user_setPwd_url, data=get_otc_user_setPwd(otc_token=otc_token,pwd=pwd,
                                                                                             pwd2=pwd2,
                                                                                             nick_name=nick_name))

    logger.info("设置交易密码：{0}----接口：{1}---状态：{2}---返回信息：{3}".format(pwd, names.otc_user_setPwd_url, set_resp.status_code, set_resp.json()))

    return set_resp


def otc_update_password(session, user_id, old_pwd, new_pwd, new_pwd2):
    """
    otc  修改交易密码
    :param session: 用户session
    :param user_id: 用户id
    :param old_pwd: 旧密码
    :param new_pwd: 新密码
    :param new_pwd2: 新密码2
    :return: update resp
    """
    update_resp = session.post(url=base_url+names.otc_user_updatePwd_url, data=get_otc_user_update_pwd(user_id=user_id,
                                                                                                       old_pwd=old_pwd,
                                                                                                       new_pwd=new_pwd,
                                                                                                       new_pwd2=new_pwd2,))
    logger.info("接口：{0}---状态：{1}---返回信息：{2}".format(names.otc_user_updatePwd_url, update_resp.status_code, update_resp.json()))
    logger.info("用户：{0}---旧密码：{1}---新密码：{2}----新密码2：{3}".format(user_id, old_pwd, new_pwd, new_pwd2))

    return update_resp


def otc_bank_list(session, offset=0, count=5):
    """
    收款方式列表
    :return: list resp
    """
    bank_resp = session.post(url=base_url+names.otc_user_bank_list_url, data=get_otc_user_bank_list(offset=offset,
                                                                                                    count=count))

    logger.info("接口：{0}---状态：{1}---返回结果：{2}".format(names.otc_user_bank_list_url, bank_resp.status_code, bank_resp.json()))

    return bank_resp


def otc_bank_add_0(session, bank_name, bank_card_no, user_real_name, pwd):
    """
    otc 添加银行卡
    :param bank_name:银行名称
    :param bank_card_no:银行卡号
    :param user_real_name:用户真实姓名
    :param pwd:用户密码
    :return:add resp
    """
    add_resp = session.post(url=base_url+names.otc_user_bank_add_0_url, data=get_otc_user_bank_add_0(bank_name=bank_name,
                                                                                                     bank_card_no=bank_card_no,
                                                                                                     user_real_name=user_real_name,
                                                                                                     pwd=pwd))
    logger.info("接口：{0}---状态：{1}----返回信息：{2}".format(names.otc_user_bank_add_0_url, add_resp.status_code, add_resp.json()))
    logger.info("添加银行：{0}---卡号：{1}---用户真实姓名：{2}----密码：{3}".format(bank_name, bank_card_no, user_real_name, pwd))

    return add_resp


def otc_bank_add_1(session, bank_name, bank_card_no, user_real_name, pwd):
    """
    otc 添加支付宝
    :param session: 用户session
    :param bank_name: 支付方式名，举例：支付宝
    :param bank_card_no:支付宝账号
    :param user_real_name:用户真实姓名
    :param pwd:用户密码
    :return:add resp
    """
    add_resp = session.post(url=base_url+names.otc_user_bank_add_1_url, data=get_otc_user_bank_add_1(bank_name=bank_name,
                                                                                                     bank_card_no=bank_card_no,
                                                                                                     user_real_name=user_real_name,
                                                                                                     pwd=pwd))

    logger.info("接口：{0}---状态：{1}----返回信息：{2}".format(names.otc_user_bank_add_1_url, add_resp.status_code, add_resp.json()))
    logger.info("支付方式：{0}----支付宝账号：{1}---真实姓名：{2}----密码：{3}".format(bank_name, bank_card_no, user_real_name, pwd))

    return add_resp


def otc_bank_add_2(session, bank_name, bank_card_no, user_real_name, pwd):
    """
    otc 添加支付宝
    :param session: 用户session
    :param bank_name: 支付方式名，举例：支付宝
    :param bank_card_no:支付宝账号
    :param user_real_name:用户真实姓名
    :param pwd:用户密码
    :return:add resp
    """
    add_resp = session.post(url=base_url+names.otc_user_bank_add_2_url, data=get_otc_user_bank_add_2(bank_name=bank_name,
                                                                                                     bank_card_no=bank_card_no,
                                                                                                     user_real_name=user_real_name,
                                                                                                     pwd=pwd))

    logger.info("接口：{0}---状态：{1}----返回信息：{2}".format(names.otc_user_bank_add_1_url, add_resp.status_code, add_resp.json()))
    logger.info("支付方式：{0}----微信账号：{1}---真实姓名：{2}----密码：{3}".format(bank_name, bank_card_no, user_real_name, pwd))

    return add_resp


def otc_user_bank_off_or_activate_0(session, Id, pwd):
    """
    otc 激活
    :param Id: 支付方式记录id
    :param pwd: 交易密码
    :return: off resp
    """
    off_resp = session.post(url=base_url+names.otc_user_bank_off_or_activate_0_url,
                            data=get_otc_user_bank_off_or_activate_0_param(Id=Id, pwd=pwd))

    logger.info("接口：{0}---状态：{1}----返回信息：{2}".format(names.otc_user_bank_off_or_activate_0_url, off_resp.status_code,
                                                     off_resp.json()))
    logger.info("支付方式记录ID：{0}---交易密码：{1}".format(Id, pwd))

    return off_resp


def otc_user_bank_off_or_activate_1(session, Id, pwd):
    """
    otc 关闭
    :param Id: 支付方式记录id
    :param pwd: 交易密码
    :return: off resp
    """
    off_resp = session.post(url=base_url+names.otc_user_bank_off_or_activate_1_url,
                            data=get_otc_user_bank_off_or_activate_1_param(Id=Id, pwd=pwd))

    logger.info("接口：{0}---状态：{1}----返回信息：{2}".format(names.otc_user_bank_off_or_activate_0_url, off_resp.status_code,
                                                     off_resp.json()))
    logger.info("支付方式记录ID：{0}---交易密码：{1}".format(Id, pwd))

    return off_resp


def otc_user_bank_del(session, Id, pwd):
    """
    otc 删除支付方式
    :param Id: 支付方式id
    :param pwd: 交易密码
    :return: del resp
    """
    del_resp = session.post(url=base_url+names.otc_user_bank_del_url, data=get_otc_user_bank_del_param(Id=Id,pwd=pwd))

    logger.info("接口：{0}----状态：{1}---返回信息：{2}".format(names.otc_user_bank_del_url, del_resp.status_code,del_resp.json()))
    logger.info("支付方式ID：{0}----交易密码：{1}".format(Id, pwd))

    return del_resp


def otc_order_list(session, order_type):
    """
    otc 查询购买/出售列表
    :param order_type: 订单类型，1：购买，2：出售
    :return: list resp
    """
    list_resp = session.post(url=base_url+names.otc_order_list_url, data=get_otc_order_list_param(order_type=order_type))

    logger.info("接口：{0}---状态：{1}----类型：{2}---返回信息：{3}".format(names.otc_order_list_url, list_resp.status_code,
                                                              order_type, list_resp.json()))

    return list_resp


def otc_order_delegation_list(session, user_id):
    """
    otc 商户委托列表
    :param user_id:用户id
    :return: list resp
    """
    list_resp = session.post(url=base_url+names.otc_order_delegation_list_url,
                             data=get_otc_order_delegation_list_param(user_id=user_id))

    logger.info("用户：{0}---接口:{1}---状态：{2}---返回：{3}".format(user_id,names.otc_order_delegation_list_url,
                                                           list_resp.status_code,list_resp.json()))

    return list_resp


def otc_sub_order_create(session, order_id, currency_num, money_amount):
    """
    Otc 普通用户下单
    :param order_id:订单id
    :param currency_num: 数字货币数量
    :param money_amount: 法币数量
    :return: create resp
    """
    create_resp = session.post(url=base_url+names.otc_sub_order_create_url,
                               data=get_otc_sub_order_create_param(order_id=order_id,currency_num=currency_num,
                                                                   money_amount=money_amount))

    logger.info("接口：{0}---状态：{1}---返回信息：{2}".format(names.otc_sub_order_create_url, create_resp.status_code,
                                                    create_resp.json()))

    return create_resp


def otc_sub_order_cancel(session, sub_order_id):
    """
    otc 普通用户取消订单
    :param session: 用户session
    :param sub_order_id: 子订单id
    :return: cancel resp
    """
    cancel_resp = session.post(url=base_url+names.otc_sub_order_cancel_url,
                               data=get_otc_sub_order_cancel_param(sub_order_id=sub_order_id))

    logger.info("接口：{0}---状态：{1}---取消子订单id：{2}----返回信息：{3}".format(names.otc_sub_order_cancel_url,
                                                                   cancel_resp.status_code,sub_order_id,cancel_resp.json()))

    return cancel_resp


def otc_sub_order_confirm_paid(session, sub_order_id):
    """
    otc 付款确认
    :param sub_order_id: 子订单id
    :return: confirm resp
    """
    confirm_resp = session.post(url=base_url+names.otc_sub_order_confirm_paid_url,
                                data=get_otc_sub_order_confirm_paid_param(sub_order_id=sub_order_id))

    logger.info("接口：{0}---状态：{1}---付款确认，子订单id：{2}----返回信息：{3}".format(names.otc_sub_order_confirm_paid_url,
                                                                      confirm_resp.status_code, sub_order_id,
                                                                      confirm_resp.json()))

    return confirm_resp


def otc_sub_order_send_digital_currency(session, sub_order_id):
    """
    otc 放行数字货币
    :param sub_order_id: 子订单id
    :return: currency resp
    """
    currency_resp = session.post(url=base_url+names.otc_sub_order_send_digital_currency_url,
                                 data=get_otc_sub_order_send_digital_currency_param(sub_order_id=sub_order_id))

    logger.info("接口：{0}----状态：{1}----放行数字货币，子订单id：{2}----返回信息：{3}".format(names.otc_sub_order_send_digital_currency_url,
                                                                          currency_resp.status_code, sub_order_id, currency_resp.json()))

    return currency_resp


def otc_sub_order_get(session, order_id):
    """
    otc 订单详情
    :param order_id: 订单id
    :return: get resp
    """
    get_resp = session.post(url=base_url+names.otc_sub_order_get_url, data=get_otc_sub_order_get_param(order_id=order_id))

    logger.info("接口：{0}----状态：{1}----订单详情，ID：{2}---返回信息：{3}".format(names.otc_sub_order_get_url, get_resp.status_code,
                                                                    order_id, get_resp.json()))

    return get_resp














