# -*- coding: utf-8 -*-
import unittest
import os,sys
import peewee
import re
import redis
import time
import random
from datetime import datetime

sys.path.append("../")
import utils
import config
from app import app
from database import *


class BasicTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		tables = [User, Team, TeamMember, UserAccess, Challenge, Vmachine, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.create_table() for i in tables]

	def tearDown(self):
		tables = [User, Team, TeamMember, UserAccess, Challenge, Vmachine, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.drop_table() for i in tables]

	def test_index(self):
		#/scoreboard/
		response = self.app.get('/', content_type = 'html/text',follow_redirects=True)
		self.assertIn('队伍积分', response.data)

	def test_databse(self):
		tester = os.path.exists("dev.db")
		self.assertTrue(tester)


class FlaskrTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		tables = [User, Team, TeamMember, UserAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.create_table() for i in tables]
		
	def tearDown(self):
		tables = [User, Team, TeamMember, UserAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.drop_table() for i in tables]

	def login(self, user_name, user_pwd):
		#Get csrf_token
		html = self.app.get('/login/', follow_redirects = True).data
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />', html)[0]
		#Post data
		data = dict(user_name = user_name,
                    user_pwd = user_pwd, 
                    _csrf_token = csrf_token)
		return self.app.post('/login/',data = data,follow_redirects = True), csrf_token

	def logout(self):
		return self.app.get('/logout/',follow_redirects = True)
	
	def register(self, user_name, user_email, user_pwd, pwd_confirmed):
		#Get csrf_token
		html = self.app.get('/register/',follow_redirects = True).data
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />', html)[0]
		#Post data
		data = dict(user_name = user_name,
					user_email = user_email,
					user_pwd = user_pwd,
					pwd_confirmed = pwd_confirmed,
					_csrf_token = csrf_token)
		return self.app.post('/register/',data = data, follow_redirects = True), csrf_token
	
	def test_login_and_logout(self):
		#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY)
		
		#Test Correct login-----/login/
		rv, csrf_token = self.login(USER_NAME,USER_PASSWORD)
		self.assertIn(b'Login successful.', rv.data)

		#Test logout -----/logout/
		rv = self.logout()
		self.assertIn(b'You have successfully logged out.',rv.data)
		
		#Test Wrong login-----/login/
		rv, csrf_token = self.login('',USER_PASSWORD)
		self.assertIn(b'Not exist!', rv.data)
		rv, csrf_token = self.login(USER_NAME,'')
		self.assertIn(b'Wrong pwd!', rv.data)
		rv, csrf_token = self.login(USER_NAME,'123456')
		self.assertIn(b'Wrong pwd!', rv.data)

	def test_register(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD = 'user', '464059291@qq.com', '123456ASD'
		LONG_NAME = 'a' * 100
		WRONG_PWD = '123456'
		WRONG_EMAIL = ['', 'qwerasdf', 'qweradsf.', 'qwerqwasdf@', 'qweradf@hustctf.org']

		#Test register-----/register/
		if config.registration == True:
			##Correct Register information
			rv, csrf_token = self.register(USER_NAME, USER_EMAIL, USER_PASSWORD, USER_PASSWORD)
			self.assertIn(b'register successfully.', rv.data)

			##Wrong Register information
			###exist user_name
			rv = self.register(USER_NAME, '1' + USER_EMAIL, USER_PASSWORD, USER_PASSWORD)
			self.assertIn(b'The name has been used!', rv[0].data)
			###too long user_name
			rv = self.register(LONG_NAME, '1' + USER_EMAIL, USER_PASSWORD, USER_PASSWORD)
			self.assertIn(b'wrong name format.', rv[0].data)
			###NULL user_name
			rv = self.register('', '1' + USER_EMAIL, USER_PASSWORD, USER_PASSWORD)
			self.assertIn(b'wrong name format.', rv[0].data)
			###exist email
			rv = self.register('_' + USER_NAME, USER_EMAIL, USER_PASSWORD, USER_PASSWORD)
			self.assertIn(b'The email has been used!', rv[0].data)
			###wrong email format
			rv = self.register('_' + USER_NAME, WRONG_EMAIL[0], USER_PASSWORD, USER_PASSWORD)
			self.assertIn(b'wrong email format.', rv[0].data)
			rv = self.register('_' + USER_NAME, WRONG_EMAIL[1], USER_PASSWORD, USER_PASSWORD)
			self.assertIn(b'wrong email format.', rv[0].data)
			rv = self.register('_' + USER_NAME, WRONG_EMAIL[2], USER_PASSWORD, USER_PASSWORD)
			self.assertIn(b'wrong email format.', rv[0].data)
			rv = self.register('_' + USER_NAME, WRONG_EMAIL[3], USER_PASSWORD, USER_PASSWORD)
			self.assertIn(b'wrong email format.', rv[0].data)
			rv = self.register('_' + USER_NAME, WRONG_EMAIL[4], USER_PASSWORD, USER_PASSWORD)
			self.assertIn(b'You are lying', rv[0].data)
			###two different input password
			rv = self.register('_'+USER_NAME, '1' + USER_EMAIL, USER_PASSWORD, USER_PASSWORD + '_')
			self.assertIn(b'Entered passwords differs', rv[0].data)
			###wrong format password
			rv = self.register('_'+USER_NAME, '1' + USER_EMAIL, WRONG_PWD, WRONG_PWD)
			self.assertIn(b'wrong pwd format.', rv[0].data)
		else:
			rv = self.app.get('/register/', follow_redirects = True)
			self.assertEqual(rv.data, b'抱歉，现在暂时无法注册。有问题请联系hustctf@163.com')

	def test_confirm_email(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY)
		rv, csrf_token = self.login(USER_NAME, USER_PASSWORD)
		CORRECT_DATA = dict(confirmation_key = EMAIL_CONFIRMATION_KEY, _csrf_token = csrf_token)
		WRONG_DATA = dict(confirmation_key = EMAIL_CONFIRMATION_KEY + 'xxx', _csrf_token = csrf_token)

		#Test confirm_email-----/confirm_email/
		##wrong confirmation_key
		rv = self.app.post('/confirm_email/',data = WRONG_DATA, follow_redirects = True)
		self.assertIn(b'wrong.', rv.data)
		##correct confirmation_key
		rv = self.app.post('/confirm_email/',data = CORRECT_DATA, follow_redirects = True)
		self.assertIn(b'confirmed!', rv.data)
	
	def test_user(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		User.create(username = 'test', password = pwhash, email = '3203155256@qq.com', email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		rv, csrf_token = self.login(USER_NAME, USER_PASSWORD)
		##correct case
		nothing_changed = dict(user_name = USER_NAME, user_email = USER_EMAIL, _csrf_token = csrf_token)
		correct_name_change = dict(user_name = USER_NAME + '_', user_email = USER_EMAIL, _csrf_token = csrf_token)
		correct_email_change = dict(user_name = USER_NAME, user_email = 'jjxf251@163.com', _csrf_token = csrf_token)
		##wrong name case
		exist_name_change = dict(user_name = 'test', user_email = USER_EMAIL, _csrf_token = csrf_token)
		long_name_change = dict(user_name = 'a' * 100, user_email = USER_EMAIL, _csrf_token = csrf_token)
		null_name_change = dict(user_name = '', user_email = USER_EMAIL, _csrf_token = csrf_token)
		##wrong email case
		exist_email_change = dict(user_name = USER_NAME, user_email = '3203155256@qq.com', _csrf_token = csrf_token)
		wrong_email_format_change = [dict(user_name = USER_NAME, user_email = '', _csrf_token = csrf_token),
									 dict(user_name = USER_NAME, user_email = 'qwerasdf', _csrf_token = csrf_token),
									 dict(user_name = USER_NAME, user_email = 'qwerasdf.', _csrf_token = csrf_token),
									 dict(user_name = USER_NAME, user_email = 'qwerasdf@', _csrf_token = csrf_token),
									 dict(user_name = USER_NAME, user_email = 'qwerasdf@hustctf.org', _csrf_token = csrf_token)
									]

		#Test user -----/user/
		##GET method
		rv = self.app.get('/user/', content_type = 'html/text',follow_redirects = True)
		self.assertIn('{},欢迎你！'.format(USER_NAME), rv.data)
		
		##POST method
		###nothing change
		rv = self.app.post('/user/', data = nothing_changed, follow_redirects = True)
		self.assertIn(b'nothing changed!',rv.data)
		###exist name change
		rv = self.app.post('/user/', data = exist_name_change, follow_redirects = True)
		self.assertIn(b'The name has been used!',rv.data)
		time.sleep(config.interval)
		###long name change
		rv = self.app.post('/user/', data = long_name_change, follow_redirects = True)
		self.assertIn(b'wrong name format.',rv.data)
		time.sleep(config.interval)
		###null name change
		rv = self.app.post('/user/', data = null_name_change, follow_redirects = True)
		self.assertIn(b'wrong name format.',rv.data)
		time.sleep(config.interval)
		###null email change
		rv = self.app.post('/user/', data = wrong_email_format_change[0], follow_redirects = True)
		self.assertIn(b'wrong email format.',rv.data)
		time.sleep(config.interval)
		###wrong email format change
		rv = self.app.post('/user/', data = wrong_email_format_change[1], follow_redirects = True)
		self.assertIn(b'wrong email format.',rv.data)
		time.sleep(config.interval)
		rv = self.app.post('/user/', data = wrong_email_format_change[2], follow_redirects = True)
		self.assertIn(b'wrong email format.',rv.data)
		time.sleep(config.interval)
		rv = self.app.post('/user/', data = wrong_email_format_change[3], follow_redirects = True)
		self.assertIn(b'wrong email format.',rv.data)
		time.sleep(config.interval)
		rv = self.app.post('/user/', data = wrong_email_format_change[4], follow_redirects = True)
		self.assertIn(b'You are lying',rv.data)
		time.sleep(config.interval)
		###exist email change
		rv = self.app.post('/user/', data = exist_email_change, follow_redirects = True)
		self.assertIn(b'The email has been used!',rv.data)
		time.sleep(config.interval)
		###correct name change
		rv = self.app.post('/user/', data = correct_name_change, follow_redirects = True)
		self.assertIn(b'save change.',rv.data)
		time.sleep(config.interval)
		###correct email change
		rv = self.app.post('/user/', data = correct_email_change, follow_redirects = True)
		self.assertIn(b'please confirme email',rv.data)

	def test_team_register(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		testUser = User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY)
		rv, csrf_token = self.login(USER_NAME, USER_PASSWORD)

		null_team_name = dict(team_name = '', affiliation = 'test affiliation', team_eligibility = True, _csrf_token = csrf_token)
		long_team_name = dict(team_name = 'a' * 100, affiliation = 'test affiliation', team_eligibility = True, _csrf_token = csrf_token)
		no_affiliation = dict(team_name = 'test', affiliation = '', team_eligibility = True, _csrf_token = csrf_token)
		exist_team_name = dict (team_name = 'test', affiliation = '', team_eligibility = True, _csrf_token = csrf_token)
		
		#Test team_register -----/team_register/
		##GET method
		###not confirmed
		rv = self.app.get('/team_register/', content_type = 'html/text', follow_redirects = True)
		self.assertIn('Please confirm your email.', rv.data)
		###confirmed
		testUser.email_confirmed = True
		testUser.save()
		rv = self.app.get('/team_register/', content_type = 'html/text', follow_redirects = True)
		self.assertIn('{}，欢迎你！'.format(USER_NAME), rv.data)
		##POST method
		###null team_name
		rv = self.app.post('/team_register/',data = null_team_name, follow_redirects = True)
		self.assertIn(b'wrong team name format!', rv.data)
		###long team_name
		rv = self.app.post('/team_register/',data = long_team_name, follow_redirects = True)
		self.assertIn(b'wrong team name format!', rv.data)
		###no affiliation
		rv = self.app.post('/team_register/',data = no_affiliation, follow_redirects = True)
		self.assertIn(b'The request has send to admin.', rv.data)
		###exist team_name
		rv = self.app.post('/team_register/',data = exist_team_name, follow_redirects = True)
		self.assertIn(b'The team name has been used.', rv.data)

	def test_team_modify(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		testUser = User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		rv, csrf_token = self.login(USER_NAME, USER_PASSWORD)

		TEAM_NAME, TEAM_AFFILIATION, TEAM_ELIGIBLE = 'testTeam', 'testAffiliation', True
		Team.create(name = TEAM_NAME + '1', affiliation = TEAM_AFFILIATION, eligible = TEAM_ELIGIBLE, team_leader = testUser)
		team = dict(team_name = TEAM_NAME, affiliation = TEAM_AFFILIATION, team_eligibility = TEAM_ELIGIBLE, _csrf_token = csrf_token)
		self.app.post('/team_register/',data = team, follow_redirects = True)
		
		nothing_change = dict(team_name = TEAM_NAME, affiliation = TEAM_AFFILIATION, team_eligibility = TEAM_ELIGIBLE, _csrf_token = csrf_token)
		exist_team_name = dict(team_name = TEAM_NAME + '1', affiliation = TEAM_AFFILIATION, team_eligibility = TEAM_ELIGIBLE, _csrf_token = csrf_token)
		null_team_name = dict(team_name = '', affiliation = TEAM_AFFILIATION, team_eligibility = TEAM_ELIGIBLE, _csrf_token = csrf_token)
		long_team_name = dict(team_name = 'a' * 100, affiliation = TEAM_AFFILIATION, team_eligibility = TEAM_ELIGIBLE, _csrf_token = csrf_token)
		correct_change = dict(team_name = '_' + TEAM_NAME, affiliation = TEAM_AFFILIATION, team_eligibility = TEAM_ELIGIBLE, _csrf_token = csrf_token)

		#Test team_modify -----/team_modify/
		##nothing change
		rv = self.app.post('/team_modify/', data = nothing_change, follow_redirects = True)
		self.assertIn(b'nothig changed!', rv.data)
		##exist team_name
		rv = self.app.post('/team_modify/', data = exist_team_name, follow_redirects = True)
		self.assertIn(b'The team name has been used.', rv.data)
		##null team_name
		rv = self.app.post('/team_modify/', data = null_team_name, follow_redirects = True)
		self.assertIn(b'wrong team name format!', rv.data)
		##long team_name
		rv = self.app.post('/team_modify/', data = long_team_name, follow_redirects = True)
		self.assertIn(b'wrong team name format!', rv.data)
		##correct change
		rv = self.app.post('/team_modify/', data = correct_change, follow_redirects = True)
		self.assertIn(b'change successfully.', rv.data)

	def test_team_join(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		testUser1 = User.create(username = USER_NAME + '1', password = pwhash, email = '1' + USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		testUser2 = User.create(username = USER_NAME + '2', password = pwhash, email = '2' + USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		
		TEAM_NAME, TEAM_AFFILIATION, TEAM_ELIGIBLE = 'testTeam', 'testAffiliation', True
		team = Team.create(name = TEAM_NAME, affiliation = TEAM_AFFILIATION, eligible = TEAM_ELIGIBLE, team_leader = testUser1)
		TeamMember.create(team = team, member = testUser1, member_confirmed = True)
		
		rv, csrf_token = self.login(USER_NAME + '2', USER_PASSWORD)
		not_exist_team = dict(team_name = 'not_exist', _csrf_token = csrf_token)
		test_team = dict(team_name = TEAM_NAME, _csrf_token = csrf_token)

		#Test team_join -----/team_join/
		##not exist team
		rv = self.app.post('/team_join/',data = not_exist_team, follow_redirects = True)
		self.assertIn(b'team name don not exist!', rv.data)
		##team has not been agreed
		rv = self.app.post('/team_join/',data = test_team, follow_redirects = True)
		self.assertIn(b'The team has not be agreed by admin.Please wait,or join another team!', rv.data)
		##team has been agreed
		team.team_confirmed = True
		team.save()
		rv = self.app.post('/team_join/',data = test_team, follow_redirects = True)
		self.assertIn(b'The request has sent to leader!', rv.data)

	def test_user_add(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		testUser1 = User.create(username = USER_NAME + '1', password = pwhash, email = '1' + USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		testUser2 = User.create(username = USER_NAME + '2', password = pwhash, email = '2' + USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		testUser3 = User.create(username = USER_NAME + '3', password = pwhash, email = '3' + USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		testUser4 = User.create(username = USER_NAME + '4', password = pwhash, email = '4' + USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		testUser5 = User.create(username = USER_NAME + '5', password = pwhash, email = '5' + USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		testUser6 = User.create(username = USER_NAME + '6', password = pwhash, email = '6' + USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		testUser7 = User.create(username = USER_NAME + '7', password = pwhash, email = '7' + USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)

		TEAM_NAME, TEAM_AFFILIATION, TEAM_ELIGIBLE = 'testTeam', 'testAffiliation', True
		team = Team.create(name = TEAM_NAME, affiliation = TEAM_AFFILIATION, eligible = TEAM_ELIGIBLE, team_leader = testUser1)
		TeamMember.create(team = team, member = testUser1, member_confirmed = True)
		TeamMember.create(team = team, member = testUser2)

		rv, csrf_token = self.login(USER_NAME + '1', USER_PASSWORD)

		#Test user_add -----/user_add/
		##only can choose one checkbox
		rv = self.app.post('/user_add/', data = dict(a2 = 'checked', a2a = 'checked', _csrf_token = csrf_token), follow_redirects = True)
		self.assertIn(b'You can only choose one!', rv.data)
		##reject request
		rv = self.app.post('/user_add/', data = dict(a2a = 'checked', _csrf_token = csrf_token), follow_redirects = True)
		self.assertIn(b'reject', rv.data)
		##accept request
		TeamMember.create(team = team, member = testUser2)
		rv = self.app.post('/user_add/', data = dict(a2 = 'checked', _csrf_token = csrf_token), follow_redirects = True)
		self.assertIn(b'agree', rv.data)
		##the number of members no more than 5
		TeamMember.create(team = team, member = testUser3, member_confirmed =True)
		TeamMember.create(team = team, member = testUser4, member_confirmed =True)
		TeamMember.create(team = team, member = testUser5, member_confirmed =True)
		TeamMember.create(team = team, member = testUser6, member_confirmed =True)
		TeamMember.create(team = team, member = testUser7)
		rv = self.app.post('/user_add/',data = dict(a7='checked', _csrf_token = csrf_token), follow_redirects=True)
		self.assertIn(b'The count of member must be less of 5',rv.data)

	def test_challenge(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		testUser = User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)

		rv, csrf_token = self.login(USER_NAME, USER_PASSWORD)

		#Test challenge -----/challenge/
		##without join a team
		rv = self.app.get('/challenges/', content_type = 'html/text', follow_redirects = True)
		self.assertIn(b'Please join a team!',rv.data)
		#join a team
		TEAM_NAME, TEAM_AFFILIATION, TEAM_ELIGIBLE = 'testTeam', 'testAffiliation', True
		team = Team.create(name = TEAM_NAME, affiliation = TEAM_AFFILIATION, eligible = TEAM_ELIGIBLE, team_leader = testUser)
		TeamMember.create(team = team, member = testUser, member_confirmed = True)
		self.logout()
		self.login(USER_NAME, USER_PASSWORD)
		rv = self.app.get('/challenges/', content_type = 'html/text', follow_redirects = True)
		self.assertIn(b'收起题目',rv.data)

	def test_challenge_submit(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		testUser = User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)

		TEAM_NAME, TEAM_AFFILIATION, TEAM_ELIGIBLE = 'testTeam', 'testAffiliation', True
		team = Team.create(name = TEAM_NAME, affiliation = TEAM_AFFILIATION, eligible = TEAM_ELIGIBLE, team_leader = testUser)
		TeamMember.create(team = team, member = testUser, member_confirmed = True)

		CHAL_NAME, CHAL_CATEGORY, CHAL_DESCRIBE, CHAL_POINTS, CHAL_FLAG, CHAL_AUTHOR = 'test', 'test', 'test', 100, 'flag', 'test'
		chal = Challenge.create(name = CHAL_NAME, category = CHAL_CATEGORY, description = CHAL_DESCRIBE, points = CHAL_POINTS, flag = CHAL_FLAG, author = CHAL_AUTHOR)
		r = redis.StrictRedis()
		r.hset("solves", chal.id, chal.solves.count())

		rv, csrf_token = self.login(USER_NAME, USER_PASSWORD)

		wrong_flag = dict(flag = CHAL_FLAG + '_', _csrf_token = csrf_token)
		correct_flag = dict(flag = CHAL_FLAG, _csrf_token = csrf_token)

		#Test challenge_submit -----/submit/<int:challenge>/
		##disabled challenge
		chal.enabled = False
		chal.save()
		rv = self.app.post('/submit/{}/'.format(chal.id), data = wrong_flag, follow_redirects = True)
		self.assertIn(b'You cannot submit a flag for a disabled problem.', rv.data)
		time.sleep(config.flag_rl * 2)
		##wrong flag
		chal.enabled = True
		chal.save()
		rv = self.app.post('/submit/{}/'.format(chal.id), data = wrong_flag, follow_redirects = True)
		self.assertIn(b'Incorrect flag.', rv.data)
		time.sleep(config.flag_rl * 2)
		##correct flag
		rv = self.app.post('/submit/{}/'.format(chal.id), data = correct_flag, follow_redirects = True)
		self.assertIn(b'Success!', rv.data)
		time.sleep(config.flag_rl * 2)
		##submit again when the flag accept
		rv = self.app.post('/submit/{}/'.format(chal.id), data = correct_flag, follow_redirects = True)
		self.assertIn(b'already solved that problem!', rv.data)
		##challenge_show_solves -----/challenges/<int:challenge>/solves/
		rv = self.app.get('/challenges/{}/solves/'.format(chal.id), content_type = 'html/text', follow_redirects = True)
		self.assertIn(b'答出了', rv.data)

	def test_ticket(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		testUser = User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)

		TEAM_NAME, TEAM_AFFILIATION, TEAM_ELIGIBLE = 'testTeam', 'testAffiliation', True

		#Test tickets
		##no login
		rv = self.app.get('/tickets/1/', follow_redirects = True)
		self.assertIn(b'Need login first.', rv.data)
		##no team
		rv, csrf_token = self.login(USER_NAME, USER_PASSWORD)
		rv = self.app.get('/tickets/1/', follow_redirects = True)
		self.assertIn(b'Please join a team!', rv.data)
		## /tickets/
		team = Team.create(name = TEAM_NAME, affiliation = TEAM_AFFILIATION, eligible = TEAM_ELIGIBLE, team_leader = testUser)
		TeamMember.create(team = team, member = testUser, member_confirmed = True)
		self.logout()
		self.login(USER_NAME, USER_PASSWORD)
		rv = self.app.get('/tickets/', follow_redirects = True)
		self.assertIn(b'你现在没有开启的tickets.', rv.data)

	def test_ticket_new(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		testUser = User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)

		TEAM_NAME, TEAM_AFFILIATION, TEAM_ELIGIBLE = 'testTeam', 'testAffiliation', True
		team = Team.create(name = TEAM_NAME, affiliation = TEAM_AFFILIATION, eligible = TEAM_ELIGIBLE, team_leader = testUser)
		TeamMember.create(team = team, member = testUser, member_confirmed = True)

		rv, csrf_token = self.login(USER_NAME, USER_PASSWORD)

		TICKET_SUMMARY, TICKET_DESCRIBE = 'ticket_summary', 'ticket_description'
		test_ticket = dict(summary = TICKET_SUMMARY, description = TICKET_DESCRIBE, _csrf_token = csrf_token)

		#Test ticket_new -----/tickets/new/
		##GET method
		rv = self.app.get('/tickets/new/', follow_redirects = True)
		self.assertIn(b'新建一个 Trouble Ticket', rv.data)   
		##POST method
		time.sleep(10)
		rv = self.app.post('/tickets/new/', data = test_ticket, follow_redirects = True)
		self.assertIn(b'Ticket #1 opened.', rv.data)
		rv = self.app.post('/tickets/new/', data = test_ticket, follow_redirects = True)
		self.assertIn(b'doing that too fast.', rv.data)
		##view ticket -----/tickets/<int:ticket>
		###exist ticket
		rv = self.app.get('/tickets/1/',follow_redirects = True)
		self.assertIn(b'Ticket #1: {}'.format(TICKET_SUMMARY), rv.data)
		###not exist ticket
		rv = self.app.get('/tickets/100/',follow_redirects=True)
		self.assertIn(b'Could not find ticket', rv.data)

	def test_ticket_comment(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		testUser = User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)

		TEAM_NAME, TEAM_AFFILIATION, TEAM_ELIGIBLE = 'testTeam', 'testAffiliation', True
		team = Team.create(name = TEAM_NAME, affiliation = TEAM_AFFILIATION, eligible = TEAM_ELIGIBLE, team_leader = testUser)
		TeamMember.create(team = team, member = testUser, member_confirmed = True)

		rv, csrf_token = self.login(USER_NAME, USER_PASSWORD)

		TICKET_SUMMARY, TICKET_DESCRIBE = 'ticket_summary', 'ticket_description'
		test_ticket = dict(summary = TICKET_SUMMARY, description = TICKET_DESCRIBE, _csrf_token = csrf_token)
		self.app.post('/tickets/new/', data = test_ticket, follow_redirects = True)
		
		null_comment = dict(comment = '', _csrf_token = csrf_token)
		add_comment = dict(comment = 'comment test', _csrf_token = csrf_token)
		close_ticket = dict(comment = '', _csrf_token = csrf_token, resolved = True)
		reopen_ticket = dict(comment = '', _csrf_token = csrf_token)

		#Test ticket_comment -----/tickets/<int:ticket>/comment/
		##not exist ticket
		time.sleep(10)
		rv = self.app.post('/tickets/100/comment/',data = dict(_csrf_token = csrf_token), follow_redirects = True)
		self.assertIn(b'Could not find ticket', rv.data)
		time.sleep(10)
		##null comment
		rv = self.app.post('/tickets/1/comment/',data = null_comment, follow_redirects = True)
		self.assertIn(b'Ticket #1: {}'.format(TICKET_SUMMARY), rv.data)
		self.assertNotIn(b'Comment added.', rv.data)
		self.assertNotIn(b'Ticket closed.', rv.data)
		self.assertNotIn(b'Ticket re-opened.', rv.data)
		time.sleep(10)
		##add comment
		rv = self.app.post('/tickets/1/comment/', data = add_comment, follow_redirects = True)
		self.assertIn(b'Comment added.', rv.data)
		time.sleep(10)
		##close ticket
		rv = self.app.post('/tickets/1/comment/', data = close_ticket, follow_redirects = True)
		self.assertIn(b'Ticket closed.', rv.data)
		time.sleep(10)
		##reopen ticket
		rv = self.app.post('/tickets/1/comment/', data = reopen_ticket, follow_redirects = True)
		self.assertIn(b'Ticket re-opened.', rv.data)
	
	def test_forget_pwd(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)

		#Test forget_pwd -----/forget_pwd/
		##GET method
		rv = self.app.get('/forget_pwd/', follow_redirects = True)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />', rv.data)[0]
		self.assertIn(b'忘记密码', rv.data)
		##POST method
		###not exist	
		not_exist = dict(user_name = USER_NAME, _csrf_token = csrf_token)
		rv = self.app.post('/forget_pwd/', data = not_exist, follow_redirects = True)
		self.assertIn(b'Not exist!', rv.data)
		###not email confirmed
		testUser = User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY)
		not_confirmed = dict(user_name = USER_NAME, _csrf_token = csrf_token)
		rv = self.app.post('/forget_pwd/', data = not_confirmed, follow_redirects = True)
		self.assertIn(b'Your email has not confirmed,you can input the confirmed code in your email', rv.data)
		###email confirmed
		testUser.email_confirmed = True
		testUser.save()
		confirmed = dict(user_name = USER_NAME, _csrf_token = csrf_token)
		rv = self.app.post('/forget_pwd/', data = confirmed, follow_redirects = True)
		self.assertIn(b'The confirmed code has been send to your email', rv.data)
	
	def test_confirm_code(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)

		rv = self.app.get('/forget_pwd/', follow_redirects = True)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />', rv.data)[0]
		
		#Test
		##not exist
		not_exist = dict(user_name1 = 'not_exist', confirm_code = '1234567890', _csrf_token = csrf_token)
		rv = self.app.post('/confirm_code/', data = not_exist, follow_redirects = True)
		self.assertIn(b'Not exist',rv.data)
		##wrong data
		wrong_data = dict(user_name1 = USER_NAME, confirm_code = '123456789', _csrf_token = csrf_token)
		rv = self.app.post('/confirm_code/', data = wrong_data, follow_redirects = True)
		self.assertIn(b'wrong',rv.data)
		##correct data
		correct_data = dict(user_name1 = USER_NAME, confirm_code = EMAIL_CONFIRMATION_KEY, _csrf_token = csrf_token)
		rv = self.app.post('/confirm_code/', data = correct_data, follow_redirects = True)
		self.assertIn(b'correct',rv.data)
	
	def test_reset_pwd(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)

		rv, csrf_token = self.login(USER_NAME, USER_PASSWORD)

		#Test reset_pwd -----/reset_pwd/
		##diffrent input
		different_input = dict(user_pwd = 'ASD123456', pwd_confirmed = '123456ASD', _csrf_token = csrf_token)
		rv = self.app.post('/reset_pwd/', data = different_input, follow_redirects = True)
		self.assertIn(b'Entered passwords differs', rv.data)
		##wrong format password
		wrong_data = dict(user_pwd = '123456', pwd_confirmed = '123456', _csrf_token = csrf_token)
		rv = self.app.post('/reset_pwd/', data = wrong_data, follow_redirects = True)
		self.assertIn(b'wrong pwd format.', rv.data)
		##correct format password
		correct_data = dict(user_pwd = 'ASD123456', pwd_confirmed = 'ASD123456', _csrf_token = csrf_token)
		rv = self.app.post('/reset_pwd/', data = correct_data, follow_redirects = True)
		self.assertIn(b'Success', rv.data)
	
	def test_dynamic_display(self):
    	#Test Case
		USER_NAME, USER_EMAIL, USER_PASSWORD, EMAIL_CONFIRMATION_KEY = 'user', '464059291@qq.com', '123456ASD', utils.misc.generate_confirmation_key()
		pwhash = utils.admin.create_password(USER_PASSWORD)
		testUser = User.create(username = USER_NAME, password = pwhash, email = USER_EMAIL, email_confirmation_key = EMAIL_CONFIRMATION_KEY, email_confirmed = True)
		
		TEAM_NAME, TEAM_AFFILIATION, TEAM_ELIGIBLE = 'testTeam', 'testAffiliation', True
		team = Team.create(name = TEAM_NAME, affiliation = TEAM_AFFILIATION, eligible = TEAM_ELIGIBLE, team_leader = testUser, team_confirmed = True)
		TeamMember.create(team = team, member = testUser, member_confirmed = True)

		chal = Challenge.create(name="Challenge Test", category="Test", description="Test", points=100, flag="Test",
								author="Test")
		r = redis.StrictRedis()
		r.hset("solves", chal.id, chal.solves.count())

		rv, csrf_token = self.login(USER_NAME, USER_PASSWORD)

		#Test dynamic_display -----/dynamic_display/
		##GET --- no nitice
		rv = self.app.get('/dynamic_display/', follow_redirects = True)
		self.assertIn(b'暂无任何通知', rv.data)
		##GET --- new a notice
		NewsItem.create(title="TestTitle", content="TestContent", time=datetime.now())
		rv = self.app.get('/dynamic_display/', follow_redirects = True)
		self.assertIn(b'TestTitle', rv.data)
		##Get --- challenge solve dynamics
		flag = dict(flag="Test", _csrf_token=csrf_token)
		self.app.post('/submit/{}/'.format(chal.id), data = flag, follow_redirects = True)
		rv = self.app.get('/dynamic_display/', follow_redirects = True)
		self.assertIn("Success", rv.data)


if __name__ == '__main__':
	unittest.main()
