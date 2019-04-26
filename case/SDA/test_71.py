__author__ = '123'
# coding=utf-8
import unittest
from common.tools import init_environment_213
from common.names import names
from common._mytest import MyTestTwoUser
from common._mytest import assert_one
from common.connectMysql import ConnectMysql
from common.jsonparser import JMESPathExtractor
from common.params import *
from common.logger import logger
from common.connectRedis import ConnectRedis
from common._mytest import query_account_position_get
from common._mytest import account_info
from common._mytest import make_busted_price
from common._mytest import query_order_get_history
import time

base, mysql_type, redis_type, sda_id = init_environment_213()

sda_order_create_url = names.sda_order_create_url
sda_order_get_open_url = names.sda_order_get_open_url
sda_order_cancel_url = names.sda_order_cancel_url

sda_get_url = names.sda_get_url
sda_account_asset_detail_get_url = names.sda_account_asset_detail_get_url

多单 = names.多单
空单 = names.空单
平多 = names.平多
平空 = names.平空
限价 = names.xianjiadan
市价 = names.shijiadan

currency_id = 5