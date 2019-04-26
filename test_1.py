__author__ = '123'
# coding=utf-8
import threading
from BeautifulReport import BeautifulReport
import unittest
import time
import ddt
import queue
import ptest


class MyThread(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while not self.queue.empty():
            tests = self.queue.get()
            result = BeautifulReport(tests)
            result.report(description="测试报告", log_path="/", filename="自动化测试报告")
            self.queue.task_done()


def go():
    q = queue.Queue()
    tests = unittest.defaultTestLoader.discover(start_dir="./", pattern="test*.py")
    # 把测试用例装载到队列
    for i in tests:
        print(i)
        q.put(i)

    # 开启多线程
    for i in range(3):
        t = MyThread(q)
        t.setDaemon(True)
        t.start()

    q.join()


if __name__ == '__main__':
    go()
