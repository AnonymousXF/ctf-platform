import os
from app import app
#from flask import json
import unittest
import tempfile
import database

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, database.db = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
        
    def test_root(self):
        rv = self.app.get('/')
        assert 'No entries here so far' in rv.data

if __name__ == '__main__':
    unittest.main()