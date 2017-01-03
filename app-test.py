import unittest
import os
from app import app
from database import *
import peewee
import config
import re

TEST_NAME = 'unittest'
TEST_EMAIL = '464059291@qq.com'
TEST_AFFILIATION = 'unittest'
TEST_ELIG = True


class BasicTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		tables = [Team, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.create_table() for i in tables]

	def tearDown(self):
		tables = [Team, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.drop_table() for i in tables]
	    #pass

	def test_index(self):
		response = self.app.get('/', content_type = 'html/text',follow_redirects=True)
		self.assertIn('Score progression', response.data)

	def test_databse(self):
		tester = os.path.exists("dev.db")
		self.assertTrue(tester)

class FlaskrTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		tables = [Team, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.create_table() for i in tables]

	def tearDown(self):
		tables = [Team, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.drop_table() for i in tables]
	    #pass
	
	def register(self, team_name, team_email, affiliation, team_eligibility):
		#Get csrf_token
		html = self.app.get('/register/',follow_redirects=True).data
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
		#Post data
		data = dict(team_name = team_name,
					team_email = team_email,
					affiliation = affiliation,
					team_eligibility = team_eligibility,
					_csrf_token = csrf_token)
		return self.app.post('/register/',data = data, follow_redirects = True), csrf_token

	#Test Register Function
	def test_register_and_confirm_email(self):
		if config.registration == True:
			#Correct Register information
			rv, csrf_token = self.register(TEST_NAME,TEST_EMAIL,TEST_AFFILIATION,TEST_ELIG)
			self.assertIn(b'Team created.',rv.data)
			#Comfirm email
			teamkey = re.findall(r'<span class="card-title">Team key: <code>(.*)</code></span>',rv.data)[0]
			confirmation_key = Team.get(Team.key == teamkey).email_confirmation_key

			wrong_data = dict(confirmation_key = confirmation_key+'xxx', _csrf_token = csrf_token)
			correct_data = dict(confirmation_key = confirmation_key, _csrf_token = csrf_token)
			rv = self.app.post('/confirm_email/',data = wrong_data, follow_redirects=True)
			self.assertIn(b'Incorrect confirmation key.',rv.data)
			rv = self.app.post('/confirm_email/',data = correct_data, follow_redirects=True)
			self.assertIn(b'Email confirmed!',rv.data)

			#Wrong register information
			#team_name = NULL or too long
			longname = 'a'*100
			rv = self.register('',TEST_EMAIL,TEST_AFFILIATION,TEST_ELIG)
			self.assertIn(b'You must have a team name!',rv[0].data)
			rv = self.register(longname,TEST_EMAIL,TEST_AFFILIATION,TEST_ELIG)
			self.assertIn(b'You must have a team name!',rv[0].data)

			#Wrong email format
			wrongEmail1 = 'qwerasdf'
			wrongEmail2 = 'qweradsf.'
			wrongEmail3 = 'qwerqwasdf@'
			wrongEmail4 = 'qweradf@tjctf.org'
			rv = self.register(TEST_NAME,'',TEST_AFFILIATION,TEST_ELIG)
			self.assertIn(b'You must have a valid team email!',rv[0].data)
			rv = self.register(TEST_NAME,wrongEmail1,TEST_AFFILIATION,TEST_ELIG)
			self.assertIn(b'You must have a valid team email!',rv[0].data)
			rv = self.register(TEST_NAME,wrongEmail2,TEST_AFFILIATION,TEST_ELIG)
			self.assertIn(b'You must have a valid team email!',rv[0].data)
			rv = self.register(TEST_NAME,wrongEmail3,TEST_AFFILIATION,TEST_ELIG)
			self.assertIn(b'You must have a valid team email!',rv[0].data)
			rv = self.register(TEST_NAME,wrongEmail4,TEST_AFFILIATION,TEST_ELIG)
			self.assertIn(b'You are lying',rv[0].data)

		else:
			rv = self.app.get('/register/',follow_redirects=True)
			self.assertEqual(rv.data, b'Registration is currently disabled. Email ctf@tjhsst.edu to create an account.')

	def login(self, team_key):
		#Get csrf_token
		html = self.app.get('/login/',follow_redirects=True).data
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
		#Post data
		data = dict(team_key = team_key, _csrf_token = csrf_token)
		return self.app.post('/login/',data = data,follow_redirects=True)
	
	def logout(self):
		return self.app.get('/logout/',follow_redirects = True)
	
	def test_login_and_logout(self):
		#register a team
		html = self.register(TEST_NAME,TEST_EMAIL,TEST_AFFILIATION,TEST_ELIG)
		teamkey = re.findall(r'<span class="card-title">Team key: <code>(.*)</code></span>',html[0].data)[0]
		#Correct teamkey
		rv = self.login(teamkey)
		self.assertIn(b'Login successful.', rv.data)
		rv = self.logout()
		self.assertIn(b'You have successfully logged out.',rv.data)
		#Wrong teamkey
		rv = self.login('')
		self.assertIn(b'Couldn not find your team. Check your team key.', rv.data)
		rv = self.login(teamkey+'xxxx')
		self.assertIn(b'Couldn not find your team. Check your team key.', rv.data)
	
if __name__ == '__main__':
	unittest.main()