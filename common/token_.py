__author__ = '123'
# coding=utf-8
import hashlib
from common.config import GetInit

user_buyer_mail = GetInit().GetData("user", "user_buyer_mail")
user_seller_mail = GetInit().GetData("user", "user_seller_mail")
user_password = GetInit().GetData("user", "user_password")


def get_token(path='', **kwargs):
    s = ""
    _timeStamp = ""
    i_1 = 0
    list_1 = []
    key_list = []
    for k, i in kwargs.items():
        key_list.append(k)
    key_list.sort()
    for m in key_list:
        if m == "timeStamp":
            _timeStamp = kwargs[m]
        if m != "token"and m != "timeStamp" and m != "languageType":
            list_1.append(kwargs[m])
    for i in list_1:
        i = str(i)
        s += i[-3:]
        i_1 += 1
        if i_1 == 5:
            break
    first_s = path + s + "sjs"
    token = hashlib.md5(first_s.encode("utf-8")).hexdigest()
    value = ""
    for i in range(len(token)):
        if i in [0, 1, 2, 8, 10, 14]:
            value = value + token[i]
    _second_value_time = _timeStamp[-3:]
    second_value = token + value + _second_value_time
    _token = hashlib.md5(second_value.encode("utf-8")).hexdigest()
    return _token


if __name__ == '__main__':
    param = {
        "isAuto": "",
        "userMail": "38@qq.com",
        "platform": "Android",
        "timeStamp": "1538118050702",
        "token": "",
        "languageType": 3,
        "userPassword": user_password,
        "uuid": "00000000-7508-8fb8-d616-f1c80033c587",
        "version": "1.2.1",
    }
    print(get_token(path="gin", **param))
