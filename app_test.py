# -*- coding: utf-8 -*-
import unittest
import os
from app import app
from database import *
import peewee
import config
import re
import time
import random
import utils

USER_NAME = 'user'
USER_EMAIL = 'jjxf251@163.com'
USER_PASSWORD = '123456ASD'
r = random.SystemRandom()
secret = "".join([r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for i in range(16)])
pwhash = utils.admin.create_password(USER_PASSWORD)

TEAM_NAMR = 'test_team'
TEAM_AFFILIATION = 'hust'
TEAM_ELIG = True

TEST_TICKET_SUMMARY = "Ticket Test"
TEST_TICKET_DESCRIBE = "For Ticket Test"
TEST_TICKET_COMMENT = "Comment Test"

config.debug = True
class BasicTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		tables = [User, Team, TeamMember, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.create_table() for i in tables]
		
	def tearDown(self):
		tables = [User, Team, TeamMember, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.drop_table() for i in tables]
	    #pass

	def test_index(self):
		#/scoreboard/
		response = self.app.get('/', content_type = 'html/text',follow_redirects=True)
		self.assertIn('计分板', response.data)

	def test_databse(self):
		tester = os.path.exists("dev.db")
		self.assertTrue(tester)

class FlaskrTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		tables = [User, Team, TeamMember, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.create_table() for i in tables]
		
	def tearDown(self):
		tables = [User, Team, TeamMember, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.drop_table() for i in tables]
	    #pass
	
	def register(self, user_name, user_email, user_pwd, pwd_confirmed):
		#Get csrf_token
		html = self.app.get('/register/',follow_redirects=True).data
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
		#Post data
		data = dict(user_name = user_name,
					user_email = user_email,
					user_pwd = user_pwd,
					pwd_confirmed = pwd_confirmed,
					_csrf_token = csrf_token)
		return self.app.post('/register/',data = data, follow_redirects = True), csrf_token
	
	#Test Register Function
	def test_register_and_confirm_email_and_update_information(self):
		if config.registration == True:
			#Correct Register information----/register/
			rv, csrf_token = self.register(USER_NAME,USER_EMAIL,USER_PASSWORD,USER_PASSWORD)
			self.assertIn(b'register successfully.',rv.data)
			#Comfirm email----/confirm_email/
			confirmation_key = User.get(User.username == USER_NAME).email_confirmation_key

			wrong_data = dict(confirmation_key = confirmation_key+'xxx', _csrf_token = csrf_token)
			correct_data = dict(confirmation_key = confirmation_key, _csrf_token = csrf_token)
			rv = self.app.post('/confirm_email/',data = wrong_data, follow_redirects=True)
			self.assertIn(b'wrong.',rv.data)
			rv = self.app.post('/confirm_email/',data = correct_data, follow_redirects=True)
			self.assertIn(b'confirmed!',rv.data)

			# update user_information 
			time.sleep(60)
			rv = self.app.post('/user/',data=dict(user_name=USER_NAME,user_email=USER_EMAIL, _csrf_token =csrf_token), follow_redirects=True)
			self.assertIn(b'nothing changed!',rv.data)
			time.sleep(3)
			long_name_data = dict(user_name = 'a'*100, user_email = USER_EMAIL, _csrf_token =csrf_token)
			null_name_data = dict(user_name = '', user_email = USER_EMAIL, _csrf_token =csrf_token)
			time.sleep(3)
			rv = self.app.post('/user/',data = long_name_data, follow_redirects=True)
			self.assertIn(b'wrong name format.',rv.data)
			time.sleep(3)
			rv = self.app.post('/user/',data = null_name_data, follow_redirects=True)
			self.assertIn(b'wrong name format.',rv.data)
			User.create(username='test', password='123456ASD', email='3333333@qq.com', email_confirmation_key='12345678956565')
			rv = self.app.post('/user/',data=dict(user_name='test',user_email=USER_EMAIL, _csrf_token =csrf_token), follow_redirects=True)
			self.assertIn(b'The name has been used!',rv.data)

			wrong_email_data1 = dict(user_name = USER_NAME, user_email = 'qwerasdf', _csrf_token =csrf_token)
			wrong_email_data2 = dict(user_name = USER_NAME, user_email = 'qwerasdf.', _csrf_token =csrf_token)
			wrong_email_data3 = dict(user_name = USER_NAME, user_email = 'qwerasdf@', _csrf_token =csrf_token)
			time.sleep(3)
			rv = self.app.post('/user/',data = wrong_email_data1, follow_redirects=True)
			self.assertIn(b'wrong email format.',rv.data)
			time.sleep(120)
			rv = self.app.post('/user/',data = wrong_email_data2, follow_redirects=True)
			self.assertIn(b'wrong email format.',rv.data)
			time.sleep(120)
			rv = self.app.post('/user/',data = wrong_email_data3, follow_redirects=True)
			self.assertIn(b'wrong email format.',rv.data)
			time.sleep(120)
			rv = self.app.post('/user/',data=dict(user_name=USER_NAME,user_email='3333333@qq.com', _csrf_token =csrf_token), follow_redirects=True)
			self.assertIn(b'The email has been used!',rv.data)

			#Wrong register information-----/register/
			#team_name = repeat or NULL or too long
			longname = 'a'*100
			rv = self.register(USER_NAME,USER_EMAIL,USER_PASSWORD,USER_PASSWORD)
			self.assertIn(b'The name has been used!',rv[0].data)
			rv = self.register('','1'+USER_EMAIL,USER_PASSWORD,USER_PASSWORD)
			self.assertIn(b'wrong name format.',rv[0].data)
			rv = self.register(longname,'3333@qq.com',USER_PASSWORD,USER_PASSWORD)
			self.assertIn(b'wrong name format.',rv[0].data)

			#repeat email or Wrong email format
			wrongEmail1 = 'qwerasdf'
			wrongEmail2 = 'qweradsf.'
			wrongEmail3 = 'qwerqwasdf@'
			wrongEmail4 = 'qweradf@tjctf.org'
			rv = self.register('2'+USER_NAME,USER_EMAIL,USER_PASSWORD,USER_PASSWORD)
			self.assertIn(b'The email has been used!',rv[0].data)
			rv = self.register('2'+USER_NAME,'',USER_PASSWORD,USER_PASSWORD)
			self.assertIn(b'wrong email format.',rv[0].data)
			rv = self.register('2'+USER_NAME,wrongEmail1,USER_PASSWORD,USER_PASSWORD)
			self.assertIn(b'wrong email format.',rv[0].data)
			rv = self.register('2'+USER_NAME,wrongEmail2,USER_PASSWORD,USER_PASSWORD)
			self.assertIn(b'wrong email format.',rv[0].data)
			rv = self.register('2'+USER_NAME,wrongEmail3,USER_PASSWORD,USER_PASSWORD)
			self.assertIn(b'wrong email format.',rv[0].data)
			rv = self.register('2'+USER_NAME,wrongEmail4,USER_PASSWORD,USER_PASSWORD)
			self.assertIn(b'You are lying',rv[0].data)

		else:
			rv = self.app.get('/register/',follow_redirects=True)
			self.assertEqual(rv.data, b'抱歉，现在暂时无法注册。有问题请联系hustctf@163.com')
	
	def login(self, user_name, user_pwd):
		#Get csrf_token
		html = self.app.get('/login/',follow_redirects=True).data
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
		#Post data
		data = dict(user_name = user_name, user_pwd = user_pwd, _csrf_token = csrf_token)
		return self.app.post('/login/',data = data,follow_redirects=True)
	
	def logout(self):
		return self.app.get('/logout/',follow_redirects = True)
	
	def test_login_and_logout(self):
		#create a user
		User.create(username=USER_NAME, password=pwhash, email=USER_EMAIL, email_confirmation_key='12345678956565')
		#Correct -----/login/
		rv = self.login(USER_NAME,USER_PASSWORD)
		self.assertIn(b'Login successful.', rv.data)
		#/logout/
		rv = self.logout()
		self.assertIn(b'You have successfully logged out.',rv.data)
		#Wrong -----/login/
		rv = self.login('',USER_PASSWORD)
		self.assertIn(b'Not exist!', rv.data)
		rv = self.login(USER_NAME,'')
		self.assertIn(b'Wrong pwd!', rv.data)
		rv = self.login(USER_NAME,'123456')
		self.assertIn(b'Wrong pwd!', rv.data)

    # test /team_register/
	def test_team_register(self):
		User.create(username=USER_NAME, password=pwhash, email=USER_EMAIL, email_confirmation_key='12345678956565')
		rv = self.login(USER_NAME,USER_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		# didn't confirm email
		data = dict(team_name = TEAM_NAMR,
					affiliation = TEAM_AFFILIATION,
					team_eligibility = TEAM_ELIG,
					_csrf_token = csrf_token)
		rv= self.app.post('/team_register/',data = data, follow_redirects = True)
		self.assertIn(b'Please confirm your email.',rv.data)
		# has confirm email
		confirmation_key = User.get(User.username == USER_NAME).email_confirmation_key
		correct_data = dict(confirmation_key = confirmation_key, _csrf_token = csrf_token)
		rv = self.app.post('/confirm_email/',data = correct_data, follow_redirects=True)
		self.assertIn(b'confirmed!',rv.data)
		rv = self.app.post('/team_register/',data = data, follow_redirects = True)
		self.assertIn(b'The request has send to admin.',rv.data)
		#unique team name
		rv = self.app.post('/team_register/',data = data, follow_redirects = True)
		self.assertIn(b'The team name has been used.',rv.data)
		#wrong team name format!
		data = dict(team_name = '',
					affiliation = TEAM_AFFILIATION,
					team_eligibility = TEAM_ELIG,
					_csrf_token = csrf_token)
		rv = self.app.post('/team_register/',data = data, follow_redirects = True)
		self.assertIn(b'wrong team name format!',rv.data)
		data = dict(team_name = 'A'*100,
					affiliation = TEAM_AFFILIATION,
					team_eligibility = TEAM_ELIG,
					_csrf_token = csrf_token)
		rv = self.app.post('/team_register/',data = data, follow_redirects = True)
		self.assertIn(b'wrong team name format!',rv.data)

	# test /team_modify/
	def test_team_modify(self):
		User.create(username=USER_NAME, password=pwhash, email=USER_EMAIL, email_confirmation_key='12345678956565')
		rv = self.login(USER_NAME,USER_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		data = dict(team_name = TEAM_NAMR,
					affiliation = TEAM_AFFILIATION,
					team_eligibility = TEAM_ELIG,
					_csrf_token = csrf_token)
		confirmation_key = User.get(User.username == USER_NAME).email_confirmation_key
		correct_data = dict(confirmation_key = confirmation_key, _csrf_token = csrf_token)
		self.app.post('/confirm_email/',data = correct_data, follow_redirects=True)
		self.app.post('/team_register/',data = data, follow_redirects = True)
		rv = self.app.post('/team_modify/', data=data, follow_redirects = True)
		self.assertIn(b'nothig changed!',rv.data)
		rv = self.app.post('/team_modify/', data=data, follow_redirects = True)
		self.assertIn(b'nothig changed!',rv.data)
		# unique team name
		User.create(username='nana', password=pwhash, email='56565@qq.com', email_confirmed=True, email_confirmation_key='12345678956565')
		user = User.get(User.username=='nana')
		Team.create(name='test1', affiliation='hust', eligible=True, team_leader=user)
		data = dict(team_name = 'test1',
					affiliation = TEAM_AFFILIATION,
					team_eligibility = TEAM_ELIG,
					_csrf_token = csrf_token)
		rv = self.app.post('/team_modify/',data = data, follow_redirects = True)
		self.assertIn(b'The team name has been used.',rv.data)
		#wrong team name format!
		data = dict(team_name = '',
					affiliation = TEAM_AFFILIATION,
					team_eligibility = TEAM_ELIG,
					_csrf_token = csrf_token)
		rv = self.app.post('/team_modify/',data = data, follow_redirects = True)
		self.assertIn(b'wrong team name format!',rv.data)
		data = dict(team_name = 'A'*100,
					affiliation = TEAM_AFFILIATION,
					team_eligibility = TEAM_ELIG,
					_csrf_token = csrf_token)
		rv = self.app.post('/team_modify/',data = data, follow_redirects = True)
		self.assertIn(b'wrong team name format!',rv.data)
		# correct change
		data = dict(team_name = 'test2',
					affiliation = TEAM_AFFILIATION,
					team_eligibility = TEAM_ELIG,
					_csrf_token = csrf_token)
		rv = self.app.post('/team_modify/',data = data, follow_redirects = True)
		self.assertIn(b'change successfully.',rv.data)

	# /team_join/ /user_add/
	def test_team_join_user_add(self):
		#create a team
		User.create(username='nana', password=pwhash, email='56565@qq.com', email_confirmed=True, email_confirmation_key='12345678956565')
		user = User.get(User.username=='nana')
		team = Team.create(name='test1', affiliation='hust', eligible=True, team_leader=user)
		TeamMember.create(team=team, member=user, member_confirmed=True)
		#create another user to join team
		User.create(username=USER_NAME, password=pwhash, email=USER_EMAIL, email_confirmation_key='12345678956565')
		rv = self.login(USER_NAME,USER_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		data = dict(team_name = TEAM_NAMR,
					affiliation = TEAM_AFFILIATION,
					team_eligibility = TEAM_ELIG,
					_csrf_token = csrf_token)
		confirmation_key = User.get(User.username == USER_NAME).email_confirmation_key
		correct_data = dict(confirmation_key = confirmation_key, _csrf_token = csrf_token)
		self.app.post('/confirm_email/',data = correct_data, follow_redirects=True)
		# join team
		# team name don not exist!
		rv = self.app.post('/team_join/',data = dict(team_name='test2', _csrf_token = csrf_token), follow_redirects=True)
		self.assertIn(b'team name don not exist!',rv.data)
		#The team has not be agreed by admin.Please wait,or join another team!
		rv = self.app.post('/team_join/',data = dict(team_name='test1', _csrf_token = csrf_token), follow_redirects=True)
		self.assertIn(b'The team has not be agreed by admin.Please wait,or join another team!',rv.data)
		team.team_confirmed=True
		team.save()
		rv = self.app.post('/team_join/',data = dict(team_name='test1', _csrf_token = csrf_token), follow_redirects=True)
		self.assertIn(b'The request has sent to leader!',rv.data)
		self.logout()
		# team leader login
		rv = self.login('nana',USER_PASSWORD)
		# accept
		rv = self.app.post('/user_add/',data = dict(user='checked', _csrf_token = csrf_token), follow_redirects=True)
		self.assertIn(b'agree',rv.data)

 	def test_challenge_without_join_team_and_with_join_team(self):
		User.create(username=USER_NAME, password=pwhash, email='56565@qq.com', email_confirmed=True, email_confirmation_key='12345678956565')
		rv = self.login(USER_NAME,USER_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		# before join team
		rv = self.app.get('/challenges/',data=dict(_csrf_token=csrf_token),follow_redirects=True)
 		self.assertIn(b'Please join a team!',rv.data)
 		self.logout()
 		# join a team
		user = User.get(User.username==USER_NAME)
		team = Team.create(name='test1', affiliation='hust', eligible=True, team_leader=user, team_confirmed=True)
		TeamMember.create(team=team, member=user, member_confirmed=True)
		rv = self.login(USER_NAME,USER_PASSWORD)
		rv = self.app.get('/challenges/',data=dict(_csrf_token=csrf_token),follow_redirects=True)
 		self.assertIn(b'折叠题目',rv.data)

	def test_challenge_submit(self):
		#Create a test challenge
		chal = Challenge.create(name="Challenge Test", category="Test", description="Test", points=100, flag="Test", author="Test")
		# join a team
		User.create(username=USER_NAME, password=pwhash, email='56565@qq.com', email_confirmed=True, email_confirmation_key='12345678956565')
		user = User.get(User.username==USER_NAME)
		team = Team.create(name='test1', affiliation='hust', eligible=True, team_leader=user, team_confirmed=True)
		TeamMember.create(team=team, member=user, member_confirmed=True)
		rv = self.login(USER_NAME,USER_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		#submit flag-----/submit/<int:challenge>/
		wrong_flag = dict(flag="wrong", _csrf_token = csrf_token)
		correct_flag = dict(flag="Test", _csrf_token = csrf_token)
		rv = self.app.post('/submit/{}/'.format(chal.id), data = wrong_flag, follow_redirects=True)
		self.assertIn(b'Incorrect flag.',rv.data)
		time.sleep(30)
		rv = self.app.post('/submit/{}/'.format(chal.id), data = correct_flag, follow_redirects=True)
		self.assertIn(b'Success!',rv.data)
		#challenge_show_solves-----/challenges/<int:challenge>/solves/
		rv = self.app.get('/challenges/{}/solves/'.format(chal.id), data=dict(_csrf_token=csrf_token),follow_redirects=True)
		self.assertIn(b'答出了',rv.data)

	def test_ticket(self):
		# join a team
		User.create(username=USER_NAME, password=pwhash, email='56565@qq.com', email_confirmed=True, email_confirmation_key='12345678956565')
		user = User.get(User.username==USER_NAME)
		team = Team.create(name='test1', affiliation='hust', eligible=True, team_leader=user, team_confirmed=True)
		TeamMember.create(team=team, member=user, member_confirmed=True)
		rv = self.login(USER_NAME,USER_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		#create a trouble ticket-------/tickets/new/
		#GET
		rv = self.app.get('/tickets/new/',follow_redirects=True)
		self.assertIn(b'新建一个 Trouble Ticket',rv.data)   
		#POST
		ticket = dict(summary=TEST_TICKET_SUMMARY,description=TEST_TICKET_DESCRIBE, _csrf_token=csrf_token)
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
		rv = self.app.post('/tickets/123/comment/',data=dict(_csrf_token=csrf_token),follow_redirects=True)
		self.assertIn(b'Could not find ticket #123.',rv.data)
		#comment is null
		time.sleep(30)
		comment = ''
		rv = self.app.post('/tickets/1/comment/',data=dict(comment=comment,_csrf_token=csrf_token),follow_redirects=True)
		self.assertIn(b'Ticket #1: {}'.format(TEST_TICKET_SUMMARY),rv.data)
		self.assertNotIn(b'Comment added.',rv.data)
		self.assertNotIn(b'Ticket closed.',rv.data)
		self.assertNotIn(b'Ticket re-opened.',rv.data)
		#add comment
		time.sleep(30)
		rv = self.app.post('/tickets/1/comment/',data=dict(comment=TEST_TICKET_COMMENT,_csrf_token=csrf_token),follow_redirects=True)
		self.assertIn(b'Comment added.',rv.data)
		#close ticket
		time.sleep(30)
		rv = self.app.post('/tickets/1/comment/',data=dict(comment=comment,_csrf_token=csrf_token,resolved=True),follow_redirects=True)
		self.assertIn(b'Ticket closed.',rv.data)
		#ticket re-opened
		time.sleep(30)
		rv = self.app.post('/tickets/1/comment/',data=dict(comment=comment,_csrf_token=csrf_token),follow_redirects=True)
		self.assertIn(b'Ticket re-opened.',rv.data)

if __name__ == '__main__':
	unittest.main()
