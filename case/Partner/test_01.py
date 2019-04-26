from common.partner_test import PartnerTest
import unittest



class TestCase(PartnerTest):
    """
    重置密码
    """
    def test_01(self):
        """
        重置密码
        :return:
        """
        print(self.sys_user)


if __name__ == '__main__':
    unittest.main()