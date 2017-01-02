# -*- coding:utf-8 -*- 
import unittest
from flask import json
from flask import Flask, render_template, session, redirect, url_for, request, g, flash, jsonify
app = Flask(__name__)
import os
import re

from app import app
from database import Team, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, ScoreAdjustment, TroubleTicket, TicketComment, Notification, db
from datetime import datetime
from peewee import fn

from utils import decorators, flag, cache, misc, captcha, sendemail
import utils.scoreboard

import config
import utils
import redis
import requests
import socket


class BasicTestCase(unittest.TestCase):

    def test_index(self):
        """inital test. ensure flask was set up correctly"""
        #app.config['TESTING'] = True
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 302)
        #redirect的返回状态码是302，render_template的返回状态码是200

    def test_database(self):
        """inital test. ensure that the database exists"""
        tester = os.path.exists("dev.db")
        self.assertTrue(tester)
        
class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a blank temp database before each test"""
        app.config['TESTING'] = True
        self.app = app.test_client()

    #def tearDown(self):
    #    os.unlink('dev.db')
        
    def login(self, team_key):
        """Login helper function"""
        html = self.app.get('/login/', follow_redirects=True).data
        csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="{.*}" />',html)
        return self.app.post('/login', data=dict(
            team_key=team_key, _csrf_token=csrf_token
        ), follow_redirects=True)

    def logout(self):
        """Logout helper function"""
        return self.app.get('/logout', follow_redirects=True)
        
    def test_chat(self):
        """inital test. ensure flask was set up correctly"""
        #app.config['TESTING'] = True
        tester = app.test_client(self)
        response = tester.get('/chat/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        #redirect的返回状态码是302，render_template的返回状态码是200
    
    def test_login_logout(self):
        """Test login and logout using helper functions"""
        rv = self.login('tjctf_87rfu0nwhtk0a5nc6tnzx5z8eoyr9hxu')
        self.assertIn(b'Login successful.', rv.data)
        rv = self.logout()
        self.assertIn(b"You have successfully logged out.", rv.data)
        rv = self.login('')
        self.assertIn(b'Could not find your team. Check your team key.', rv.data)
        rv = self.login('asfdsfsadfsdfsdfgdfght')
        self.assertIn(b'Could not find your team. Check your team key.', rv.data)
    
    def register(self, team_name, team_email, team_elig, affiliation):
        return self.app.post('/register/', data=dict(
            team_name=team_name, team_email=team_email, team_elig=team_elig, affiliation=affiliation
        ), follow_redirects=True)
        
    def test_register(self):
        #rv = self.register('test','358693294@qq.com',True,'hust')
        #self.assertIn(b'Team created.',rv.data)  #正常注册
        rv = self.register('','358693294@qq.com',True,'hust')
        self.assertIn(b'You must have a team name!',rv.data)   #用户名为空
        rv = self.register('111111111111111111111111111111111111111111111111111111\
        1111111111111111111111111111111111111111111111111111111111111111111111','358693294@qq.com',True,'hust')  
        self.assertIn(b'You must have a team name!',rv.data)    #用户名过长
        rv = self.register('test','358693294@qqcom',True,'hust')
        self.assertIn(b'You must have a valid team email!',rv.data)
        rv = self.register('test','',True,'hust')
        self.assertIn(b'You must have a valid team email!',rv.data)
        rv = self.register('test','358693294qq.com',True,'hust')
        self.assertIn(b'You must have a valid team email!',rv.data)
        rv = self.register('test','358693294qqcom',True,'hust')
        self.assertIn(b'You must have a valid team email!',rv.data)     #邮箱格式不正确
        rv = self.register('test','358693294@qq.com',True,'')
        self.assertIn(b'No affiliation',rv.data)
        rv = self.register('test','358693294@qq.com',True,'11111111111111111111111111111111111111111111111111111\
        11111111111111111111111111111111111111111111111111111111111111111111111111111111111')
        self.assertIn(b'No affiliation',rv.data)     #affiliation不正确
        
    def test_scoreboard(self):
        rv = self.app.get('/scoreboard/')
        self.assertNotEqual(b'No scoreboard data available. Please contact an organizer.',rv.data)
    
    
if __name__ == '__main__':
    unittest.main()