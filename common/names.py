__author__ = '123'
# coding=utf-8
from common.config import GetInit
from collections import namedtuple

base_data = GetInit().get_test_data(file_name="base.yaml")


class names(object):
    url_50 = "http://192.168.1.50:88/dididu"
    url_253 = "http://192.168.1.253:8080/dididu"
    url_252 = "http://192.168.1.252:8080/dididu"
    url_251 = "http://192.168.1.251:8080/dididu"
    url_123 = base_data.get("base_url")
    url_7 = base_data.get("7_base_url")
    url_135 = "http://192.168.1.135:8080/dididu"
    url_50_public = "http://211.103.178.202:9096/dididu"
    url_partner = "http://192.168.1.253:9292"

    mysql_type_135 = 3
    mysql_type_123 = base_data.get("mysql_type")
    mysql_type_50 = base_data.get("50_mysql_type")
    mysql_type_7 = base_data.get("7_mysql_type")
    mysql_type_253 = 5

    redis_type_123 = base_data.get("redis_type")
    redis_type_50 = base_data.get("50_redis_type")
    redis_type_7 = base_data.get("7_redis_type")
    redis_type_135 = 3
    redis_type_253 = 6
    redis_type_252 = 7
    redis_type_251 = 8

    user_39 = base_data.get("user_39")
    user_41 = base_data.get("user_41")
    user_42 = base_data.get("user_42")
    user_43 = base_data.get("user_43")
    user_48 = "48@qq.com"
    user_49 = "49@qq.com"
    user_51 = "51@qq.com"
    user_52 = "52@qq.com"
    user_53 = "53@qq.com"
    user_54 = "54@qq.com"

    market_user_38 = base_data.get("market_user_38")
    market_user_40 = base_data.get("market_user_40")

    password = base_data.get("password")

    login_header = {
                    "Accept-Encoding": "gzip",
                    "User-Agent": "android-6.0/Meizu(M5)",
                    }

    login_url = base_data.get("login_url")
    get_user_balance_servlet_url = base_data.get("get_user_balance_servlet_url")
    order_reservations_url = base_data.get("order_reservations_url")
    sell_order_url = base_data.get("sell_order_url")
    update_revocation_status_url = base_data.get("update_revocation_status_url")
    user_balance_and_currency_type = base_data.get("user_balance_and_currency_type")
    user_balance_details_url = base_data.get("user_balance_details_url")
    logout_url = "/userLogout.do"
    query_present_order_url = "/queryPresentOrder.do"
    query_transtion_pari_url = "/queryTranstionPair.do"

    user_check_in_url = "/userCheckin.do"  # 签到接口
    get_user_checkin_info_url = "/getUserCheckinInfo.do"  # 查询签到信息接口
    user_withdraw_operate_url = "/userWithdrawOperate.do"  # 提现接口
    user_withdraw_check_url = "/userWithdrawCheck.do"  # 提现，确认用户余额接口
    ticker_url = "/ticker.do"  # 资讯接口

    xianjiadan = 0
    shijiadan = 1

    buy_order = 1
    sell_order = 2
    transtion_id = [4, 23, 24, 29, 30, 32, 34, 36, 37, 38, 44, 45, 46, 47]
    balance_value = 9900000000000000

    sda_account_create_url = "/SDAAccountCreate.do"  # 创建账户
    sda_account_deposit_url = "/SDAAccountDeposit.do"  # 资金划转
    sda_account_withdraw_url = "/SDAAccountWithdraw.do"  # 合约账户转到币币账号
    sda_get_list_url = "/SDAGetList.do"  # 查询SDA列表信息
    sda_get_url = "/SDAGet.do"  # 查询单个SDA信息
    sda_order_create_url = "/SDAOrderCreate.do"  # 下单接口
    sda_order_cancel_url = "/SDAOrderCancel.do"  # 撤单接口
    sda_order_get_open_url = "/SDAOrderGetOpen.do"  # 查询当前委托
    sda_order_get_history_url = "/SDAOrderGetHistory.do"  # 查询历史委托
    sda_account_positions_get_url = "/SDAAccountPositionsGet.do"  # 查询当前持仓
    sda_account_asset_get_url = "/SDAAccountAssetGet.do"  # 个人中心
    sda_account_asset_detail_get_url = "/SDAAccountAssetDetailGet.do"  # 账户详情
    query_sda_fund_record_url = "/SDAFundRecordGet.do"  # 资金流水
    sda_agreement_accept_url = "/SDAAgreementAccept.do"  # 交易提醒
    sda_market_info_get_url = "/SDAMarketInfoGet.do"  # 获取市场行情及10档数据
    sda_minuter_Kline_url = "/SDAMinuteKLine.do"  # 查询K线
    sda_fund_balance_url = "/SDAFundBalance.do"  # 查询用户资金余额接口
    sda_account_info_url = "/SDAAccountInfo.do"  # 查询单个SDA合约账户信息
    sda_set_stock_price_url = "/SetStockPrice.do"  # 给指定股票指定价格
    sda_refresh_user_balance_url = "/SDAAccountRefresh.do"  # sda刷新用户余额接口
    sda_sync_lock_url = "/SDASyncLock.do"  # sda用来同步数据的接口，返回OK代表已经同步完成
    home_page_url = "/SDAHomePageGet.do"  # 首页

    partner_rest_password_url = "/sys/user/resetPassword"  # 代理商系统管理员重置密码接口
    partner_login_url = "/login/userLogin"  # 代理商登陆

    otc_user_index_url = "/otc/user/index"  # otc账户
    otc_token_get_url = "/token/get"  # 获取token
    otc_account_recharge_url = "/otc/account/recharge"  # 充值，BB转法币
    otc_account_withdraw_url = "/otc/account/withdraw"  # 提现，法币转BB
    otc_user_setPwd_url = "/otc/user/setPwd"  # 设置交易密码
    otc_user_updatePwd_url = "/otc/user/updatePwd"  # 修改交易密码
    otc_user_bank_list_url = "/otc/user/bank/list"  # 收款列表
    otc_user_bank_add_0_url = "/otc/user/bank/add/0"  # 添加银行卡
    otc_user_bank_add_1_url = "/otc/user/bank/add/1"  # 添加支付宝
    otc_user_bank_add_2_url = "/otc/user/bank/add/2"  # 添加微信支付
    otc_user_bank_off_or_activate_0_url = "/otc/user/bank/offOrActivate/0"  # 激活
    otc_user_bank_off_or_activate_1_url = "/otc/user/bank/offOrActivate/1"  # 关闭
    otc_user_bank_del_url = "/otc/user/bank/del"  # 删除
    otc_order_create_url = "/otc/order/create"  # 发布交易单
    otc_order_cancel_url = "/otc/order/cancel"  # 撤销委托单
    otc_order_list_url = "/otc/order/list"  # 查询购买/出售委托单列表
    otc_order_delegation_list_url = "/otc/order/delegationList"  # 商户委托列表(商家查看自己的订单列表)
    otc_sub_order_create_url = "/otc/subOrder/create"  # 普通用户订单
    otc_sub_order_cancel_url = "/otc/subOrder/cancel"  # 取消订单
    otc_sub_order_confirm_paid_url = "/otc/subOrder/confirmPaid"  # 买家付款确认
    otc_sub_order_send_digital_currency_url = "/otc/subOrder/sendDigitalCurrency"  # 放行数字货币
    otc_child_order_finish_url = "/otc/childOrder/finish"  # 订单完成
    otc_sub_order_get_url = "/otc/subOrder/get"  # 订单详情
    otc_complaint_list_url = "/otc/complaint/list"  # 查询申诉理由
    otc_order_complaint_add_url = "/otc/order/complaint/add"  # 订单添加申诉
    otc_order_complaint_cancel_url = "/otc/order/complaint/cancel"  # 订单取消申诉
    otc_order_complaint_list_url = "/otc/order/complaint/list"  # 查询订单申诉
    otc_user_asset_url = "/otc/user/asset"  # 法币账户资产
    otc_user_asset_detail_url = "/otc/user/asset/detail"  # 法币账户资产明细





    多单 = 0
    空单 = 1
    平多 = 2
    平空 = 3

    _order_type = namedtuple("order_type", ("多单", "空单", "平多", "平空", "限价", "市价"))
    order_type = _order_type._make([0, 1, 2, 3, 0, 1])

_order_type = namedtuple("order_type", ("多单", "空单", "平多", "平空", "限价", "市价"))
order_type = _order_type._make([0, 1, 2, 3, 0, 1])


if __name__ == '__main__':
    print(order_type.市价)