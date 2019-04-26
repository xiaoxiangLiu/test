__author__ = '123'
# coding=utf-8
import re


a = "216516.0000"
b = re.search(".\d*", a).group()
print(b)
