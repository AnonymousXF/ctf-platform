import unittest
import misc

class MiscTestCase(unittest.TestCase):
    def test_generate_random_string(self):
        self.assertTrue(misc.generate_random_string())
    
    def test_generate_team_key(self):
        self.assertTrue(misc.generate_team_key())
        
    def test_generate_confirmation_key(self):
        self.assertTrue(misc.generate_confirmation_key())
        
    '''def test_get_ip(self):
        self.app = app.test_client()
        self.app.request.remote_addr = '127.0.0.1'
        self.assertTrue(misc.get_ip())'''
        
if __name__ == '__main__':
    unittest.main()