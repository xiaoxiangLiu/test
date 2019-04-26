__author__ = '123'
import pytest
import time


if __name__ == '__main__':
    for i in range(10):
        time_data = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        html_name = "/work/report/test_report%s.html" % time_data
        pytest.main(["e:/workspace/test/case/SDA", "--html=%s"%html_name, "-reruns 2"])