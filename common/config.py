__author__ = '123'
# coding=utf-8
import configparser, os
import yaml

class GetInit(object):

    """
    读取Init文件
    """
    filenames = os.path.dirname(os.path.dirname(__file__)).replace("\\", "/") + "/config.ini"
    yaml_file_path = os.path.dirname(os.path.dirname(__file__)).replace("\\", "/") + "/case/testdata/"

    def GetData(self, section, option):
        reader = configparser.ConfigParser()
        reader.read(filenames=self.filenames, encoding="utf-8")
        value = reader.get(section=section, option=option)
        return value

    def get_test_data(self, file_name):
        yaml_file = self.yaml_file_path + file_name
        with open(yaml_file, "r", encoding="utf-8") as f:
            read = yaml.load(f)
            return read

if __name__ == '__main__':
    reader = GetInit()
    print(reader.get_test_data(file_name="transtion_8.yaml"))



