#-*-coding:utf-8-*-
import unittest
import admin

class user:
    pw = ''
    password = ''
    
class AdminTestCase(unittest.TestCase):
    '''����admin.create_password ����Կ����hash�ǿ�'''
    def test_create_password(self):
        u = user
        u.pw = 'cat'
        u.password = admin.create_password(u.pw)
        self.assertTrue(u.password)
    
    '''����verify_password'''
    def test_verify_password(self):
        u = user
        u.pw = 'cat'
        u.password = admin.create_password(u.pw)
        self.assertTrue(admin.verify_password(u ,'cat'))
        self.assertFalse(admin.verify_password(u ,'dog'))
        
if __name__ == '__main__':
    unittest.main()