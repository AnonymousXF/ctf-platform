import unittest
import os
from app import app
from database import *
import peewee
import config
import re
import api
import random
import utils
import redis
import time
from datetime import datetime

USER_NAME = 'user'
USER_EMAIL = 'jjxf251@163.com'
USER_PASSWORD = '123456ASD'
r = random.SystemRandom()
secret = "".join([r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for i in range(16)])
pwhash = utils.admin.create_password(USER_PASSWORD)

class FlaskrTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		tables = [User, Team, TeamMember, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.create_table() for i in tables]
		
	def tearDown(self):
		tables = [User, Team, TeamMember, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.drop_table() for i in tables]

	def login(self, user_name, user_pwd):
		#Get csrf_token
		html = self.app.get('/login/',follow_redirects=True).data
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
		#Post data
		data = dict(user_name = user_name, user_pwd = user_pwd, _csrf_token = csrf_token)
		return self.app.post('/login/',data = data,follow_redirects=True)

	#test /submit/<int:challenge>.json
	def test_submit_api(self):
		# create a team
		User.create(username=USER_NAME, password=pwhash, email='56565@qq.com', email_confirmed=True, email_confirmation_key='12345678956565')
		user = User.get(User.username==USER_NAME)
		team = Team.create(name='test1', affiliation='hust', eligible=True, team_leader=user, team_confirmed=True)
		TeamMember.create(team=team, member=user, member_confirmed=True)
		rv = self.login(USER_NAME,USER_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		# add challenge
		chal = Challenge.create(name="Challenge Test", category="Test", description="Test", points=100, flag="Test", author="Test")
		r = redis.StrictRedis()
		r.hset("solves", chal.id, chal.solves.count())
		# wrong flag
		data = dict(_csrf_token=csrf_token, flag='test')
		rv = self.app.post('/api/submit/1.json', data=data, follow_redirects=True)
		self.assertIn(b'Incorrect flag', rv.data)
		# submit too fast
		data = dict(_csrf_token=csrf_token, flag='test')
		rv = self.app.post('/api/submit/1.json', data=data, follow_redirects=True)
		self.assertIn(b'You\'re submitting flags too fast!', rv.data)
		# wait some time and submit correct flag
		time.sleep(3)
		data = dict(_csrf_token=csrf_token, flag='Test')
		rv = self.app.post('/api/submit/1.json', data=data, follow_redirects=True)
		self.assertIn(b'Success!', rv.data)

	# test /dismiss/<int:nid>.json
	def test_dismiss_notification(self):
		# create a team
		User.create(username=USER_NAME, password=pwhash, email='56565@qq.com', email_confirmed=True, email_confirmation_key='12345678956565')
		user = User.get(User.username==USER_NAME)
		team = Team.create(name='test1', affiliation='hust', eligible=True, team_leader=user, team_confirmed=True)
		TeamMember.create(team=team, member=user, member_confirmed=True)
		rv = self.login(USER_NAME,USER_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		# create a notification
		notification = Notification.create(team=team, notification='test /dismiss/<int:nid>.json')
		data = dict(_csrf_token=csrf_token)
		# failed
		User.create(username="test", password=pwhash, email='565635@qq.com', email_confirmed=True, email_confirmation_key='12345678956565')
		user = User.get(User.username=="test",)
		team = Team.create(name='test2', affiliation='hust', eligible=True, team_leader=user, team_confirmed=True)
		TeamMember.create(team=team, member=user, member_confirmed=True)
		notification = Notification.create(team=team, notification='test /dismiss/<int:nid>.json')
		rv = self.app.post('/api/dismiss/2.json', data=data, follow_redirects=True)
		self.assertIn(b'You cannot dismiss notifications that do not belong to you.', rv.data)
		# success
		rv = self.app.post('/api/dismiss/1.json', data=data, follow_redirects=True)
		self.assertIn(b'Success!', rv.data)

	# test /_ctftime/
	def test_ctftime_scoreboard_json(self):
		# create a team
		User.create(username=USER_NAME, password=pwhash, email='56565@qq.com', email_confirmed=True, email_confirmation_key='12345678956565')
		user = User.get(User.username==USER_NAME)
		team = Team.create(name='test1', affiliation='hust', eligible=True, team_leader=user, team_confirmed=True)
		TeamMember.create(team=team, member=user, member_confirmed=True)
		rv = self.login(USER_NAME,USER_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		# add challenge
		chal = Challenge.create(name="Challenge Test", category="Test", description="Test", points=100, flag="Test", author="Test")
		r = redis.StrictRedis()
		r.hset("solves", chal.id, chal.solves.count())
		correct_flag = dict(flag="Test", _csrf_token = csrf_token)
		rv = self.app.post('/submit/{}/'.format(chal.id), data = correct_flag, follow_redirects=True)
		self.assertIn(b'Success!',rv.data)
		# if not config.immediate_scoreboard  datetime.now() < config.competition_end
		config.immediate_scoreboard = False
		rv= self.app.get('/api/_ctftime/', follow_redirects=True)
		self.assertIn(b'unavailable', rv.data)
		# normal
		config.immediate_scoreboard = True
		rv= self.app.get('/api/_ctftime/', follow_redirects=True)
		self.assertIn(b'standings', rv.data)
		
if __name__ == '__main__':
	unittest.main()