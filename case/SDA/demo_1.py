__author__ = '123'
# coding=utf-8
import requests
from common._mytest import MytestOnePlayer
from common.connectRedis import ConnectRedis
from common.connectMysql import ConnectMysql
from common.tools import init_environment_213
from common.tools import init_environment_253
from common._mytest import make_money

base, mysql_type, redis_type, sda_id = init_environment_253()
base_50, mysql_type_50, redis_type_50, sda_id_50 = init_environment_213()

def clear_all_data(sda_id, user_mail, user_id):
    """
    清除用户的合约下所有的mysql和redis数据
    :param sda_id: 合约ID
    :param user_id: 用户ID
    :return:
    """
    ConnectMysql(_type=mysql_type).sda_delete_user_order(sda_id=sda_id)
    ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
    ConnectRedis(_type=redis_type, db=4).sda_clear_user_balance(user_id=user_id, keys=sda_id)
    ConnectMysql(_type=mysql_type).sda_clear_balance_value(user_id=user_id, sda_id=sda_id)
    # ConnectMysql(_type=mysql_type).update_balance_value(user_mail=user_mail, currency_id=2, balance_value=90000000000000000)

# 51、52、53、54
user_id_list = ["f381a98d7ad84d1389f8500673e498c3",  "ffc61f4756a046408a7b144765389e37",
                "ffc61f4756a046408a7b144765389e38","cce62b1e97704b15a93248cb3874b488",
                "f381a98d7ad84d1389f8500673e498c3", "ffc61f4756a046408a7b144765389e37",
                "ffc61f4756a046408a7b144765389e38"]
_sda_id = "bfec1605014d43f6968f7cf3d83511fe"
xiaolin_list = ["3b3110ab9785419a8e1a4e9b42c3c511", "9fe065bac62140599ce126086838cb01",
                "599763575d4b43fbb9fa3e21986bf7fb", "3b3110ab9785419a8e1a4e9b42c3c511"]
baidu_sda_id = "19"
MOMO_ID = "31"
TSL_ID = "22"
all_user_id = ["3ccacc44b71540e0be560f55f02f393f", "3a22848ee44744da9637dd2a1e4834bd", "3b870bcc32374f17a2922893aebeaacf",
               "c2e0ee39546f404b8214b6ad6bd91b08", "cd37a5ca610f401f9dfda66125f31a10", "47885b99832946148be58d92835409f7",
               "0541499e4c384643a99bbab41f3f203a", "b07f62659faa418c8c3301eb892e9ece", "60439c75810244419c9c962067eeb7e2",
               "3b3110ab9785419a8e1a4e9b42c3c511", "9c5f6519c7164e1093acaf0b5617577b", "a1013e1f382f4841be92650df21d2a47",
               "823552a612cd4df09711471ceba896d3", "cf35422671454bcb9164d9b201547f16"
               ]

all_user_mail = [
    "3143998133@qq.com", "bp746@sina.com", "15766306256@163.com", "971202607@qq.com", "921519390@qq.com",
    "850405097@qq.com", "741447990@qq.com", "6257643@qq.com", "411395838@qq.com", "1040021448@qq.com",
    "154854990@qq.com", "19@qq.com", "1048516779@qq.com", "2226@qq.com"
]

all_dict = {
    "3143998133@qq.com":"2c7c6849d11f4aaca81eabd32914ccb0",
    "bp746@sina.com":"cd37a5ca610f401f9dfda66125f31a10",
    "15766306256@163.com":"47885b99832946148be58d92835409f7",
    "971202607@qq.com":"3b870bcc32374f17a2922893aebeaacf",
    "921519390@qq.com":"c2e0ee39546f404b8214b6ad6bd91b08",
    "850405097@qq.com":"3ccacc44b71540e0be560f55f02f393f",
    "741447990@qq.com":"0541499e4c384643a99bbab41f3f203a",
    "6257643@qq.com":"8983f3eae30d483183a59f406e4e657b",
    "411395838@qq.com":"146ef027d6d04267b0ce73d427fa5c0d",
    "1040021448@qq.com":"cf35422671454bcb9164d9b201547f16",
    "154854990@qq.com":"823552a612cd4df09711471ceba896d3",
    "19@qq.com":"9fe065bac62140599ce126086838cb01",
    "1048516779@qq.com":"3b3110ab9785419a8e1a4e9b42c3c511",
    "2226@qq.com":"599763575d4b43fbb9fa3e21986bf7fb",
    "38720034@qq.com":"cce62b1e97704b15a93248cb3874b488",
}

HUYA_ID = "30"
AAPL_ID = "4"
# sda_id_list = ["bfec1605014d43f6968f7cf3d83511fe", "f3f5062537b44bcabcd1847a09e53e77", "5", "6", "12", "15", "16", "17", "18", "19", "20","21", "22", "23", "24", "25"]
baoyang_id = "19985a6017944feca2a4b228303622c2"
sda_id_list = ["1", "2", "3", "4", "5"]


def delete_all_order(sda_id):
    """
    清除合约下所有订单
    :param sda_id: 合约ID
    :return:
    """
    ConnectRedis(_type=redis_type).sda_clear_order(sda_id=sda_id)
    ConnectMysql(_type=mysql_type).sda_delete_order(sda_id=sda_id)


user_50_53_list = [
    "a4116160c99643639c8d1ec6cc807469", "as6d54a654sd6a5s4d6as54d65as4d65",
    "as65d4a65s4d65a4sd654as65d4a65s4", "as6d46a5s4d5w4d56wa1d65w1a6d5",
]
quan_user_id_list = [
    "sdaSysQuanLongAccountId",
    "sdaSysQuanShortAccountId"
]
quan_user_50_id_list = [
    "cce62b1e97704b15a93248cb3874b488",
    "84b322d22c3b48d693fb330341be40d9",
]

xiaolin_dict = {
    "0891@qq.com":"dd7656c31ca8436fb5eb0d3b0f0634d3",
    "10@qq.com ":"884a32528fde4bc6a72639fb7bbe444d",
    "c@qq.com":"02a266c518014c699eedffea33f163ae",
    "d@qq.com":"f24048c622d7464abedcfa3d85defa67",
}

user_sda_dict = {"41@qq.com": "2", "42@qq.com": "14", "43@qq.com": "16", "44@qq.com": "3", "51@qq.com": "4",
                 "52@qq.com": "12", "53@qq.com": "13", "54@qq.com": "5"}

user_41_42 = ["ffc61f4756a046408a7b144765389e37", "f381a98d7ad84d1389f8500673e498c3"]
# sda_list = [14, 16, 24, 81]
# for v in sda_list:
for i in quan_user_id_list:
    clear_all_data(sda_id="10", user_id="f381a98d7ad84d1389f8500673e498c3", user_mail="41@qq.com")

# make_money(now_price=24.58, deal_price=22, deal_num=100, unit=0.001)