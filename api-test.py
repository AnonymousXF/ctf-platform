import unittest
import os
from app import app
from database import *
import peewee
import config
import re
import api
import time
from datetime import datetime

class FlaskrTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		os.system('python ctftool create-tables')
		
	def tearDown(self):
		tables = [Team, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.drop_table() for i in tables]

	def login(self, team_key):
		#Get csrf_token
		html = self.app.get('/login/', follow_redirects=True).data
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
		#Post data
		data = dict(team_key = team_key, _csrf_token = csrf_token)
		return self.app.post('/login/',data = data,follow_redirects=True)

	#test /submit/<int:challenge>.json
	def test_submit_api(self):
		# create a team
		team = Team.create(name='test_team', email='358693294@qq.com', eligible=True, affiliation='Hust', key='tjctf_87rfu0nwhtk0a5nc6tnzx5z8eoyr9hxu',
                            email_confirmation_key='6b654twftg4vjzpl8zzpw6y0g5ilh08ti2ytczo323ajmua7', email_confirmed=True)
		rv = self.login('tjctf_87rfu0nwhtk0a5nc6tnzx5z8eoyr9hxu')
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		self.assertIn(b'Login successful.', rv.data)
		# add challenge
		os.system('python ctftool add-challenge problem.yml')
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
		data = dict(_csrf_token=csrf_token, flag='flag{whatever}')
		rv = self.app.post('/api/submit/1.json', data=data, follow_redirects=True)
		self.assertIn(b'Success!', rv.data)

	# test /dismiss/<int:nid>.json
	def test_dismiss_notification(self):
		# create a team
		team = Team.create(name='test_team', email='358693294@qq.com', eligible=True, affiliation='Hust', key='tjctf_87rfu0nwhtk0a5nc6tnzx5z8eoyr9hxu',
                            email_confirmation_key='6b654twftg4vjzpl8zzpw6y0g5ilh08ti2ytczo323ajmua7', email_confirmed=True)
		rv = self.login('tjctf_87rfu0nwhtk0a5nc6tnzx5z8eoyr9hxu')
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		self.assertIn(b'Login successful.', rv.data)
		# create a notification
		notification = Notification.create(team=team, notification='test /dismiss/<int:nid>.json')
		data = dict(_csrf_token=csrf_token)
		rv = self.app.post('/api/dismiss/1.json', data=data, follow_redirects=True)
		self.assertIn(b'Success!', rv.data)

	# test /_ctftime/
	def test_ctftime_scoreboard_json(self):
		# if not config.immediate_scoreboard  datetime.now() < config.competition_end
		config.immediate_scoreboard = False
		rv= self.app.get('/api/_ctftime/', follow_redirects=True)
		self.assertIn(b'unavailable', rv.data)
		# normal
		config.immediate_scoreboard = True
		rv= self.app.get('/api/_ctftime/', follow_redirects=True)
		print(rv.data)
		self.assertIn(b'standings', rv.data)
		
if __name__ == '__main__':
	unittest.main()