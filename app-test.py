import unittest
import os
from app import app
from database import *
import peewee
import config
import re
import time

TEST_NAME = 'unittest'
TEST_EMAIL = 'jjxf251@163.com'
TEST_AFFILIATION = 'unittest'
TEST_ELIG = True

TEST_TICKET_SUMMARY = "Ticket Test"
TEST_TICKET_DESCRIBE = "For Ticket Test"
TEST_TICKET_COMMENT = "Comment Test"
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
		#/scoreboard/
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
	def test_register_and_confirm_email_and_update_information(self):
		if config.registration == True:
			#Correct Register information----/register/
			rv, csrf_token = self.register(TEST_NAME,TEST_EMAIL,TEST_AFFILIATION,TEST_ELIG)
			self.assertIn(b'Team created.',rv.data)
			#Comfirm email----/confirm_email/
			teamkey = re.findall(r'<span class="card-title">Team key: <code>(.*)</code></span>',rv.data)[0]
			confirmation_key = Team.get(Team.key == teamkey).email_confirmation_key

			wrong_data = dict(confirmation_key = confirmation_key+'xxx', _csrf_token = csrf_token)
			correct_data = dict(confirmation_key = confirmation_key, _csrf_token = csrf_token)
			rv = self.app.post('/confirm_email/',data = wrong_data, follow_redirects=True)
			self.assertIn(b'Incorrect confirmation key.',rv.data)
			rv = self.app.post('/confirm_email/',data = correct_data, follow_redirects=True)
			self.assertIn(b'Email confirmed!',rv.data)

			#update information-----/team/
			long_name_data = dict(team_name = 'a'*100, team_email = TEST_EMAIL, affiliation = TEST_AFFILIATION, team_eligibility = TEST_ELIG, _csrf_token =csrf_token)
			null_name_data = dict(team_name = '', team_email = TEST_EMAIL, affiliation = TEST_AFFILIATION, team_eligibility = TEST_ELIG, _csrf_token =csrf_token)
			time.sleep(120)
			rv = self.app.post('/team/',data = long_name_data, follow_redirects=True)
			self.assertIn(b'You must have a team name!',rv.data)
			time.sleep(120)
			rv = self.app.post('/team/',data = null_name_data, follow_redirects=True)
			self.assertIn(b'You must have a team name!',rv.data)
			
			wrong_email_data1 = dict(team_name = TEST_NAME, team_email = 'qwerasdf', affiliation = TEST_AFFILIATION, team_eligibility = TEST_ELIG, _csrf_token =csrf_token)
			wrong_email_data2 = dict(team_name = TEST_NAME, team_email = 'qwerasdf.', affiliation = TEST_AFFILIATION, team_eligibility = TEST_ELIG, _csrf_token =csrf_token)
			wrong_email_data3 = dict(team_name = TEST_NAME, team_email = 'qwerasdf@', affiliation = TEST_AFFILIATION, team_eligibility = TEST_ELIG, _csrf_token =csrf_token)
			time.sleep(120)
			rv = self.app.post('/team/',data = wrong_email_data1, follow_redirects=True)
			self.assertIn(b'You must have a valid team email!',rv.data)
			time.sleep(120)
			rv = self.app.post('/team/',data = wrong_email_data2, follow_redirects=True)
			self.assertIn(b'You must have a valid team email!',rv.data)
			time.sleep(120)
			rv = self.app.post('/team/',data = wrong_email_data3, follow_redirects=True)
			self.assertIn(b'You must have a valid team email!',rv.data)
			
			correct_name_data = dict(team_name = TEST_NAME, team_email = TEST_EMAIL, affiliation = TEST_AFFILIATION, team_eligibility = TEST_ELIG, _csrf_token =csrf_token)
			time.sleep(120)
			rv = self.app.post('/team/',data = correct_name_data, follow_redirects=True)
			self.assertIn(b'Changes saved.',rv.data)
			time.sleep(120)
			correct_email_data = dict(team_name = TEST_NAME, team_email = '464059291@qq.com', affiliation = TEST_AFFILIATION, team_eligibility = TEST_ELIG, _csrf_token =csrf_token)
			rv = self.app.post('/team/',data = correct_email_data, follow_redirects=True)
			self.assertIn(b'Changes saved. Please check your email for a new confirmation key.',rv.data)
			

			#Wrong register information-----/register/
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
		
		#Correct teamkey-----/login/
		rv = self.login(teamkey)
		self.assertIn(b'Login successful.', rv.data)
		
		#/logout/
		rv = self.logout()
		self.assertIn(b'You have successfully logged out.',rv.data)
		
		#Wrong teamkey-----/login/
		rv = self.login('')
		self.assertIn(b'Couldn not find your team. Check your team key.', rv.data)
		rv = self.login(teamkey+'xxxx')
		self.assertIn(b'Couldn not find your team. Check your team key.', rv.data)

	def test_challenge_without_email_confirm_and_with_email_confirm(self):
		#register a team
		html = self.register(TEST_NAME,TEST_EMAIL,TEST_AFFILIATION,TEST_ELIG)
		teamkey = re.findall(r'<span class="card-title">Team key: <code>(.*)</code></span>',html[0].data)[0]
		
		#without email comfirm-----/challenges/
		rv = self.app.get('/challenges/',data=dict(_csrf_token=html[1]),follow_redirects=True)
		self.assertIn(b'Please confirm your email in order to access that page.',rv.data)
		
		#with email comfirm------/challenges/
		confirmation_key = Team.get(Team.key == teamkey).email_confirmation_key
		data = dict(confirmation_key = confirmation_key, _csrf_token = html[1])
		self.app.post('/confirm_email/',data = data, follow_redirects=True)
		rv = self.app.get('/challenges/',data=dict(_csrf_token=html[1]),follow_redirects=True)
		self.assertNotIn(b'Please confirm your email in order to access that page.',rv.data)

	def test_challenge_submit(self):
		#Create a test challenge
		chal = Challenge.create(name="Challenge Test", category="Test", description="Test", points=100, flag="Test", author="Test")
		#register a team
		html = self.register(TEST_NAME,TEST_EMAIL,TEST_AFFILIATION,TEST_ELIG)
		teamkey = re.findall(r'<span class="card-title">Team key: <code>(.*)</code></span>',html[0].data)[0]
		confirmation_key = Team.get(Team.key == teamkey).email_confirmation_key
		data = dict(confirmation_key = confirmation_key, _csrf_token = html[1])
		self.app.post('/confirm_email/',data = data, follow_redirects=True)
		
		#submit flag-----/submit/<int:challenge>/
		wrong_flag = dict(flag="wrong", _csrf_token = html[1])
		correct_flag = dict(flag="Test", _csrf_token = html[1])
		rv = self.app.post('/submit/{}/'.format(chal.id), data = wrong_flag, follow_redirects=True)
		self.assertIn(b'Incorrect flag.',rv.data)
		time.sleep(30)
		rv = self.app.post('/submit/{}/'.format(chal.id), data = correct_flag, follow_redirects=True)
		self.assertIn(b'Success!',rv.data)
		#challenge_show_solves-----/challenges/<int:challenge>/solves/
		rv = self.app.get('/challenges/{}/solves/'.format(chal.id), data=dict(_csrf_token=html[1]),follow_redirects=True)
		self.assertIn(b'<td>{}</td>'.format(TEST_NAME),rv.data)

	def test_ticket(self):
		#register a team
		html = self.register(TEST_NAME,TEST_EMAIL,TEST_AFFILIATION,TEST_ELIG)
		teamkey = re.findall(r'<span class="card-title">Team key: <code>(.*)</code></span>',html[0].data)[0]
		confirmation_key = Team.get(Team.key == teamkey).email_confirmation_key
		data = dict(confirmation_key = confirmation_key, _csrf_token = html[1])
		self.app.post('/confirm_email/',data = data, follow_redirects=True)

		#create a trouble ticket-------/tickets/new/
		#GET
		rv = self.app.get('/tickets/new/',follow_redirects=True)
		self.assertIn(b'Open a Trouble Ticket',rv.data)
		#POST
		ticket = dict(summary=TEST_TICKET_SUMMARY,description=TEST_TICKET_DESCRIBE, _csrf_token=html[1])
		rv = self.app.post('/tickets/new/', data=ticket, follow_redirects=True)
		self.assertIn(b'Ticket #1 opened.',rv.data)

		#-----/tickets/
		rv = self.app.get('/tickets/', follow_redirects=True)
		self.assertIn(b'#1 {}'.format(TEST_TICKET_SUMMARY),rv.data)

		#-----/tickets/<int:ticket>/
		#not exsisting ticket
		rv = self.app.get('/tickets/123/',follow_redirects=True)
		self.assertIn(b'Could not find ticket #123.',rv.data)
		#exsisting ticket
		rv = self.app.get('/tickets/1/',follow_redirects=True)
		self.assertIn(b'Ticket #1: {}'.format(TEST_TICKET_SUMMARY),rv.data)

		#-----/tickets/<int:ticket>/comment/
		#not exsisting ticket
		time.sleep(30)
		rv = self.app.post('/tickets/123/comment/',data=dict(_csrf_token=html[1]),follow_redirects=True)
		self.assertIn(b'Could not find ticket #123.',rv.data)
		
		#comment is null
		time.sleep(30)
		comment = ''
		rv = self.app.post('/tickets/1/comment/',data=dict(comment=comment,_csrf_token=html[1]),follow_redirects=True)
		self.assertIn(b'Ticket #1: {}'.format(TEST_TICKET_SUMMARY),rv.data)
		self.assertNotIn(b'Comment added.',rv.data)
		self.assertNotIn(b'Ticket closed.',rv.data)
		self.assertNotIn(b'Ticket re-opened.',rv.data)
		
		#add comment
		time.sleep(30)
		rv = self.app.post('/tickets/1/comment/',data=dict(comment=TEST_TICKET_COMMENT,_csrf_token=html[1]),follow_redirects=True)
		self.assertIn(b'Comment added.',rv.data)

		#close ticket
		time.sleep(30)
		rv = self.app.post('/tickets/1/comment/',data=dict(comment=comment,_csrf_token=html[1],resolved=True),follow_redirects=True)
		self.assertIn(b'Ticket closed.',rv.data)

		#ticket re-opened
		time.sleep(30)
		rv = self.app.post('/tickets/1/comment/',data=dict(comment=comment,_csrf_token=html[1]),follow_redirects=True)
		self.assertIn(b'Ticket re-opened.',rv.data)

if __name__ == '__main__':
	unittest.main()