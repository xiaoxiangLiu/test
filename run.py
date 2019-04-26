__author__ = '123'
# coding=utf-8
import unittest
from BeautifulReport import BeautifulReport
import os

# 获取路径
cur_path = os.path.dirname(os.path.realpath(__file__))
case_path = os.path.join(cur_path, "case")
if not os.path.exists(case_path):
    print("测试用例需要放在'case'文件目录下")
    os.mkdir(case_path)
report_path = os.path.join(cur_path, "report")
if not os.path.exists(report_path):
    os.mkdir(report_path)

def add_case(case_path=case_path, rule="test*.py"):

    "加载所有测试用例"

    discover = unittest.defaultTestLoader.discover(case_path,
                                                   pattern=rule,
                                                   top_level_dir=None)
    return discover


def run(test_suite):
    result = BeautifulReport(test_suite)
    result.report(filename="report.html", description="接口自动化测试报告",
                  log_path="report")

if __name__ == '__main__':
    cases = add_case()
    run(cases)
