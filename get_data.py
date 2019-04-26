__author__ = '123'
# coding=utf-8
import yaml
import os


path = os.path.dirname(__file__) + "/case/testdata/test_01.yaml"
with open(path, "r", encoding="utf-8") as file:
    count = file.read()
    y = yaml.load(count)
    print(y)
